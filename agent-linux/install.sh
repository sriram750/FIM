#!/usr/bin/env bash
# ==============================================================================
# FIM Enterprise — Linux Endpoint Agent Installer & Systemd Service Setup
# ==============================================================================
set -euo pipefail

SERVER_URL=""
ENROLLMENT_TOKEN=""
INSTALL_DIR="/opt/fim-agent"
DATA_DIR="/var/lib/fim-agent"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --server)
      SERVER_URL="$2"
      shift 2
      ;;
    --token)
      ENROLLMENT_TOKEN="$2"
      shift 2
      ;;
    --dir)
      INSTALL_DIR="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

if [[ -z "$SERVER_URL" || -z "$ENROLLMENT_TOKEN" ]]; then
  echo "Usage: sudo ./install.sh --server <SERVER_URL> --token <ENROLLMENT_TOKEN>"
  exit 1
fi

if [[ $EUID -ne 0 ]]; then
  echo "[!] This script must be run as root (sudo)."
  exit 1
fi

echo "=========================================================="
echo " FIM ENTERPRISE — LINUX AGENT INSTALLER"
echo "=========================================================="

echo "[*] Creating target directories..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$DATA_DIR"

# Install Python3 & venv if not present
echo "[*] Checking Python3 & prerequisites..."
if ! command -v python3 &>/dev/null; then
  if command -v apt-get &>/dev/null; then
    apt-get update -qq && apt-get install -y -qq python3 python3-venv python3-pip
  elif command -v yum &>/dev/null; then
    yum install -y python3 python3-pip
  else
    echo "[!] Please install Python 3.10+ before continuing."
    exit 1
  fi
fi

# Setup Virtual Environment
echo "[*] Setting up Python virtual environment in $INSTALL_DIR/venv..."
python3 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip --quiet
"$INSTALL_DIR/venv/bin/pip" install watchdog requests psutil --quiet

# Download / copy agent core files
echo "[*] Writing agent core modules..."
cat << 'EOF' > "$INSTALL_DIR/agent.py"
import os
import sys
import time
import json
import sqlite3
import hashlib
import requests
import threading
from pathlib import Path
from datetime import datetime, timezone
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

DATA_DIR = Path("/var/lib/fim-agent")
DATA_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILE = Path("/opt/fim-agent/agent_config.json")
SPOOL_DB = DATA_DIR / "spool.db"

class LocalSpool:
    def __init__(self, db_path=SPOOL_DB):
        self.db_path = db_path
        self.lock = threading.Lock()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS spool_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE NOT NULL,
                    sequence_number INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
            """)
            conn.execute("CREATE TABLE IF NOT EXISTS spool_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);")
            conn.execute("INSERT OR IGNORE INTO spool_meta (key, value) VALUES ('last_seq', '0');")
            conn.commit()

    def enqueue(self, event_type, payload):
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.execute("SELECT value FROM spool_meta WHERE key = 'last_seq';")
                seq = int(cur.fetchone()[0]) + 1
                conn.execute("UPDATE spool_meta SET value = ? WHERE key = 'last_seq';", (str(seq),))
                payload["sequence_number"] = seq
                payload["event_id"] = str(time.time_ns())
                conn.execute(
                    "INSERT INTO spool_events (event_id, sequence_number, event_type, payload_json, created_at) VALUES (?, ?, ?, ?, ?);",
                    (payload["event_id"], seq, event_type, json.dumps(payload), datetime.now(timezone.utc).isoformat())
                )
                conn.commit()

    def peek(self, limit=50):
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.execute("SELECT payload_json FROM spool_events ORDER BY id ASC LIMIT ?;", (limit,))
                return [json.loads(r[0]) for r in cur.fetchall()]

    def ack(self, event_ids):
        if not event_ids: return
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(f"DELETE FROM spool_events WHERE event_id IN ({','.join(['?']*len(event_ids))});", event_ids)
                conn.commit()

spool = LocalSpool()

def hash_file(path):
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest(), os.path.getsize(path)
    except Exception:
        return None, 0

class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory: return
        sha, sz = hash_file(event.src_path)
        spool.enqueue("file_created", {"file_path": event.src_path, "file_name": os.path.basename(event.src_path), "sha256_hash": sha, "file_size_bytes": sz, "source": "watcher", "severity": "info"})
    def on_modified(self, event):
        if event.is_directory: return
        sha, sz = hash_file(event.src_path)
        spool.enqueue("file_modified", {"file_path": event.src_path, "file_name": os.path.basename(event.src_path), "sha256_hash": sha, "file_size_bytes": sz, "source": "watcher", "severity": "info"})
    def on_deleted(self, event):
        if event.is_directory: return
        spool.enqueue("file_deleted", {"file_path": event.src_path, "file_name": os.path.basename(event.src_path), "sha256_hash": None, "file_size_bytes": 0, "source": "watcher", "severity": "medium"})

def run():
    with open(CONFIG_FILE) as f:
        cfg = json.load(f)
    observer = Observer()
    handler = Handler()
    for p in cfg.get("monitored_paths", ["/etc", "/usr/bin", "/var/www"]):
        if os.path.exists(p):
            observer.schedule(handler, path=p, recursive=True)
            print(f"[+] Watching: {p}")
    observer.start()

    session = requests.Session()
    headers = {"Content-Type": "application/json", "X-Endpoint-Key": cfg.get("token", "")}
    print("[✓] FIM Linux Agent is active.")

    while True:
        try:
            batch = spool.peek(50)
            if batch:
                res = session.post(f"{cfg['server_url']}/api/v1/agents/events/batch", json={"events": batch}, headers=headers, timeout=10)
                if res.status_code == 200:
                    spool.ack(res.json().get("acknowledged_event_ids", []))
        except Exception as e:
            pass
        time.sleep(2)

if __name__ == "__main__":
    run()
EOF

# Enroll endpoint with central server
HOSTNAME=$(hostname)
echo "[*] Enrolling Linux node '$HOSTNAME' with server $SERVER_URL..."
ENROLL_RESP=$(curl -s -X POST "$SERVER_URL/api/v1/agents/enroll" \
  -H "Content-Type: application/json" \
  -d "{\"hostname\":\"$HOSTNAME\",\"os_name\":\"Linux\",\"agent_version\":\"1.0.0\",\"enrollment_token\":\"$ENROLLMENT_TOKEN\"}")

TOKEN=$(echo "$ENROLL_RESP" | grep -o '"token":"[^"]*' | cut -d'"' -f4 || true)
ENDPOINT_ID=$(echo "$ENROLL_RESP" | grep -o '"endpoint_id":"[^"]*' | cut -d'"' -f4 || true)

if [[ -z "$TOKEN" ]]; then
  echo "[✗] Enrollment failed. Response: $ENROLL_RESP"
  exit 1
fi

cat << EOF > "$INSTALL_DIR/agent_config.json"
{
  "server_url": "$SERVER_URL",
  "endpoint_id": "$ENDPOINT_ID",
  "token": "$TOKEN",
  "hostname": "$HOSTNAME",
  "monitored_paths": ["/etc", "/usr/bin", "/var/www", "/var/log"]
}
EOF

# Create Systemd Service
echo "[*] Registering systemd service (fim-agent.service)..."
cat << EOF > /etc/systemd/system/fim-agent.service
[Unit]
Description=FIM Enterprise Linux Agent
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/agent.py
Restart=always
RestartSec=5
KillMode=process

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable fim-agent.service
systemctl restart fim-agent.service

echo "=========================================================="
echo " [✓] FIM Linux Agent successfully installed and started!"
echo " Service Status: systemctl status fim-agent"
echo "=========================================================="
