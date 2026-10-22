"""
URL Service — Modules 3 & 4
=============================
Write logic  (Module 3): create_short_url()
Read logic   (Module 4): resolve_short_code(), increment_click_count()

Keeps all DB + cache interactions out of route handlers.
"""

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from app.models.url import URL
from app.services.keygen import generate_short_code
from app.core.config import settings

# Redis TTL constants
_CACHE_TTL_SECONDS     = 86_400   # 24 hours  — positive cache (real URLs)
_NEGATIVE_CACHE_TTL    = 60       # 60 seconds — negative cache (invalid codes)
_NEGATIVE_CACHE_MARKER = "NULL"   # sentinel value stored for missing codes


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


# ---------------------------------------------------------------------------
# Module 4 — Read Service
# ---------------------------------------------------------------------------

async def resolve_short_code(
    short_code: str,
    redis: aioredis.Redis,
    db: AsyncSession,
) -> str:
    """
    Resolve a short code to its original long URL using the Cache-Aside pattern.

    Order of operations:
      1. Check Redis — instant return if cached
      2. Negative cache hit ("NULL") — raise immediately, skip PostgreSQL
      3. Cache miss — query PostgreSQL
      4. Not found in DB — write negative cache, raise 404
      5. Found in DB — write to Redis, return long_url

    Args:
        short_code: The short code to look up (e.g. "git")
        redis:      Async Redis client
        db:         Async SQLAlchemy session

    Returns:
        The original long URL string.

    Raises:
        KeyError: When the short code does not exist (caller maps → HTTP 404)
    """
    cache_key = f"url:{short_code}"

    # ── 1. Redis lookup ───────────────────────────────────────────────────────
    cached = await redis.get(cache_key)

    if cached is not None:
        if cached == _NEGATIVE_CACHE_MARKER:
            # Negative cache hit — short code is known to not exist
            raise KeyError(short_code)
        # Positive cache hit — return immediately, no DB query needed
        return cached

    # ── 2. Cache miss → query PostgreSQL ─────────────────────────────────────
    result = await db.execute(
        select(URL).where(URL.short_code == short_code)
    )
    url_record = result.scalar_one_or_none()

    if url_record is None:
        # Store a negative cache entry so repeat lookups skip the DB
        await redis.set(cache_key, _NEGATIVE_CACHE_MARKER, ex=_NEGATIVE_CACHE_TTL)
        raise KeyError(short_code)

    # ── 3. Populate cache for future requests ─────────────────────────────────
    await redis.set(cache_key, url_record.long_url, ex=_CACHE_TTL_SECONDS)

    return url_record.long_url


async def increment_click_count(short_code: str, db: AsyncSession) -> None:
    """
    Atomically increment the click counter for a given short code.

    Designed to be run as a FastAPI BackgroundTask — called after the
    redirect response has already been sent to the user, so it never
    adds latency to the redirect path.

    Args:
        short_code: The short code that was clicked.
        db:         Async SQLAlchemy session.
    """
    await db.execute(
        update(URL)
        .where(URL.short_code == short_code)
        .values(clicks=URL.clicks + 1)
    )
    await db.commit()
