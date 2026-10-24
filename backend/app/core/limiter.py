"""
Rate Limiter Configuration — Module 6
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
    storage_options={"socket_timeout": 2, "socket_connect_timeout": 2},
    auto_check=False,
)
