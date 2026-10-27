from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional

from app.db.session import get_db
from app.models.endpoint import Endpoint, AgentCredential
from app.models.auth import User
from app.security.rbac import get_current_active_user, require_permission
from app.schemas.endpoints import EndpointOut, EndpointListResponse, EndpointActionResponse

router = APIRouter(prefix="/endpoints", tags=["Endpoints"])


@router.get("", response_model=EndpointListResponse)
async def list_endpoints(
    search: Optional[str] = Query(None, description="Filter by hostname, IP address, or domain"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (online, offline, etc.)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user: User = Depends(require_permission("endpoints:read")),
    db: AsyncSession = Depends(get_db)
):
    """
    List registered endpoints with search, pagination, and status filters.
    Requires 'endpoints:read' permission (Admin, Analyst, Auditor).
    """
    stmt = select(Endpoint)

    if search:
        search_pattern = f"%{search}%"
        stmt = stmt.where(
            (Endpoint.hostname.ilike(search_pattern)) |
            (Endpoint.ip_address.ilike(search_pattern)) |
            (Endpoint.domain.ilike(search_pattern))
        )

    if status_filter and status_filter != "all":
        stmt = stmt.where(Endpoint.status == status_filter)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.order_by(desc(Endpoint.last_seen)).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    endpoints = result.scalars().all()

    return EndpointListResponse(
        items=[EndpointOut.model_validate(ep) for ep in endpoints],
        total=total
    )


@router.get("/{endpoint_id}", response_model=EndpointOut)
async def get_endpoint(
    endpoint_id: str,
    user: User = Depends(require_permission("endpoints:read")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information for a single endpoint.
    Requires 'endpoints:read' permission.
    """
    stmt = select(Endpoint).where(Endpoint.id == endpoint_id)
    result = await db.execute(stmt)
    endpoint = result.scalar_one_or_none()

    if not endpoint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Endpoint not found")

    return EndpointOut.model_validate(endpoint)


@router.post("/{endpoint_id}/revoke", response_model=EndpointActionResponse)
async def revoke_endpoint(
    endpoint_id: str,
    user: User = Depends(require_permission("endpoints:manage")),
    db: AsyncSession = Depends(get_db)
):
    """
    Revoke credentials and isolate/block an endpoint.
    Requires 'endpoints:manage' permission (Admin only).
    """
    stmt = select(Endpoint).where(Endpoint.id == endpoint_id)
    result = await db.execute(stmt)
    endpoint = result.scalar_one_or_none()

    if not endpoint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Endpoint not found")

    endpoint.status = "revoked"
    endpoint.is_isolated = True

    # Revoke all credentials for this endpoint
    cred_stmt = select(AgentCredential).where(AgentCredential.endpoint_id == endpoint_id)
    cred_result = await db.execute(cred_stmt)
    credentials = cred_result.scalars().all()
    for cred in credentials:
        cred.is_revoked = True

    await db.commit()

    return EndpointActionResponse(
        success=True,
        message=f"Endpoint '{endpoint.hostname}' credentials have been revoked",
        endpoint_id=endpoint_id
    )


@router.delete("/{endpoint_id}", response_model=EndpointActionResponse)
async def delete_endpoint(
    endpoint_id: str,
    user: User = Depends(require_permission("endpoints:delete")),
    db: AsyncSession = Depends(get_db)
):
    """
    Permanently delete an endpoint record.
    Requires 'endpoints:delete' permission (Admin only).
    """
    stmt = select(Endpoint).where(Endpoint.id == endpoint_id)
    result = await db.execute(stmt)
    endpoint = result.scalar_one_or_none()

    if not endpoint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Endpoint not found")

    await db.delete(endpoint)
    await db.commit()

    return EndpointActionResponse(
        success=True,
        message=f"Endpoint '{endpoint.hostname}' has been removed",
        endpoint_id=endpoint_id
    )
