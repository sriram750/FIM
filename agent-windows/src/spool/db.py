import sqlite3
import json
import uuid
import os
import threading
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional


class LocalSpool:
    """
    Transactional, crash-safe local SQLite spool database.
    Guarantees that filesystem events are written to durable storage
    before network transmission.
    """
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            local_db = Path("data/spool.db")
            if local_db.exists():
                self.db_path = local_db
            else:
                program_data = os.environ.get("ProgramData")
                if program_data:
                    self.db_path = Path(program_data) / "FIMEnterprise" / "spool.db"
                else:
                    self.db_path = local_db
        else:
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
                    CREATE TABLE IF NOT EXISTS spool_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_id TEXT UNIQUE NOT NULL,
                        sequence_number INTEGER NOT NULL,
                        event_type TEXT NOT NULL,
                        payload_json TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        attempts INTEGER DEFAULT 0,
                        status TEXT DEFAULT 'pending'
                    );
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS spool_meta (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    );
                """)
                conn.execute("""
                    INSERT OR IGNORE INTO spool_meta (key, value) VALUES ('last_sequence', '0');
                """)
                conn.commit()

    def _next_sequence_number(self, conn: sqlite3.Connection) -> int:
        cur = conn.execute("SELECT value FROM spool_meta WHERE key = 'last_sequence';")
        row = cur.fetchone()
        last_seq = int(row["value"]) if row else 0
        new_seq = last_seq + 1
        conn.execute("UPDATE spool_meta SET value = ? WHERE key = 'last_sequence';", (str(new_seq),))
        return new_seq

    def enqueue_event(self, event_type: str, payload: Dict[str, Any]) -> str:
        """
        Enqueues an event transactionally into the local spool.
        Returns the stable event UUID.
        """
        event_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        
        with self.lock:
            with self._connection() as conn:
                seq = self._next_sequence_number(conn)
                payload["event_id"] = event_id
                payload["sequence_number"] = seq
                payload["event_type"] = event_type
                if "event_timestamp" not in payload:
                    payload["event_timestamp"] = created_at

                conn.execute("""
                    INSERT INTO spool_events (event_id, sequence_number, event_type, payload_json, created_at)
                    VALUES (?, ?, ?, ?, ?);
                """, (event_id, seq, event_type, json.dumps(payload), created_at))
                conn.commit()
                return event_id

    def peek_batch(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self.lock:
            with self._connection() as conn:
                cur = conn.execute("""
                    SELECT id, event_id, payload_json, attempts 
                    FROM spool_events 
                    ORDER BY id ASC 
                    LIMIT ?;
                """, (limit,))
                rows = cur.fetchall()
                batch = []
                for r in rows:
                    try:
                        p = json.loads(r["payload_json"])
                        batch.append(p)
                    except Exception:
                        continue
                return batch

    def acknowledge_events(self, event_ids: List[str]) -> int:
        if not event_ids:
            return 0
        with self.lock:
            with self._connection() as conn:
                placeholders = ",".join("?" for _ in event_ids)
                cur = conn.execute(f"""
                    DELETE FROM spool_events WHERE event_id IN ({placeholders});
                """, event_ids)
                conn.commit()
                return cur.rowcount

    def increment_attempts(self, event_ids: List[str]):
        if not event_ids:
            return
        with self.lock:
            with self._connection() as conn:
                placeholders = ",".join("?" for _ in event_ids)
                conn.execute(f"""
                    UPDATE spool_events SET attempts = attempts + 1 WHERE event_id IN ({placeholders});
                """, event_ids)
                conn.commit()

    def get_queue_depth(self) -> int:
        with self.lock:
            with self._connection() as conn:
                cur = conn.execute("SELECT COUNT(*) as cnt FROM spool_events;")
                row = cur.fetchone()
                return row["cnt"] if row else 0

    def get_spool_size_bytes(self) -> int:
        if self.db_path.exists():
            return os.path.getsize(self.db_path)
        return 0
