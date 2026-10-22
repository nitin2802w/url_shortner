"""
GET /{short_code} — Redirect Endpoint (Module 4)
"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from app.api.dependencies import get_db, get_redis
from app.services.url_service import resolve_short_code, increment_click_count

router = APIRouter()


@router.get(
    "/{short_code}",
    summary="Redirect to original URL",
    description=(
        "Looks up the short code in Redis (and falls back to PostgreSQL on "
        "a cache miss), then issues an **HTTP 302** redirect to the original URL. "
        "The click counter is incremented asynchronously after the response "
        "is sent — so redirect latency is never affected by the DB write."
    ),
    response_class=RedirectResponse,
    status_code=status.HTTP_302_FOUND,
    responses={
        302: {"description": "Redirect to the original long URL"},
        404: {"description": "Short code not found"},
    },
)
async def redirect_to_url(
    short_code: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
) -> RedirectResponse:

    try:
        long_url = await resolve_short_code(short_code, redis, db)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short code '{short_code}' not found.",
        )

    # Fire-and-forget: increment click counter AFTER response is sent
    background_tasks.add_task(increment_click_count, short_code, db)

    return RedirectResponse(url=long_url, status_code=status.HTTP_302_FOUND)
