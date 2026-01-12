"""FastAPI application main module."""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from next_epoch import __version__
from next_epoch.config import get_settings
from next_epoch.api.routes import content, digests, health, runs, sources, fields
from next_epoch.db.session import init_db, close_db
from next_epoch.tasks.scheduler import start_scheduler, stop_scheduler

logger = structlog.get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup
    logger.info("Starting Next.Epoch API", version=__version__)
    await init_db()
    start_scheduler()
    yield
    # Shutdown
    logger.info("Shutting down Next.Epoch API")
    stop_scheduler()
    await close_db()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Next.Epoch API",
        description="AI Frontier Intelligence Platform - Track the cutting edge of AI research",
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router, prefix=settings.api_prefix, tags=["Health"])
    app.include_router(content.router, prefix=settings.api_prefix, tags=["Content"])
    app.include_router(digests.router, prefix=settings.api_prefix, tags=["Digests"])
    app.include_router(sources.router, prefix=settings.api_prefix, tags=["Sources"])
    app.include_router(runs.router, prefix=settings.api_prefix, tags=["Runs"])
    app.include_router(fields.router, prefix=settings.api_prefix, tags=["Fields"])

    return app


# Create the app instance
app = create_app()
