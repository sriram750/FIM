from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ServiceHealth(BaseModel):
    status: str = Field(..., description="healthy, degraded, unhealthy, or unreachable")
    latency_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    status: str = Field(..., description="Overall platform health: healthy, degraded, or unhealthy")
    app_name: str
    version: str
    environment: str
    timestamp: datetime
    services: Dict[str, ServiceHealth]
