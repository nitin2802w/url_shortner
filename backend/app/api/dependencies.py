"""
FastAPI dependencies — DB session & Redis client injectors.
Rate-limiting middleware will be added in Module 6.
"""

from typing import AsyncGenerator

import redis.asyncio as aioredis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionFactory, get_redis as _get_redis


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session for the duration of a single request."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_redis() -> aioredis.Redis:
    """Return the shared async Redis client."""
    return await _get_redis()
