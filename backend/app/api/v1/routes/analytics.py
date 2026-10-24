"""
GET /api/v1/stats/{short_code} — Analytics Endpoint (Module 5)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.schemas.url import StatsResponse
from app.services.analytics_service import get_url_stats

router = APIRouter()


@router.get(
    "/stats/{short_code}",
    response_model=StatsResponse,
    summary="Get click stats and analytics",
    description=(
        "Returns aggregate click metrics, device breakdown, and browser statistics "
        "for a given short code."
    ),
    responses={
        200: {"description": "Analytics data for the short code"},
        404: {"description": "Short code not found"},
    },
)
async def get_stats(
    short_code: str,
    db: AsyncSession = Depends(get_db),
) -> StatsResponse:
    try:
        return await get_url_stats(short_code, db)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short code '{short_code}' not found.",
        )
