from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class EndpointOut(BaseModel):
    id: str
    hostname: str
    domain: Optional[str] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    os_name: str = "Windows"
    os_version: Optional[str] = None
    os_build: Optional[str] = None
    agent_version: str = "1.0.0"
    status: str = "online"
    last_seen: datetime
    is_isolated: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EndpointListResponse(BaseModel):
    items: List[EndpointOut]
    total: int


class EndpointActionResponse(BaseModel):
    success: bool
    message: str
    endpoint_id: str
