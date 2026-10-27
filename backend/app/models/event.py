from sqlalchemy import String, Boolean, ForeignKey, Integer, BigInteger, DateTime, Float, Text, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
import uuid
from app.db.base import Base, TimestampMixin


class FileEvent(Base, TimestampMixin):
    __tablename__ = "file_events"
    __table_args__ = (
        UniqueConstraint("endpoint_id", "client_event_id", name="uq_endpoint_client_event"),
        Index("idx_file_events_endpoint_time", "endpoint_id", "event_timestamp"),
        Index("idx_file_events_path", "file_path"),
        Index("idx_file_events_type", "event_type"),
        Index("idx_file_events_hash", "sha256_hash"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    endpoint_id: Mapped[str] = mapped_column(String(36), ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False, index=True)
    client_event_id: Mapped[str] = mapped_column(String(36), nullable=False) # UUID assigned by agent
    sequence_number: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    
    # event_type: file_created, file_modified, file_deleted, file_renamed, baseline_created, integrity_mismatch, watcher_overflow
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    old_file_path: Mapped[str] = mapped_column(String(1000), nullable=True) # for renames
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    
    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=True)
    old_sha256_hash: Mapped[str] = mapped_column(String(64), nullable=True)
    
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    ingestion_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    
    source: Mapped[str] = mapped_column(String(50), default="watcher", nullable=False) # watcher, reconciliation, usn
    severity: Mapped[str] = mapped_column(String(20), default="info", nullable=False) # info, low, medium, high, critical
    schema_version: Mapped[str] = mapped_column(String(10), default="1.0", nullable=False)
    extra_metadata: Mapped[str] = mapped_column(Text, nullable=True) # JSON extra metadata

    # Relationships
    correlations: Mapped[list["EventCorrelation"]] = relationship("EventCorrelation", back_populates="file_event", cascade="all, delete-orphan")


class SecurityEvent(Base, TimestampMixin):
    __tablename__ = "security_events"
    __table_args__ = (
        Index("idx_sec_events_endpoint_time", "endpoint_id", "event_time"),
        Index("idx_sec_events_object", "object_name"),
        Index("idx_sec_events_user", "account_name"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    endpoint_id: Mapped[str] = mapped_column(String(36), ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False, index=True)
    event_record_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    channel: Mapped[str] = mapped_column(String(50), default="Security", nullable=False)
    event_id: Mapped[int] = mapped_column(Integer, nullable=False) # 4663, 4656, 4670
    computer_name: Mapped[str] = mapped_column(String(255), nullable=True)
    
    security_id: Mapped[str] = mapped_column(String(100), nullable=True) # SID
    account_name: Mapped[str] = mapped_column(String(100), nullable=True)
    account_domain: Mapped[str] = mapped_column(String(100), nullable=True)
    
    process_id: Mapped[int] = mapped_column(Integer, nullable=True)
    process_name: Mapped[str] = mapped_column(String(500), nullable=True)
    access_mask: Mapped[str] = mapped_column(String(50), nullable=True)
    access_list: Mapped[str] = mapped_column(String(500), nullable=True)
    object_name: Mapped[str] = mapped_column(String(1000), nullable=True)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    correlations: Mapped[list["EventCorrelation"]] = relationship("EventCorrelation", back_populates="security_event")


class EventCorrelation(Base, TimestampMixin):
    __tablename__ = "event_correlations"
    __table_args__ = (
        Index("idx_correlation_file_event", "file_event_id"),
        Index("idx_correlation_attributed_user", "attributed_user"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_event_id: Mapped[str] = mapped_column(String(36), ForeignKey("file_events.id", ondelete="CASCADE"), nullable=False)
    security_event_id: Mapped[str] = mapped_column(String(36), ForeignKey("security_events.id", ondelete="SET NULL"), nullable=True)
    
    # correlation_status: CONFIRMED, PROBABLE, AMBIGUOUS, UNKNOWN
    correlation_status: Mapped[str] = mapped_column(String(30), default="UNKNOWN", nullable=False, index=True)
    # correlation_method: HANDLE_MATCH, TIME_PATH_WINDOW, PROCESS_PID, NONE
    correlation_method: Mapped[str] = mapped_column(String(50), default="NONE", nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    attributed_user: Mapped[str] = mapped_column(String(150), default="Unknown / Not attributed", nullable=False)
    attributed_sid: Mapped[str] = mapped_column(String(100), nullable=True)
    evidence_notes: Mapped[str] = mapped_column(Text, nullable=True)

    file_event: Mapped["FileEvent"] = relationship("FileEvent", back_populates="correlations")
    security_event: Mapped["SecurityEvent"] = relationship("SecurityEvent", back_populates="correlations")
