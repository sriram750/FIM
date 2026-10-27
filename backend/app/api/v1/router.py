from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.agents import router as agents_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="", tags=["Health"])
api_router.include_router(agents_router, prefix="", tags=["Agents"])

