# TODO – Module 3: Implement POST /api/v1/shorten
# This file will contain the URL shortening endpoint.
# It depends on:
#   - app.schemas.url (ShortenRequest, ShortenResponse)
#   - app.services.keygen (Base62 / Sqids encoder)
#   - app.db.session (AsyncSession dependency)
#   - app.db.session (Redis dependency)

from fastapi import APIRouter

router = APIRouter()
