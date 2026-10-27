import threading
import time
from typing import Optional

from configuration.config import AgentConfig
from spool.db import LocalSpool
from hashing.hasher import FileHasher
from watcher.engine import FilesystemWatcher
from baseline.scanner import BaselineScanner
from auditing.collector import WindowsAuditCollector
from transport.client import TransportClient
from diagnostics.health import HostDiagnostics



class FIMAgentService:
    def __init__(self, config: AgentConfig = None):
        self.config = config or AgentConfig()
        self.spool = LocalSpool()
        self.hasher = FileHasher(max_size_mb=self.config.max_file_size_mb)
        self.watcher = FilesystemWatcher(self.spool, self.hasher, self.config.exclusions)
        self.scanner = BaselineScanner(self.spool, self.hasher)
        self.auditor = WindowsAuditCollector(self.spool)
        self.transport = TransportClient(self.config, self.spool)
        self.diagnostics = HostDiagnostics(self.spool)

        self.is_running = False
        self._threads = []

    def start(self):
        print(f"[*] Starting FIM Enterprise Windows Agent on {self.config.hostname}...")
        self.is_running = True

        # Fetch remote configuration if enrolled
        if self.config.is_enrolled():
            remote_config = self.transport.fetch_config()
            if remote_config:
                self.config.monitored_paths = [p["path"] for p in remote_config.get("monitored_paths", [])]
                self.config.exclusions = remote_config.get("exclusions", [])
                self.config.save()

        # Fallback default path if none configured
        if not self.config.monitored_paths:
            test_dir = "data/watched_test"
            self.config.monitored_paths = [test_dir]
            self.config.save()

        # Start filesystem watcher
        for p in self.config.monitored_paths:
            self.watcher.add_watch(p, recursive=True)
            print(f"[+] Watching directory: {p}")
        self.watcher.start()

        # Start background transport worker thread
        transport_thread = threading.Thread(target=self._transport_loop, daemon=True, name="TransportWorker")
        transport_thread.start()
        self._threads.append(transport_thread)

        # Start background heartbeat worker thread
        heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True, name="HeartbeatWorker")
        heartbeat_thread.start()
        self._threads.append(heartbeat_thread)

        # Start audit collector thread
        audit_thread = threading.Thread(target=self._audit_loop, daemon=True, name="AuditCollector")
        audit_thread.start()
        self._threads.append(audit_thread)

        # Enqueue agent_started event
        self.spool.enqueue_event("agent_started", {
            "hostname": self.config.hostname,
            "agent_version": "1.0.0",
            "source": "service",
            "severity": "info",
        })

        # Run initial baseline scan
        print("[*] Running initial baseline scan...")
        scan_stats = self.scanner.run_full_scan(self.config.monitored_paths)
        print(f"[+] Initial scan complete: {scan_stats}")

        print("[✓] FIM Agent Service is actively running and monitoring.")

    def stop(self):
        print("[*] Stopping FIM Enterprise Windows Agent...")
        self.is_running = False
        self.watcher.stop()
        self.spool.enqueue_event("agent_stopped", {
            "hostname": self.config.hostname,
            "source": "service",
            "severity": "info",
        })
        # Final flush
        self.transport.flush_spool_batch()
        print("[✓] FIM Agent Service stopped cleanly.")

    def _transport_loop(self):
        while self.is_running:
            try:
                flushed = self.transport.flush_spool_batch()
                if flushed > 0:
                    pass
            except Exception as e:
                print(f"[!] Transport loop error: {e}")
            time.sleep(self.config.batch_upload_interval)

    def _heartbeat_loop(self):
        while self.is_running:
            try:
                metrics = self.diagnostics.get_health_metrics(
                    watcher_active=self.watcher.is_running,
                    audit_active=True
                )
                self.transport.send_heartbeat(metrics)
            except Exception as e:
                print(f"[!] Heartbeat loop error: {e}")
            time.sleep(self.config.heartbeat_interval)

    def _audit_loop(self):
        while self.is_running:
            try:
                self.auditor.collect_and_spool()
            except Exception:
                pass
            time.sleep(5)
