from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.limiter import limiter
from app.db.session import close_redis, engine
from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.shorten import router as shorten_router
from app.api.v1.routes.redirect import router as redirect_router
from app.api.v1.routes.analytics import router as analytics_router


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
# Rate Limiting (Module 6)
# ---------------------------------------------------------------------------
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ---------------------------------------------------------------------------
# Security Headers Middleware (Module 6)
# ---------------------------------------------------------------------------
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# ---------------------------------------------------------------------------
# CORS — allow any localhost port (Vite can use 5173, 5174, etc.)
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(health_router, tags=["Health"])
app.include_router(shorten_router, prefix="/api/v1", tags=["Shorten"])
app.include_router(analytics_router, prefix="/api/v1", tags=["Analytics"])
app.include_router(redirect_router, tags=["Redirect"])
