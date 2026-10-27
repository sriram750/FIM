from sqlalchemy import String, Boolean, ForeignKey, Integer, BigInteger, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
import uuid
from app.db.base import Base, TimestampMixin


class Endpoint(Base, TimestampMixin):
    __tablename__ = "endpoints"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hostname: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    mac_address: Mapped[str] = mapped_column(String(50), nullable=True)
    os_name: Mapped[str] = mapped_column(String(100), default="Windows", nullable=False)
    os_version: Mapped[str] = mapped_column(String(100), nullable=True)
    os_build: Mapped[str] = mapped_column(String(50), nullable=True)
    agent_version: Mapped[str] = mapped_column(String(50), default="1.0.0", nullable=False)
    
    # Status: online, offline, unhealthy, quarantined, revoked
    status: Mapped[str] = mapped_column(String(20), default="online", index=True, nullable=False)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    is_isolated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    credentials: Mapped[list["AgentCredential"]] = relationship("AgentCredential", back_populates="endpoint", cascade="all, delete-orphan")
    checkpoints: Mapped[list["AgentCheckpoint"]] = relationship("AgentCheckpoint", back_populates="endpoint", cascade="all, delete-orphan")
    health_records: Mapped[list["AgentHealthRecord"]] = relationship("AgentHealthRecord", back_populates="endpoint", cascade="all, delete-orphan")
    policy_assignments: Mapped[list["EndpointPolicyAssignment"]] = relationship("EndpointPolicyAssignment", back_populates="endpoint", cascade="all, delete-orphan")


class AgentCredential(Base, TimestampMixin):
    __tablename__ = "agent_credentials"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    endpoint_id: Mapped[str] = mapped_column(String(36), ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    public_key: Mapped[str] = mapped_column(String(1024), nullable=True)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    revoked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    endpoint: Mapped["Endpoint"] = relationship("Endpoint", back_populates="credentials")


class AgentCheckpoint(Base, TimestampMixin):
    __tablename__ = "agent_checkpoints"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    endpoint_id: Mapped[str] = mapped_column(String(36), ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False, index=True)
    last_event_id: Mapped[str] = mapped_column(String(36), nullable=True)
    last_sequence_number: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    usn_journal_id: Mapped[str] = mapped_column(String(50), nullable=True)
    usn_record_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    committed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    endpoint: Mapped["Endpoint"] = relationship("Endpoint", back_populates="checkpoints")


class AgentHealthRecord(Base):
    __tablename__ = "agent_health_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    endpoint_id: Mapped[str] = mapped_column(String(36), ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False, index=True)
    queue_depth: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    disk_usage_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    cpu_percent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    memory_percent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    watcher_status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    audit_collector_status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    policy_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True, nullable=False)

    endpoint: Mapped["Endpoint"] = relationship("Endpoint", back_populates="health_records")
