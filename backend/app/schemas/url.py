"""
Pydantic schemas for the URL Shortener — Module 3.

ShortenRequest  : what the client POSTs to /api/v1/shorten
ShortenResponse : what we return on success (201 Created)
"""

import re
from datetime import datetime

from pydantic import BaseModel, HttpUrl, field_validator, model_validator

from app.core.config import settings
from app.utils.validators import is_reserved, is_loop

# Custom alias must be 3-16 chars, only letters / digits / hyphen / underscore
_ALIAS_RE = re.compile(r"^[a-zA-Z0-9_-]{3,16}$")


class ShortenRequest(BaseModel):
    long_url: HttpUrl
    custom_alias: str | None = None

    @field_validator("custom_alias")
    @classmethod
    def validate_alias(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not _ALIAS_RE.match(v):
            raise ValueError(
                "custom_alias must be 3–16 characters and contain only "
                "letters, digits, hyphens, or underscores."
            )
        if is_reserved(v):
            raise ValueError(f"'{v}' is a reserved word and cannot be used as an alias.")
        return v

    @model_validator(mode="after")
    def validate_no_loop(self) -> "ShortenRequest":
        if is_loop(str(self.long_url)):
            raise ValueError(
                "The destination URL points back to this shortener — "
                "infinite redirect loops are not allowed."
            )
        return self


class ShortenResponse(BaseModel):
    short_url: str
    short_code: str
    long_url: str
    custom_alias: bool
    clicks: int
    created_at: datetime

    model_config = {"from_attributes": True}


class StatsResponse(BaseModel):
    short_code: str
    short_url: str
    long_url: str
    custom_alias: bool
    total_clicks: int
    clicks: int
    created_at: datetime
    device_breakdown: dict[str, int]
    top_browsers: dict[str, int]

    model_config = {"from_attributes": True}

