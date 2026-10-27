import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional


def get_default_storage_dir() -> Path:
    # Use ProgramData on Windows if available
    program_data = os.environ.get("ProgramData")
    if program_data:
        p = Path(program_data) / "FIMEnterprise"
    else:
        p = Path.cwd() / "data"
    try:
        p.mkdir(parents=True, exist_ok=True)
        return p
    except Exception:
        # Fallback to local data dir
        fallback = Path.cwd() / "data"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


def get_default_config_path() -> Path:
    local_cfg = Path("agent_config.json")
    if local_cfg.exists():
        return local_cfg
    storage = get_default_storage_dir()
    global_cfg = storage / "agent_config.json"
    if global_cfg.exists():
        return global_cfg
    return local_cfg if os.access(Path.cwd(), os.W_OK) else global_cfg


class AgentConfig:
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or get_default_config_path()
        self.data_dir = get_default_storage_dir()
        self.server_url: str = "http://localhost:8000"
        self.endpoint_id: Optional[str] = None
        self.endpoint_token: Optional[str] = None
        self.hostname: str = os.environ.get("COMPUTERNAME", "UNKNOWN-HOST")
        self.heartbeat_interval: int = 30
        self.batch_upload_interval: int = 2
        self.batch_max_size: int = 50
        self.max_file_size_mb: int = 100
        self.monitored_paths: List[str] = []
        self.exclusions: List[Dict[str, str]] = []
        
        self.load()

    def load(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.server_url = data.get("server_url", self.server_url)
                    self.endpoint_id = data.get("endpoint_id", self.endpoint_id)
                    self.endpoint_token = data.get("endpoint_token", self.endpoint_token)
                    self.heartbeat_interval = data.get("heartbeat_interval", self.heartbeat_interval)
                    self.batch_upload_interval = data.get("batch_upload_interval", self.batch_upload_interval)
                    self.batch_max_size = data.get("batch_max_size", self.batch_max_size)
                    self.max_file_size_mb = data.get("max_file_size_mb", self.max_file_size_mb)
                    self.monitored_paths = data.get("monitored_paths", self.monitored_paths)
                    self.exclusions = data.get("exclusions", self.exclusions)
            except Exception as e:
                print(f"[!] Warning: Failed to load config from {self.config_path}: {e}")

    def save(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)
        # Ensure parent directory of config path exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "server_url": self.server_url,
            "endpoint_id": self.endpoint_id,
            "endpoint_token": self.endpoint_token,
            "hostname": self.hostname,
            "heartbeat_interval": self.heartbeat_interval,
            "batch_upload_interval": self.batch_upload_interval,
            "batch_max_size": self.batch_max_size,
            "max_file_size_mb": self.max_file_size_mb,
            "monitored_paths": self.monitored_paths,
            "exclusions": self.exclusions,
        }
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def is_enrolled(self) -> bool:
        return bool(self.endpoint_id and self.endpoint_token)
