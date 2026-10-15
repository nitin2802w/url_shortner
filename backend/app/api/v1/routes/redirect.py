# TODO – Module 4: Implement GET /{short_code} (redirect + cache-aside)
# This file will contain the redirect endpoint.
# It depends on:
#   - app.db.session (AsyncSession & Redis dependencies)
#   - app.services.analytics (async click logging)

from fastapi import APIRouter

router = APIRouter()
