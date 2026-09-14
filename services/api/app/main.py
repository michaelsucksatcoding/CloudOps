from fastapi import FastAPI

from services.api.app.config import settings
from services.api.app.monitoring import ObservabilityMiddleware, setup_logging
from services.api.app.routes import api_router


def create_app() -> FastAPI:
    """Application factory for CloudOps AI API."""
    setup_logging(
        log_level=settings.log_level,
        service_name=settings.app_name,
        environment=settings.environment,
    )

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="CloudOps AI Intelligent Operations Platform API",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Register observability middleware for request tracking and Prometheus metrics
    application.add_middleware(ObservabilityMiddleware)

    application.include_router(api_router)
    return application


app = create_app()
