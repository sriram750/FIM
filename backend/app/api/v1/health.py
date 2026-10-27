from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timezone
import time

from app.db.session import get_db
from app.core.config import settings
from app.schemas.health import HealthResponse, ServiceHealth

router = APIRouter(tags=["Health & System"])


@router.get("/health", response_model=HealthResponse)
async def check_health(db: AsyncSession = Depends(get_db)):
    """
    Perform deep health checks on primary database, queue, and search engine.
    """
    services = {}
    overall_status = "healthy"

    # 1. Primary Database Check
    db_start = time.perf_counter()
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        db_latency = round((time.perf_counter() - db_start) * 1000, 2)
        services["database"] = ServiceHealth(status="healthy", latency_ms=db_latency)
    except Exception as e:
        db_latency = round((time.perf_counter() - db_start) * 1000, 2)
        services["database"] = ServiceHealth(status="unhealthy", latency_ms=db_latency, details={"error": str(e)})
        overall_status = "unhealthy"

    # 2. Redis Check
    redis_start = time.perf_counter()
    try:
        import redis.asyncio as aioredis
        r = aioredis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD or None,
            socket_connect_timeout=1.0,
            socket_timeout=1.0,
        )
        await r.ping()
        await r.aclose()
        redis_latency = round((time.perf_counter() - redis_start) * 1000, 2)
        services["redis"] = ServiceHealth(status="healthy", latency_ms=redis_latency)
    except Exception as e:
        redis_latency = round((time.perf_counter() - redis_start) * 1000, 2)
        services["redis"] = ServiceHealth(status="degraded", latency_ms=redis_latency, details={"error": "Redis unavailable or not connected"})
        if overall_status == "healthy":
            overall_status = "degraded"

    # 3. OpenSearch Check
    os_start = time.perf_counter()
    try:
        import httpx
        protocol = "https" if settings.OPENSEARCH_USE_SSL else "http"
        url = f"{protocol}://{settings.OPENSEARCH_HOST}:{settings.OPENSEARCH_PORT}"
        async with httpx.AsyncClient(timeout=1.0) as client:
            resp = await client.get(url)
            os_latency = round((time.perf_counter() - os_start) * 1000, 2)
            if resp.status_code == 200:
                services["opensearch"] = ServiceHealth(status="healthy", latency_ms=os_latency)
            else:
                services["opensearch"] = ServiceHealth(status="degraded", latency_ms=os_latency, details={"status_code": resp.status_code})
                if overall_status == "healthy":
                    overall_status = "degraded"
    except Exception:
        os_latency = round((time.perf_counter() - os_start) * 1000, 2)
        services["opensearch"] = ServiceHealth(status="degraded", latency_ms=os_latency, details={"error": "OpenSearch cluster unreachable"})
        if overall_status == "healthy":
            overall_status = "degraded"

    return HealthResponse(
        status=overall_status,
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(timezone.utc),
        services=services,
    )


@router.get("/health/liveness")
async def liveness():
    """Simple ping for container orchestrator or process watcher."""
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}
