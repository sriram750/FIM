import os
from typing import Dict, Any

try:
    import psutil
except ImportError:
    psutil = None

from spool.db import LocalSpool



class HostDiagnostics:
    def __init__(self, spool: LocalSpool):
        self.spool = spool

    def get_health_metrics(self, watcher_active: bool, audit_active: bool) -> Dict[str, Any]:
        cpu_pct = 0.0
        mem_pct = 0.0

        if psutil:
            try:
                cpu_pct = psutil.cpu_percent(interval=None)
                mem_pct = psutil.virtual_memory().percent
            except Exception:
                pass

        return {
            "queue_depth": self.spool.get_queue_depth(),
            "disk_usage_bytes": self.spool.get_spool_size_bytes(),
            "cpu_percent": float(cpu_pct),
            "memory_percent": float(mem_pct),
            "watcher_status": "active" if watcher_active else "stopped",
            "audit_collector_status": "active" if audit_active else "degraded",
            "policy_version": 1,
        }
