from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timezone
import hashlib
import secrets
import uuid
import json

from app.db.session import get_db
from app.core.config import settings
from app.core.logging import logger
from app.models.endpoint import Endpoint, AgentCredential, AgentHealthRecord
from app.models.event import FileEvent
from app.schemas.agents import (
    AgentEnrollRequest,
    AgentEnrollResponse,
    AgentHeartbeatRequest,
    AgentHeartbeatResponse,
    AgentEventsBatchRequest,
    AgentEventsBatchResponse,
    AgentConfigResponse,
    MonitoredPathConfig,
)

router = APIRouter(prefix="/agents", tags=["Agents"])


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def get_current_agent(
    x_endpoint_key: str = Header(None, alias="X-Endpoint-Key"),
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db)
) -> Endpoint:
    token = x_endpoint_key
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing endpoint authentication token (X-Endpoint-Key or Bearer token required)"
        )

    token_h = hash_token(token)
    stmt = select(AgentCredential).where(
        and_(
            AgentCredential.token_hash == token_h,
            AgentCredential.is_revoked == False
        )
    )
    result = await db.execute(stmt)
    cred = result.scalar_one_or_none()

    if not cred:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, expired, or revoked endpoint credentials"
        )

    endpoint_stmt = select(Endpoint).where(Endpoint.id == cred.endpoint_id)
    ep_result = await db.execute(endpoint_stmt)
    endpoint = ep_result.scalar_one_or_none()

    if not endpoint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Endpoint record not found")

    if endpoint.status == "revoked":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Endpoint access has been revoked")

    return endpoint


@router.post("/enroll", response_model=AgentEnrollResponse)
async def enroll_agent(req: AgentEnrollRequest, db: AsyncSession = Depends(get_db)):
    """
    Enroll a new Windows endpoint using the pre-shared enrollment secret.
    Generates a unique, revocable cryptographic token for the agent.
    """
    if req.enrollment_token != settings.ENROLLMENT_TOKEN_SECRET:
        logger.warning(f"Failed enrollment attempt for host {req.hostname}: invalid enrollment token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid enrollment token")

    # Check if endpoint with same hostname exists, or create new
    stmt = select(Endpoint).where(Endpoint.hostname == req.hostname)
    result = await db.execute(stmt)
    endpoint = result.scalar_one_or_none()

    if not endpoint:
        endpoint = Endpoint(
            id=str(uuid.uuid4()),
            hostname=req.hostname,
            domain=req.domain,
            ip_address=req.ip_address,
            mac_address=req.mac_address,
            os_name=req.os_name,
            os_version=req.os_version,
            os_build=req.os_build,
            agent_version=req.agent_version,
            status="online",
            last_seen=datetime.now(timezone.utc),
        )
        db.add(endpoint)
        await db.flush()
    else:
        endpoint.domain = req.domain or endpoint.domain
        endpoint.ip_address = req.ip_address or endpoint.ip_address
        endpoint.os_version = req.os_version or endpoint.os_version
        endpoint.agent_version = req.agent_version or endpoint.agent_version
        endpoint.last_seen = datetime.now(timezone.utc)
        endpoint.status = "online"

    # Generate unique 64-char hex key
    raw_key = f"fim_agent_{secrets.token_hex(32)}"
    key_h = hash_token(raw_key)

    # Invalidate old credentials for this host
    old_creds_stmt = select(AgentCredential).where(
        and_(AgentCredential.endpoint_id == endpoint.id, AgentCredential.is_revoked == False)
    )
    old_res = await db.execute(old_creds_stmt)
    for c in old_res.scalars():
        c.is_revoked = True
        c.revoked_at = datetime.now(timezone.utc)

    # Create new credential
    credential = AgentCredential(
        id=str(uuid.uuid4()),
        endpoint_id=endpoint.id,
        token_hash=key_h,
    )
    db.add(credential)
    await db.commit()

    logger.info(f"Endpoint enrolled successfully: {endpoint.hostname} ({endpoint.id})")

    return AgentEnrollResponse(
        endpoint_id=endpoint.id,
        token=raw_key,
        hostname=endpoint.hostname,
        status="online",
        message="Agent enrolled successfully. Store your endpoint token securely."
    )


@router.post("/heartbeat", response_model=AgentHeartbeatResponse)
async def heartbeat(
    req: AgentHeartbeatRequest,
    agent: Endpoint = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db)
):
    """
    Report agent heartbeat, operational metrics, queue depth, and health telemetry.
    """
    agent.last_seen = datetime.now(timezone.utc)
    if agent.status != "quarantined":
        agent.status = "online"

    health_record = AgentHealthRecord(
        id=str(uuid.uuid4()),
        endpoint_id=agent.id,
        queue_depth=req.queue_depth,
        disk_usage_bytes=req.disk_usage_bytes,
        cpu_percent=req.cpu_percent,
        memory_percent=req.memory_percent,
        watcher_status=req.watcher_status,
        audit_collector_status=req.audit_collector_status,
        policy_version=req.policy_version,
        recorded_at=datetime.now(timezone.utc),
    )
    db.add(health_record)
    await db.commit()

    return AgentHeartbeatResponse(
        status="ok",
        acknowledged_at=datetime.now(timezone.utc),
        policy_version_expected=1,
    )


@router.get("/config", response_model=AgentConfigResponse)
async def get_agent_config(
    agent: Endpoint = Depends(get_current_agent),
):
    """
    Get active monitoring policy and monitored paths for the endpoint.
    """
    return AgentConfigResponse(
        endpoint_id=agent.id,
        policy_name="Enterprise Default Baseline",
        policy_version=1,
        scan_interval_seconds=3600,
        hash_on_create=True,
        hash_on_modify=True,
        max_file_size_mb=100,
        audit_collection_enabled=True,
        monitored_paths=[
            MonitoredPathConfig(path=r"C:\Windows\System32\drivers\etc", is_recursive=False),
            MonitoredPathConfig(path=r"C:\Program Files\Common Files", is_recursive=True),
        ],
        exclusions=[
            {"pattern_type": "extension", "pattern": ".tmp"},
            {"pattern_type": "extension", "pattern": ".log"},
        ]
    )


@router.post("/events/batch", response_model=AgentEventsBatchResponse)
async def ingest_event_batch(
    batch: AgentEventsBatchRequest,
    agent: Endpoint = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db)
):
    """
    Durable batch ingestion of file integrity events from agent local spool.
    Idempotent and deduplicated on (endpoint_id, client_event_id).
    """
    acknowledged_ids = []
    now_utc = datetime.now(timezone.utc)

    for item in batch.events:
        # Check if event already exists (deduplication)
        check_stmt = select(FileEvent.id).where(
            and_(
                FileEvent.endpoint_id == agent.id,
                FileEvent.client_event_id == item.event_id
            )
        )
        res = await db.execute(check_stmt)
        if res.scalar_one_or_none():
            acknowledged_ids.append(item.event_id)
            continue

        file_event = FileEvent(
            id=str(uuid.uuid4()),
            endpoint_id=agent.id,
            client_event_id=item.event_id,
            sequence_number=item.sequence_number,
            event_type=item.event_type,
            file_path=item.file_path,
            old_file_path=item.old_file_path,
            file_name=item.file_name,
            file_size_bytes=item.file_size_bytes,
            sha256_hash=item.sha256_hash,
            old_sha256_hash=item.old_sha256_hash,
            event_timestamp=item.event_timestamp,
            ingestion_timestamp=now_utc,
            source=item.source,
            severity=item.severity,
            schema_version=item.schema_version,
            extra_metadata=json.dumps(item.extra_metadata) if item.extra_metadata else None,
        )
        db.add(file_event)
        acknowledged_ids.append(item.event_id)

    await db.commit()

    return AgentEventsBatchResponse(
        acknowledged_event_ids=acknowledged_ids,
        count=len(acknowledged_ids),
        received_at=now_utc,
    )


@router.get("/installer-info")
async def get_installer_info():
    """
    Returns deployment commands and configuration tokens for Windows and Linux agent installation.
    """
    return {
        "server_url": f"http://{settings.SERVER_HOST}:{settings.SERVER_PORT}",
        "enrollment_token": settings.ENROLLMENT_TOKEN_SECRET,
        "windows": {
            "powershell_command": f'& "C:\\Temp\\FIM\\agent-windows\\installer\\install.ps1" -ServerUrl "http://{settings.SERVER_HOST}:{settings.SERVER_PORT}" -EnrollmentToken "{settings.ENROLLMENT_TOKEN_SECRET}"',
            "exe_download_url": f"/api/v1/agents/download/windows-exe",
            "msi_download_url": f"/api/v1/agents/download/windows-msi",
        },
        "linux": {
            "bash_command": f'curl -sSL http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/api/v1/agents/download/linux-script | sudo bash -s -- --server "http://{settings.SERVER_HOST}:{settings.SERVER_PORT}" --token "{settings.ENROLLMENT_TOKEN_SECRET}"',
            "script_download_url": f"/api/v1/agents/download/linux-script",
        }
    }


@router.get("/download/windows-exe")
async def download_windows_exe():
    from fastapi.responses import FileResponse, PlainTextResponse
    import os
    exe_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../agent-windows/dist/fim-agent.exe"))
    if os.path.exists(exe_path):
        return FileResponse(exe_path, media_type="application/vnd.microsoft.portable-executable", filename="fim-agent.exe")
    return PlainTextResponse("fim-agent.exe not found on server", status_code=404)


@router.get("/download/windows-msi")
async def download_windows_msi():
    from fastapi.responses import FileResponse, PlainTextResponse
    import os
    msi_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../agent-windows/dist/fim-agent-installer.msi"))
    if os.path.exists(msi_path):
        return FileResponse(msi_path, media_type="application/x-msi", filename="fim-agent-installer.msi")
    return PlainTextResponse("fim-agent-installer.msi not found on server", status_code=404)


@router.get("/download/linux-script")
async def download_linux_script():
    from fastapi.responses import FileResponse, PlainTextResponse
    import os
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../agent-linux/install.sh"))
    if os.path.exists(script_path):
        return FileResponse(script_path, media_type="text/x-shellscript", filename="install.sh")
    return PlainTextResponse("# Linux agent installer not found on server", status_code=404)


