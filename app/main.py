"""
FastAPI application entry point.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes.auth import router as auth_router
from app.routes.notes import router as notes_router
from app.routes.tags import router as tags_router
from app.utils.errors import register_exception_handlers

# ── Logging ────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── App Factory ────────────────────────────────────────────────

def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    application = FastAPI(
        title=settings.APP_NAME,
        description="Production-grade CRUD & Auth Service",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── CORS ───────────────────────────────────────────────────
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception Handlers ─────────────────────────────────────
    register_exception_handlers(application)

    # ── Routers ────────────────────────────────────────────────
    application.include_router(auth_router)
    application.include_router(notes_router)
    application.include_router(tags_router)

    # ── Health Check ───────────────────────────────────────────
    @application.get("/health", tags=["Health"])
    def health_check():
        return {"status": "healthy", "service": settings.APP_NAME}

    logger.info("🚀 %s started", settings.APP_NAME)
    return application


app = create_app()
