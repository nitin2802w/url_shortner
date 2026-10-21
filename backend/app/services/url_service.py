"""
URL Write Service — Module 3
=============================
Core business logic for creating shortened URLs.
Keeps all DB + cache interactions out of the route handler.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from app.models.url import URL
from app.services.keygen import generate_short_code
from app.core.config import settings

# Redis TTL for cached URLs — 24 hours
_CACHE_TTL_SECONDS = 86_400


async def create_short_url(
    long_url: str,
    db: AsyncSession,
    redis: aioredis.Redis,
    custom_alias: str | None = None,
) -> URL:
    """
    Persist a new shortened URL and pre-warm the Redis cache.

    Args:
        long_url:      The original long URL to shorten.
        db:            Async SQLAlchemy session.
        redis:         Async Redis client.
        custom_alias:  Optional user-provided short code.

    Returns:
        The newly created URL ORM object.

    Raises:
        ValueError:  If the custom alias is already taken (caller maps → HTTP 409).
    """

    # ── 1. Resolve the short code ────────────────────────────────────────────
    if custom_alias:
        # Check whether this alias already exists in the database
        result = await db.execute(
            select(URL).where(URL.short_code == custom_alias)
        )
        if result.scalar_one_or_none() is not None:
            raise ValueError(f"Alias '{custom_alias}' is already in use.")
        short_code = custom_alias
        is_custom = True
    else:
        short_code = generate_short_code()
        is_custom = False

    # ── 2. Persist to PostgreSQL ─────────────────────────────────────────────
    url_record = URL(
        short_code=short_code,
        long_url=long_url,
        custom_alias=is_custom,
    )
    db.add(url_record)
    await db.flush()   # assigns url_record.id & created_at without full commit
    await db.refresh(url_record)

    # ── 3. Pre-warm Redis cache ──────────────────────────────────────────────
    # Pattern: "url:{short_code}" → long_url  (24-hour TTL)
    await redis.set(f"url:{short_code}", long_url, ex=_CACHE_TTL_SECONDS)

    return url_record
