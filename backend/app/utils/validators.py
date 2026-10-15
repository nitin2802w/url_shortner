"""
URL validation utilities.

Checks:
  - Reserved application routes (api, docs, redoc, health, static, admin)
  - Domain loop prevention (shortener's own BASE_URL)
"""

from urllib.parse import urlparse

from app.core.config import settings

# Routes reserved by the FastAPI application — cannot be used as short codes
RESERVED_WORDS: frozenset[str] = frozenset(
    {"api", "docs", "redoc", "health", "static", "admin", "favicon.ico"}
)


def is_reserved(alias: str) -> bool:
    """Return True if the alias conflicts with a reserved application route."""
    return alias.lower() in RESERVED_WORDS


def is_loop(long_url: str) -> bool:
    """
    Return True if the destination URL points back to this shortener's
    own domain, which would create an infinite redirect loop.
    """
    try:
        dest_host = urlparse(long_url).netloc.lower()
        own_host = urlparse(settings.BASE_URL).netloc.lower()
        return dest_host == own_host
    except Exception:
        return False
