"""
SQLAlchemy ORM models for the URL Shortener.

Tables:
  - urls            : Stores the short_code → long_url mapping.
  - click_analytics : Stores individual click events for analytics.
"""

import hashlib
from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class URL(Base):
    """Represents a shortened URL record."""

    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    short_code: Mapped[str] = mapped_column(String(16), unique=True, nullable=False, index=True)
    long_url: Mapped[str] = mapped_column(Text, nullable=False)
    custom_alias: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationship to click analytics
    click_events: Mapped[list["ClickAnalytic"]] = relationship(
        "ClickAnalytic", back_populates="url", cascade="all, delete-orphan"
    )

    def is_expired(self) -> bool:
        """Return True if the URL has passed its expiration timestamp."""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    def __repr__(self) -> str:
        return f"<URL id={self.id} short_code={self.short_code!r}>"


class ClickAnalytic(Base):
    """Stores individual click/redirect events for analytics purposes."""

    __tablename__ = "click_analytics"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    url_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("urls.id", ondelete="CASCADE"), nullable=False, index=True
    )
    clicked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    # Privacy-safe: SHA-256 hash of the client IP address
    ip_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    referrer: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Parsed device/browser info (populated by analytics service)
    device_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    browser: Mapped[str | None] = mapped_column(String(50), nullable=True)

    url: Mapped["URL"] = relationship("URL", back_populates="click_events")

    @staticmethod
    def hash_ip(ip: str) -> str:
        """Return a SHA-256 hex digest of the given IP address."""
        return hashlib.sha256(ip.encode()).hexdigest()

    def __repr__(self) -> str:
        return f"<ClickAnalytic id={self.id} url_id={self.url_id}>"


# Composite index: queries on url_id ordered by clicked_at (for time-series analytics)
Index("ix_click_analytics_url_id_clicked_at", ClickAnalytic.url_id, ClickAnalytic.clicked_at)
