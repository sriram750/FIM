import requests
import time
import random
from typing import Dict, Any, List, Optional
from configuration.config import AgentConfig
from spool.db import LocalSpool



class TransportClient:
    def __init__(self, config: AgentConfig, spool: LocalSpool):
        self.config = config
        self.spool = spool
        self.session = requests.Session()
        self.backoff_delay = 1.0
        self.max_backoff = 60.0

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.config.endpoint_token:
            headers["X-Endpoint-Key"] = self.config.endpoint_token
        return headers

    def enroll(self, enrollment_token: str) -> bool:
        """
        Enrolls this agent with the FIM central backend server.
        """
        url = f"{self.config.server_url}/api/v1/agents/enroll"
        payload = {
            "hostname": self.config.hostname,
            "agent_version": "1.0.0",
            "enrollment_token": enrollment_token,
        }
        try:
            resp = self.session.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                self.config.endpoint_id = data["endpoint_id"]
                self.config.endpoint_token = data["token"]
                self.config.save()
                return True
            else:
                print(f"[!] Enrollment failed: HTTP {resp.status_code} - {resp.text}")
                return False
        except Exception as e:
            print(f"[!] Network error during enrollment: {e}")
            return False

    def send_heartbeat(self, metrics: Dict[str, Any]) -> bool:
        if not self.config.is_enrolled():
            return False

        url = f"{self.config.server_url}/api/v1/agents/heartbeat"
        try:
            resp = self.session.post(url, json=metrics, headers=self._headers(), timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    def fetch_config(self) -> Optional[Dict[str, Any]]:
        if not self.config.is_enrolled():
            return None

        url = f"{self.config.server_url}/api/v1/agents/config"
        try:
            resp = self.session.get(url, headers=self._headers(), timeout=5)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def flush_spool_batch(self) -> int:
        """
        Reads pending events from local spool, sends batch to server,
        and purges only the acknowledged events.
        """
        if not self.config.is_enrolled():
            return 0

        batch = self.spool.peek_batch(limit=self.config.batch_max_size)
        if not batch:
            return 0

        url = f"{self.config.server_url}/api/v1/agents/events/batch"
        payload = {"events": batch}

        try:
            resp = self.session.post(url, json=payload, headers=self._headers(), timeout=10)
            if resp.status_code == 200:
                result = resp.json()
                acked_ids = result.get("acknowledged_event_ids", [])
                self.spool.acknowledge_events(acked_ids)
                self.backoff_delay = 1.0 # Reset backoff
                return len(acked_ids)
            else:
                # Mark attempts
                self.spool.increment_attempts([e["event_id"] for e in batch if "event_id" in e])
                self._apply_backoff()
                return 0
        except Exception:
            self.spool.increment_attempts([e["event_id"] for e in batch if "event_id" in e])
            self._apply_backoff()
            return 0

    def _apply_backoff(self):
        jitter = random.uniform(0.8, 1.2)
        sleep_time = min(self.backoff_delay * jitter, self.max_backoff)
        time.sleep(sleep_time)
        self.backoff_delay = min(self.backoff_delay * 2, self.max_backoff)
