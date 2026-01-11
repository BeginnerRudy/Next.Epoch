"""Health check endpoints."""

from datetime import datetime

from fastapi import APIRouter

from next_epoch import __version__

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": __version__,
    }


@router.get("/health/ready")
async def readiness_check():
    """Readiness check - verify service can handle requests."""
    # TODO: Add database connectivity check
    return {"status": "ready"}
