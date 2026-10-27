import sqlite3
import os
import threading
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from hashing.hasher import FileHasher
from spool.db import LocalSpool


class BaselineScanner:
    """
    Computes full directory baseline snapshots and periodically reconciles
    monitored paths against stored baselines to detect offline/missed changes.
    """
    def __init__(self, spool: LocalSpool, hasher: FileHasher, db_path: Path = Path("data/baseline.db")):
        self.spool = spool
        self.hasher = hasher
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self._init_db()

    @contextmanager
    def _connection(self):
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self.lock:
            with self._connection() as conn:
                conn.execute("PRAGMA journal_mode = WAL;")
                conn.execute("PRAGMA synchronous = NORMAL;")
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS file_baselines (
                        file_path TEXT PRIMARY KEY,
                        file_name TEXT NOT NULL,
                        directory_path TEXT NOT NULL,
                        file_size_bytes INTEGER NOT NULL,
                        sha256_hash TEXT NOT NULL,
                        last_scanned_at TEXT NOT NULL
                    );
                """)
                conn.commit()

    def run_full_scan(self, directories: List[str]) -> Dict[str, int]:
        stats = {"files_scanned": 0, "mismatches": 0, "new_baselines": 0}
        now_iso = datetime.now(timezone.utc).isoformat()

        for dir_path_str in directories:
            dir_path = Path(dir_path_str)
            if not dir_path.exists() or not dir_path.is_dir():
                continue

            for root, _, files in os.walk(dir_path):
                for f in files:
                    full_path = os.path.abspath(os.path.join(root, f))
                    stats["files_scanned"] += 1

                    sha, size, mtime, status = self.hasher.compute_sha256(full_path)
                    if status != "success" or not sha:
                        continue

                    with self.lock:
                        with self._connection() as conn:
                            cur = conn.execute("SELECT sha256_hash, file_size_bytes FROM file_baselines WHERE file_path = ?;", (full_path,))
                            row = cur.fetchone()

                            if not row:
                                conn.execute("""
                                    INSERT INTO file_baselines (file_path, file_name, directory_path, file_size_bytes, sha256_hash, last_scanned_at)
                                    VALUES (?, ?, ?, ?, ?, ?);
                                """, (full_path, f, root, size, sha, now_iso))
                                conn.commit()
                                stats["new_baselines"] += 1

                                self.spool.enqueue_event("baseline_created", {
                                    "file_path": full_path,
                                    "file_name": f,
                                    "file_size_bytes": size,
                                    "sha256_hash": sha,
                                    "source": "reconciliation",
                                    "severity": "info",
                                })
                            elif row["sha256_hash"] != sha:
                                old_hash = row["sha256_hash"]
                                conn.execute("""
                                    UPDATE file_baselines 
                                    SET sha256_hash = ?, file_size_bytes = ?, last_scanned_at = ?
                                    WHERE file_path = ?;
                                """, (sha, size, now_iso, full_path))
                                conn.commit()
                                stats["mismatches"] += 1

                                self.spool.enqueue_event("integrity_mismatch", {
                                    "file_path": full_path,
                                    "file_name": f,
                                    "file_size_bytes": size,
                                    "sha256_hash": sha,
                                    "old_sha256_hash": old_hash,
                                    "source": "reconciliation",
                                    "severity": "high",
                                })

        return stats
