"""Health check endpoints for system probes, liveness, and readiness."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from services.api.app.config import Settings
from services.api.app.database import get_db
from services.api.app.dependencies import get_settings
from services.api.app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def get_health(
    config: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> HealthResponse:
    """System liveness, readiness, and database connectivity probe."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unavailable"

    overall_status = "ok" if db_status == "connected" else "degraded"

    return HealthResponse(
        status=overall_status,
        app=config.app_name,
        version=config.app_version,
        environment=config.environment,
        timestamp=datetime.now(UTC),
        database=db_status,
    )


@router.get("/health/live", response_model=HealthResponse)
def get_liveness(
    config: Settings = Depends(get_settings),
) -> HealthResponse:
    """Kubernetes liveness probe: verifies process is alive without touching external systems."""
    return HealthResponse(
        status="ok",
        app=config.app_name,
        version=config.app_version,
        environment=config.environment,
        timestamp=datetime.now(UTC),
        database="untested",
    )


@router.get("/health/ready", response_model=HealthResponse)
def get_readiness(
    config: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> HealthResponse:
    """Kubernetes readiness probe: verifies database connectivity before routing traffic."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connectivity check failed: {exc}",
        ) from exc

    return HealthResponse(
        status="ok",
        app=config.app_name,
        version=config.app_version,
        environment=config.environment,
        timestamp=datetime.now(UTC),
        database=db_status,
    )
