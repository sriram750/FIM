import subprocess
import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from spool.db import LocalSpool



class WindowsAuditCollector:
    """
    Subscribes to or queries the Windows Security Event Log for object access audit records:
    - Event ID 4663: An attempt was made to access an object.
    - Event ID 4656: A handle to an object was requested.
    - Event ID 4670: Permissions on an object were changed.
    """
    def __init__(self, spool: LocalSpool):
        self.spool = spool
        self.is_running = False
        self.last_record_id: Optional[int] = None

    def query_recent_security_events(self, max_records: int = 50) -> List[Dict[str, Any]]:
        """
        Queries recent Security audit records via PowerShell Get-WinEvent.
        """
        if os.name != "nt":
            return []

        ps_script = f"""
        try {{
            $events = Get-WinEvent -FilterHashtable @{{
                LogName = 'Security'
                Id = 4663, 4656, 4670
            }} -MaxEvents {max_records} -ErrorAction Stop
            
            $results = @()
            foreach ($e in $events) {{
                $xml = [xml]$e.ToXml()
                $data = @{{}}
                foreach ($d in $xml.Event.EventData.Data) {{
                    $data[$d.Name] = $d.'#text'
                }}
                $results += @{{
                    RecordId = $e.RecordId
                    Id = $e.Id
                    TimeCreated = $e.TimeCreated.ToUniversalTime().ToString("o")
                    AccountName = $data['SubjectUserName']
                    AccountDomain = $data['SubjectDomainName']
                    UserSid = $data['SubjectUserSid']
                    ObjectName = $data['ObjectName']
                    ProcessName = $data['ProcessName']
                    ProcessId = $data['ProcessId']
                }}
            }}
            $results | ConvertTo-Json -Compress
        }} catch {{
            Write-Output "[]"
        }}
        """

        try:
            res = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=10,
            )
            out = res.stdout.strip()
            if out and out != "[]":
                data = json.loads(out)
                if isinstance(data, dict):
                    return [data]
                elif isinstance(data, list):
                    return data
        except Exception:
            pass

        return []

    def collect_and_spool(self):
        records = self.query_recent_security_events()
        for r in records:
            rec_id = r.get("RecordId")
            if self.last_record_id and rec_id and rec_id <= self.last_record_id:
                continue

            payload = {
                "event_record_id": rec_id,
                "event_id": r.get("Id"),
                "event_timestamp": r.get("TimeCreated", datetime.now(timezone.utc).isoformat()),
                "account_name": r.get("AccountName"),
                "account_domain": r.get("AccountDomain"),
                "security_id": r.get("UserSid"),
                "object_name": r.get("ObjectName"),
                "process_name": r.get("ProcessName"),
                "process_id": r.get("ProcessId"),
                "source": "audit_log",
                "severity": "info",
            }
            self.spool.enqueue_event("audit_event", payload)
            if rec_id:
                self.last_record_id = rec_id
