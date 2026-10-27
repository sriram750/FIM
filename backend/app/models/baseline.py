from sqlalchemy import String, Boolean, ForeignKey, Integer, BigInteger, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
import uuid
from app.db.base import Base, TimestampMixin


class BaselineScan(Base, TimestampMixin):
    __tablename__ = "baseline_scans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    endpoint_id: Mapped[str] = mapped_column(String(36), ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False, index=True)
    scan_type: Mapped[str] = mapped_column(String(50), default="full", nullable=False) # full, incremental, reconciliation
    status: Mapped[str] = mapped_column(String(50), default="in_progress", nullable=False) # in_progress, completed, failed
    total_files: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    errors_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_details: Mapped[str] = mapped_column(String(1000), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)


class FileBaseline(Base, TimestampMixin):
    __tablename__ = "file_baselines"
    __table_args__ = (
        UniqueConstraint("endpoint_id", "file_path", name="uq_endpoint_file_baseline"),
        Index("idx_baseline_endpoint_path", "endpoint_id", "file_path"),
        Index("idx_baseline_hash", "sha256_hash"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    endpoint_id: Mapped[str] = mapped_column(String(36), ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False, index=True)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    directory_path: Mapped[str] = mapped_column(String(745), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    file_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    file_modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    attributes: Mapped[str] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
