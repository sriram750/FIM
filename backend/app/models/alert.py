from sqlalchemy import String, Boolean, ForeignKey, Integer, DateTime, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
import uuid
from app.db.base import Base, TimestampMixin


class AlertRule(Base, TimestampMixin):
    __tablename__ = "alert_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. baseline_mismatch, unexpected_deletion, bulk_burst
    severity: Mapped[str] = mapped_column(String(20), default="high", nullable=False) # low, medium, high, critical
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    cooldown_seconds: Mapped[int] = mapped_column(Integer, default=300, nullable=False)
    conditions_json: Mapped[str] = mapped_column(Text, nullable=False) # JSON condition definitions

    alerts: Mapped[list["Alert"]] = relationship("Alert", back_populates="rule")


class Alert(Base, TimestampMixin):
    __tablename__ = "alerts"
    __table_args__ = (
        Index("idx_alerts_status_severity", "status", "severity"),
        Index("idx_alerts_endpoint", "endpoint_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_id: Mapped[str] = mapped_column(String(36), ForeignKey("alert_rules.id", ondelete="SET NULL"), nullable=True)
    endpoint_id: Mapped[str] = mapped_column(String(36), ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="high", nullable=False)
    
    # status: open, investigating, resolved, closed, false_positive
    status: Mapped[str] = mapped_column(String(30), default="open", nullable=False, index=True)
    assigned_to: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    first_triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    last_triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    event_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    resolution_reason: Mapped[str] = mapped_column(Text, nullable=True)
    resolved_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    rule: Mapped["AlertRule"] = relationship("AlertRule", back_populates="alerts")
    alert_events: Mapped[list["AlertEvent"]] = relationship("AlertEvent", back_populates="alert", cascade="all, delete-orphan")
    notes: Mapped[list["InvestigationNote"]] = relationship("InvestigationNote", back_populates="alert", cascade="all, delete-orphan")


class AlertEvent(Base, TimestampMixin):
    __tablename__ = "alert_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_id: Mapped[str] = mapped_column(String(36), ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    file_event_id: Mapped[str] = mapped_column(String(36), ForeignKey("file_events.id", ondelete="CASCADE"), nullable=False, index=True)

    alert: Mapped["Alert"] = relationship("Alert", back_populates="alert_events")


class InvestigationNote(Base, TimestampMixin):
    __tablename__ = "investigation_notes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_id: Mapped[str] = mapped_column(String(36), ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    author_name: Mapped[str] = mapped_column(String(100), nullable=False)
    note_text: Mapped[str] = mapped_column(Text, nullable=False)

    alert: Mapped["Alert"] = relationship("Alert", back_populates="notes")
