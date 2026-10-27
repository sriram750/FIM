import argparse
import sys
import time

from configuration.config import AgentConfig
from service.agent_service import FIMAgentService
from spool.db import LocalSpool
from hashing.hasher import FileHasher
from baseline.scanner import BaselineScanner
from transport.client import TransportClient



def cmd_enroll(args):
    config = AgentConfig()
    if args.server:
        config.server_url = args.server
    if args.hostname:
        config.hostname = args.hostname
    
    spool = LocalSpool()
    client = TransportClient(config, spool)
    
    print(f"[*] Enrolling host '{config.hostname}' with server {config.server_url}...")
    success = client.enroll(args.token)
    if success:
        print(f"[✓] Successfully enrolled! Assigned Endpoint ID: {config.endpoint_id}")
        print(f"[✓] Cryptographic endpoint token saved to {config.config_path}")
    else:
        print("[✗] Enrollment failed. Verify server URL and enrollment secret token.")
        sys.exit(1)


def cmd_start(args):
    config = AgentConfig()
    if not config.is_enrolled():
        print("[!] Agent is not enrolled yet. Run 'enroll' command first or configure agent_config.json.")
    
    service = FIMAgentService(config)
    service.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        service.stop()


def cmd_scan(args):
    config = AgentConfig()
    spool = LocalSpool()
    hasher = FileHasher(max_size_mb=config.max_file_size_mb)
    scanner = BaselineScanner(spool, hasher)

    paths = args.paths or config.monitored_paths or ["data/watched_test"]
    print(f"[*] Running baseline scan on paths: {paths}")
    stats = scanner.run_full_scan(paths)
    print(f"[✓] Scan completed: {stats}")


def cmd_status(args):
    config = AgentConfig()
    spool = LocalSpool()
    
    print("=========================================")
    print(" FIM ENTERPRISE — WINDOWS AGENT STATUS")
    print("=========================================")
    print(f"Hostname:        {config.hostname}")
    print(f"Enrolled:        {config.is_enrolled()}")
    print(f"Endpoint ID:     {config.endpoint_id or 'None'}")
    print(f"Server URL:      {config.server_url}")
    print(f"Local Spool DB:  {spool.db_path} ({spool.get_spool_size_bytes()} bytes)")
    print(f"Pending Events:  {spool.get_queue_depth()}")
    print(f"Monitored Paths: {config.monitored_paths or 'None'}")
    print("=========================================")


def main():
    parser = argparse.ArgumentParser(description="FIM Enterprise Windows Agent")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # enroll
    enroll_parser = subparsers.add_parser("enroll", help="Enroll endpoint with server")
    enroll_parser.add_argument("--server", help="Server base URL (e.g. http://localhost:8000)")
    enroll_parser.add_argument("--token", required=True, help="Enrollment secret token")
    enroll_parser.add_argument("--hostname", help="Override local hostname")

    # start
    subparsers.add_parser("start", help="Start the FIM Agent monitoring service")

    # scan
    scan_parser = subparsers.add_parser("scan", help="Run a manual baseline scan")
    scan_parser.add_argument("--paths", nargs="+", help="Specific directories to scan")

    # status
    subparsers.add_parser("status", help="Display local agent diagnostics")

    args = parser.parse_args()
    if args.command == "enroll":
        cmd_enroll(args)
    elif args.command == "start":
        cmd_start(args)
    elif args.command == "scan":
        cmd_scan(args)
    elif args.command == "status":
        cmd_status(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
