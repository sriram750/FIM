from sqlalchemy import String, Boolean, ForeignKey, Integer, BigInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from app.db.base import Base, TimestampMixin


class MonitoringPolicy(Base, TimestampMixin):
    __tablename__ = "monitoring_policies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    scan_interval_seconds: Mapped[int] = mapped_column(Integer, default=3600, nullable=False)
    hash_on_create: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    hash_on_modify: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    max_file_size_mb: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    audit_collection_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    paths: Mapped[list["MonitoredPath"]] = relationship("MonitoredPath", back_populates="policy", cascade="all, delete-orphan")
    exclusions: Mapped[list["PolicyExclusion"]] = relationship("PolicyExclusion", back_populates="policy", cascade="all, delete-orphan")
    assignments: Mapped[list["EndpointPolicyAssignment"]] = relationship("EndpointPolicyAssignment", back_populates="policy", cascade="all, delete-orphan")


class MonitoredPath(Base, TimestampMixin):
    __tablename__ = "monitored_paths"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    policy_id: Mapped[str] = mapped_column(String(36), ForeignKey("monitoring_policies.id", ondelete="CASCADE"), nullable=False, index=True)
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    is_recursive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    track_attributes: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    hash_algorithm: Mapped[str] = mapped_column(String(20), default="SHA-256", nullable=False)

    policy: Mapped["MonitoringPolicy"] = relationship("MonitoringPolicy", back_populates="paths")


class PolicyExclusion(Base, TimestampMixin):
    __tablename__ = "policy_exclusions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    policy_id: Mapped[str] = mapped_column(String(36), ForeignKey("monitoring_policies.id", ondelete="CASCADE"), nullable=False, index=True)
    # pattern_type: wildcard, regex, extension
    pattern_type: Mapped[str] = mapped_column(String(50), default="wildcard", nullable=False)
    pattern: Mapped[str] = mapped_column(String(255), nullable=False)

    policy: Mapped["MonitoringPolicy"] = relationship("MonitoringPolicy", back_populates="exclusions")


class EndpointPolicyAssignment(Base, TimestampMixin):
    __tablename__ = "endpoint_policy_assignments"
    __table_args__ = (
        UniqueConstraint("endpoint_id", "policy_id", name="uq_endpoint_policy"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    endpoint_id: Mapped[str] = mapped_column(String(36), ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False, index=True)
    policy_id: Mapped[str] = mapped_column(String(36), ForeignKey("monitoring_policies.id", ondelete="CASCADE"), nullable=False, index=True)

    endpoint: Mapped["Endpoint"] = relationship("Endpoint", back_populates="policy_assignments")
    policy: Mapped["MonitoringPolicy"] = relationship("MonitoringPolicy", back_populates="assignments")
