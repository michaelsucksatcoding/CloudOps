"""API route definitions for CloudOps AI."""

from fastapi import APIRouter

from services.api.app.routes.analytics import router as analytics_router
from services.api.app.routes.events import router as events_router
from services.api.app.routes.health import router as health_router
from services.api.app.routes.incidents import router as incidents_router
from services.api.app.routes.metrics import router as metrics_router
from services.api.app.routes.ml import router as ml_router
from services.api.app.routes.services import router as services_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["Health"])
api_router.include_router(services_router)
api_router.include_router(events_router)
api_router.include_router(metrics_router)
api_router.include_router(ml_router)
api_router.include_router(incidents_router)
api_router.include_router(analytics_router)
