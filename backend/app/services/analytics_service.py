"""
Analytics Service — Module 5
============================
Handles asynchronous click event recording and aggregated URL statistics.
"""

import logging
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionFactory
from app.models.url import URL, ClickAnalytic
from app.schemas.url import StatsResponse
from app.core.config import settings

logger = logging.getLogger(__name__)


def detect_device(user_agent: str | None) -> str:
    """Parse user agent string to classify device as mobile, tablet, or desktop."""
    if not user_agent:
        return "desktop"
    ua = user_agent.lower()
    if "ipad" in ua or "tablet" in ua:
        return "tablet"
    if "mobile" in ua or "android" in ua or "iphone" in ua or "ipod" in ua:
        return "mobile"
    return "desktop"


def detect_browser(user_agent: str | None) -> str:
    """Parse user agent string to identify client browser."""
    if not user_agent:
        return "Other"
    ua = user_agent.lower()
    if "edg/" in ua or "edge/" in ua:
        return "Edge"
    if "opr/" in ua or "opera/" in ua:
        return "Opera"
    if "chrome/" in ua or "crios/" in ua:
        return "Chrome"
    if "firefox/" in ua or "fxios/" in ua:
        return "Firefox"
    if "safari/" in ua and "chrome/" not in ua and "crios/" not in ua:
        return "Safari"
    return "Other"


async def record_click(
    short_code: str,
    ip: str | None = None,
    user_agent: str | None = None,
    referrer: str | None = None,
) -> None:
    """
    Background task: records a click event and increments total click count.
    
    Creates a dedicated DB session to ensure independence from the HTTP request lifespan.
    """
    try:
        async with AsyncSessionFactory() as session:
            async with session.begin():
                result = await session.execute(
                    select(URL).where(URL.short_code == short_code)
                )
                url_record = result.scalar_one_or_none()
                if not url_record:
                    logger.warning(f"record_click: short_code '{short_code}' not found.")
                    return

                # Increment total clicks
                url_record.clicks += 1

                # Parse client metadata
                device_type = detect_device(user_agent)
                browser = detect_browser(user_agent)
                ip_hash = ClickAnalytic.hash_ip(ip) if ip else None

                click_event = ClickAnalytic(
                    url_id=url_record.id,
                    ip_hash=ip_hash,
                    user_agent=user_agent[:1000] if user_agent else None,
                    referrer=referrer[:1000] if referrer else None,
                    device_type=device_type,
                    browser=browser,
                )
                session.add(click_event)
    except Exception as exc:
        logger.error(f"Error recording click for '{short_code}': {exc}", exc_info=True)


async def get_url_stats(short_code: str, db: AsyncSession) -> StatsResponse:
    """
    Retrieve aggregated analytics for a specific short code.

    Raises:
        KeyError: If the short code does not exist.
    """
    result = await db.execute(
        select(URL).where(URL.short_code == short_code)
    )
    url_record = result.scalar_one_or_none()
    if not url_record:
        raise KeyError(short_code)

    # 1. Device breakdown
    device_query = await db.execute(
        select(ClickAnalytic.device_type, func.count(ClickAnalytic.id))
        .where(ClickAnalytic.url_id == url_record.id)
        .group_by(ClickAnalytic.device_type)
    )
    device_breakdown = {
        (row[0] or "unknown"): row[1]
        for row in device_query.all()
    }

    # 2. Top browsers
    browser_query = await db.execute(
        select(ClickAnalytic.browser, func.count(ClickAnalytic.id))
        .where(ClickAnalytic.url_id == url_record.id)
        .group_by(ClickAnalytic.browser)
        .order_by(func.count(ClickAnalytic.id).desc())
        .limit(5)
    )
    top_browsers = {
        (row[0] or "unknown"): row[1]
        for row in browser_query.all()
    }

    return StatsResponse(
        short_code=url_record.short_code,
        short_url=f"{settings.BASE_URL}/{url_record.short_code}",
        long_url=url_record.long_url,
        custom_alias=url_record.custom_alias,
        total_clicks=url_record.clicks,
        clicks=url_record.clicks,
        created_at=url_record.created_at,
        device_breakdown=device_breakdown,
        top_browsers=top_browsers,
    )
