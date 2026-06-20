"""
FastAPI dependency injection — shared dependencies across routes.
"""
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database.connection import get_db
from app.services.cache import cache
from app.config import settings


async def get_session(db: AsyncSession = Depends(get_db)) -> AsyncSession:
    """Database session dependency."""
    return db


async def get_cache():
    """Redis cache dependency."""
    return cache


async def get_settings():
    """App settings dependency."""
    return settings


async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """
    Optional API key verification.
    Set API_KEY in .env to enable. Leave blank to disable (dev mode).
    """
    api_key = getattr(settings, "api_key", None)
    if not api_key:
        return True   # API key not configured — allow all (development mode)
    if x_api_key != api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    return True


class PaginationParams:
    def __init__(self, skip: int = 0, limit: int = 50):
        self.skip  = max(0, skip)
        self.limit = min(200, limit)


def get_pagination(skip: int = 0, limit: int = 50) -> PaginationParams:
    return PaginationParams(skip=skip, limit=limit)
