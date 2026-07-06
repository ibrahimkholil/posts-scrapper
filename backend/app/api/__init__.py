from fastapi import APIRouter

from app.api import auth, wp_connections, jobs

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(wp_connections.router)
api_router.include_router(jobs.router)

__all__ = ["api_router"]
