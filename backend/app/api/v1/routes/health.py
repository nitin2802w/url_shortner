from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/health", summary="Health Check")
async def health_check() -> dict:
    """
    Returns the operational status of the service.
    Use this endpoint to verify the application is running before
    exercising other routes or running integration tests.
    """
    return {"status": "ok", "service": settings.PROJECT_NAME}
