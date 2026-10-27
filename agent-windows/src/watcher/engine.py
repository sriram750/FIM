import os
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from hashing.hasher import FileHasher
from spool.db import LocalSpool



class FIMEventHandler(FileSystemEventHandler):
    def __init__(self, spool: LocalSpool, hasher: FileHasher, exclusions: List[Dict[str, str]] = None):
        super().__init__()
        self.spool = spool
        self.hasher = hasher
        self.exclusions = exclusions or []

    def _is_excluded(self, path_str: str) -> bool:
        filename = os.path.basename(path_str).lower()
        for exc in self.exclusions:
            pattern = exc.get("pattern", "").lower()
            ptype = exc.get("pattern_type", "extension")
            if ptype == "extension" and filename.endswith(pattern):
                return True
            elif ptype == "wildcard" and pattern in filename:
                return True
        return False

    def on_created(self, event: FileSystemEvent):
        if event.is_directory or self._is_excluded(event.src_path):
            return
        
        path_str = str(event.src_path)
        sha, size, mtime, status = self.hasher.compute_sha256(path_str)
        
        payload = {
            "file_path": path_str,
            "file_name": os.path.basename(path_str),
            "file_size_bytes": size,
            "sha256_hash": sha,
            "event_timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "watcher",
            "severity": "info",
            "extra_metadata": {"hashing_status": status, "mtime": mtime}
        }
        self.spool.enqueue_event("file_created", payload)

    def on_modified(self, event: FileSystemEvent):
        if event.is_directory or self._is_excluded(event.src_path):
            return

        path_str = str(event.src_path)
        sha, size, mtime, status = self.hasher.compute_sha256(path_str)

        payload = {
            "file_path": path_str,
            "file_name": os.path.basename(path_str),
            "file_size_bytes": size,
            "sha256_hash": sha,
            "event_timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "watcher",
            "severity": "info",
            "extra_metadata": {"hashing_status": status, "mtime": mtime}
        }
        self.spool.enqueue_event("file_modified", payload)

    def on_deleted(self, event: FileSystemEvent):
        if event.is_directory or self._is_excluded(event.src_path):
            return

        path_str = str(event.src_path)
        payload = {
            "file_path": path_str,
            "file_name": os.path.basename(path_str),
            "file_size_bytes": 0,
            "sha256_hash": None,
            "event_timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "watcher",
            "severity": "medium",
        }
        self.spool.enqueue_event("file_deleted", payload)

    def on_moved(self, event: FileSystemEvent):
        if event.is_directory or self._is_excluded(event.dest_path):
            return

        src_path = str(event.src_path)
        dest_path = str(event.dest_path)
        sha, size, mtime, status = self.hasher.compute_sha256(dest_path)

        payload = {
            "file_path": dest_path,
            "old_file_path": src_path,
            "file_name": os.path.basename(dest_path),
            "file_size_bytes": size,
            "sha256_hash": sha,
            "event_timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "watcher",
            "severity": "info",
            "extra_metadata": {"hashing_status": status, "mtime": mtime}
        }
        self.spool.enqueue_event("file_renamed", payload)


class FilesystemWatcher:
    """
    Watches designated filesystem paths using Windows kernel notifications.
    """
    def __init__(self, spool: LocalSpool, hasher: FileHasher, exclusions: List[Dict[str, str]] = None):
        self.spool = spool
        self.hasher = hasher
        self.exclusions = exclusions or []
        self.observer = Observer()
        self.handler = FIMEventHandler(spool, hasher, exclusions)
        self.watched_paths = []
        self.is_running = False

    def add_watch(self, path_str: str, recursive: bool = True):
        path = Path(path_str)
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass
        if path.is_dir():
            self.observer.schedule(self.handler, path=str(path), recursive=recursive)
            self.watched_paths.append(str(path))

    def start(self):
        if not self.is_running:
            self.observer.start()
            self.is_running = True

    def stop(self):
        if self.is_running:
            self.observer.stop()
            self.observer.join(timeout=5.0)
            self.is_running = False
