import pytest
from datetime import datetime, timezone
import uuid

from app.models.auth import Role, User
from app.models.endpoint import Endpoint, AgentCredential
from app.models.policy import MonitoringPolicy, MonitoredPath
from app.models.event import FileEvent, EventCorrelation
from app.models.baseline import FileBaseline
from app.models.alert import AlertRule, Alert


@pytest.mark.asyncio
async def test_endpoint_and_credential_creation(db_session):
    endpoint = Endpoint(
        id=str(uuid.uuid4()),
        hostname="WIN-SRV-2026",
        domain="CORP.LOCAL",
        ip_address="192.168.1.100",
        os_version="Windows Server 2022 Datacenter",
        agent_version="1.0.0",
        status="online",
    )
    db_session.add(endpoint)
    await db_session.flush()

    cred = AgentCredential(
        id=str(uuid.uuid4()),
        endpoint_id=endpoint.id,
        token_hash="sha256_mock_hash_token",
    )
    db_session.add(cred)
    await db_session.commit()

    assert endpoint.id is not None
    assert cred.endpoint_id == endpoint.id


@pytest.mark.asyncio
async def test_file_event_and_correlation(db_session):
    endpoint = Endpoint(
        id=str(uuid.uuid4()),
        hostname="DESKTOP-FINANCE-01",
        status="online",
    )
    db_session.add(endpoint)
    await db_session.flush()

    event = FileEvent(
        id=str(uuid.uuid4()),
        endpoint_id=endpoint.id,
        client_event_id=str(uuid.uuid4()),
        sequence_number=1,
        event_type="file_modified",
        file_path="C:\\Confidential\\payroll.xlsx",
        file_name="payroll.xlsx",
        file_size_bytes=1048576,
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        event_timestamp=datetime.now(timezone.utc),
        source="watcher",
    )
    db_session.add(event)
    await db_session.flush()

    correlation = EventCorrelation(
        id=str(uuid.uuid4()),
        file_event_id=event.id,
        correlation_status="CONFIRMED",
        correlation_method="HANDLE_MATCH",
        confidence_score=0.98,
        attributed_user="CORP\\john.doe",
        attributed_sid="S-1-5-21-1234567890-1234567890-1001",
    )
    db_session.add(correlation)
    await db_session.commit()

    assert event.id is not None
    assert correlation.attributed_user == "CORP\\john.doe"
    assert correlation.correlation_status == "CONFIRMED"
