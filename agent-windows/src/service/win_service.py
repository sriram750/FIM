import sys
import os
import win32serviceutil
import win32service
import win32event
import servicemanager

from configuration.config import AgentConfig
from service.agent_service import FIMAgentService


class FIMWindowsService(win32serviceutil.ServiceFramework):
    _svc_name_ = "FIMEnterpriseAgent"
    _svc_display_name_ = "FIM Enterprise Agent"
    _svc_description_ = "File Integrity Monitoring real-time endpoint security agent"

    def __init__(self, args):
        super().__init__(args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.agent_service = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        if self.agent_service:
            self.agent_service.stop()
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, "")
        )
        try:
            config = AgentConfig()
            self.agent_service = FIMAgentService(config)
            self.agent_service.start()
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
        except Exception as e:
            servicemanager.LogErrorMsg(f"FIM Enterprise Agent runtime error: {e}")
            if self.agent_service:
                self.agent_service.stop()
