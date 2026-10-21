from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.db.session import close_redis, engine
from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.shorten import router as shorten_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    - Startup: nothing special required (engine creates connections lazily).
    - Shutdown: close the Redis connection pool and dispose the DB engine.
    """
    yield
    # Shutdown
    await close_redis()
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="A high-performance URL shortener built with FastAPI, PostgreSQL & Redis.",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(health_router, tags=["Health"])
app.include_router(shorten_router, prefix="/api/v1", tags=["Shorten"])

# Module 4+: uncomment as you build each module
# from app.api.v1.routes.redirect import router as redirect_router
# from app.api.v1.routes.analytics import router as analytics_router
# app.include_router(redirect_router)
# app.include_router(analytics_router, prefix="/api/v1")
