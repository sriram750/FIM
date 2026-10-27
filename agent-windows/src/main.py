import argparse
import sys
import time
import os

# Ensure Windows console doesn't crash on non-ASCII characters
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

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
        print(f"[OK] Successfully enrolled! Assigned Endpoint ID: {config.endpoint_id}")
        print(f"[OK] Cryptographic endpoint token saved to {config.config_path}")
    else:
        print("[FAIL] Enrollment failed. Verify server URL and enrollment secret token.")
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
    print(f"[OK] Scan completed: {stats}")


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


def cmd_service(args):
    """
    Manage the Windows Service in services.msc (install, start, stop, restart, remove, status)
    """
    try:
        import win32serviceutil
        import win32service
        from service.win_service import FIMWindowsService
    except ImportError:
        print("[FAIL] win32service module is not available. Please ensure pywin32 is installed.")
        sys.exit(1)

    action = args.action
    service_name = FIMWindowsService._svc_name_

    if action == "install":
        print(f"[*] Installing '{service_name}' into Windows Service Control Manager (services.msc)...")
        try:
            exe_path = sys.executable if getattr(sys, 'frozen', False) else None
            win32serviceutil.InstallService(
                win32serviceutil.GetServiceClassString(FIMWindowsService),
                service_name,
                FIMWindowsService._svc_display_name_,
                startType=win32service.SERVICE_AUTO_START,
                description=FIMWindowsService._svc_description_,
                exeName=exe_path
            )
            print(f"[OK] Windows Service '{service_name}' installed successfully!")
        except Exception as e:
            print(f"[FAIL] Failed to install Windows service: {e}")
            sys.exit(1)

    elif action == "start":
        print(f"[*] Starting Windows Service '{service_name}'...")
        try:
            win32serviceutil.StartService(service_name)
            print(f"[OK] Windows Service '{service_name}' started successfully.")
        except Exception as e:
            print(f"[FAIL] Failed to start service: {e}")
            sys.exit(1)

    elif action == "stop":
        print(f"[*] Stopping Windows Service '{service_name}'...")
        try:
            win32serviceutil.StopService(service_name)
            print(f"[OK] Windows Service '{service_name}' stopped.")
        except Exception as e:
            print(f"[FAIL] Failed to stop service: {e}")
            sys.exit(1)

    elif action == "restart":
        print(f"[*] Restarting Windows Service '{service_name}'...")
        try:
            win32serviceutil.RestartService(service_name)
            print(f"[OK] Windows Service '{service_name}' restarted.")
        except Exception as e:
            print(f"[FAIL] Failed to restart service: {e}")
            sys.exit(1)

    elif action == "remove":
        print(f"[*] Removing Windows Service '{service_name}' from services.msc...")
        try:
            win32serviceutil.RemoveService(service_name)
            print(f"[OK] Windows Service '{service_name}' removed.")
        except Exception as e:
            print(f"[FAIL] Failed to remove service: {e}")
            sys.exit(1)

    elif action == "status":
        try:
            status = win32serviceutil.QueryServiceStatus(service_name)
            status_map = {
                win32service.SERVICE_STOPPED: "STOPPED",
                win32service.SERVICE_START_PENDING: "START_PENDING",
                win32service.SERVICE_STOP_PENDING: "STOP_PENDING",
                win32service.SERVICE_RUNNING: "RUNNING",
                win32service.SERVICE_CONTINUE_PENDING: "CONTINUE_PENDING",
                win32service.SERVICE_PAUSE_PENDING: "PAUSE_PENDING",
                win32service.SERVICE_PAUSED: "PAUSED",
            }
            state = status_map.get(status[1], f"UNKNOWN ({status[1]})")
            print(f"Service Name:   {service_name}")
            print(f"Current State:  {state}")
        except Exception as e:
            print(f"Service Status: Not installed or error querying ({e})")


def main():
    # If launched by Windows SCM with no arguments
    if len(sys.argv) == 1 and getattr(sys, 'frozen', False):
        try:
            import servicemanager
            from service.win_service import FIMWindowsService
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(FIMWindowsService)
            servicemanager.StartServiceCtrlDispatcher()
            return
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="FIM Enterprise Windows Agent")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # enroll
    enroll_parser = subparsers.add_parser("enroll", help="Enroll endpoint with server")
    enroll_parser.add_argument("--server", help="Server base URL (e.g. http://localhost:8000)")
    enroll_parser.add_argument("--token", required=True, help="Enrollment secret token")
    enroll_parser.add_argument("--hostname", help="Override local hostname")

    # start
    subparsers.add_parser("start", help="Start the FIM Agent monitoring service in foreground")

    # service
    service_parser = subparsers.add_parser("service", help="Manage background Windows Service in services.msc")
    service_parser.add_argument("action", choices=["install", "start", "stop", "restart", "remove", "status"], help="Service action")

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
    elif args.command == "service":
        cmd_service(args)
    elif args.command == "scan":
        cmd_scan(args)
    elif args.command == "status":
        cmd_status(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
