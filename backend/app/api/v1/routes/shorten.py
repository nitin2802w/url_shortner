"""
POST /api/v1/shorten — URL Shortening Endpoint (Module 3)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from app.api.dependencies import get_db, get_redis
from app.schemas.url import ShortenRequest, ShortenResponse
from app.services.url_service import create_short_url
from app.core.config import settings

router = APIRouter()


@router.post(
    "/shorten",
    response_model=ShortenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Shorten a URL",
    description=(
        "Accepts a long URL and returns a shortened version. "
        "Optionally accepts a custom alias (3–16 alphanumeric chars). "
        "Returns **409 Conflict** if the custom alias is already taken."
    ),
)
async def shorten_url(
    payload: ShortenRequest,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
) -> ShortenResponse:

    try:
        url_record = await create_short_url(
            long_url=str(payload.long_url),
            db=db,
            redis=redis,
            custom_alias=payload.custom_alias,
        )
    except ValueError as exc:
        # custom alias already taken
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    return ShortenResponse(
        short_url=f"{settings.BASE_URL}/{url_record.short_code}",
        short_code=url_record.short_code,
        long_url=url_record.long_url,
        custom_alias=url_record.custom_alias,
        clicks=url_record.clicks,
        created_at=url_record.created_at,
    )
