"""Telemetry events ingestion and retrieval endpoints."""

import logging

from fastapi import APIRouter, Depends, status

from services.api.app.dependencies import (
    get_hot_storage,
    get_producer,
    get_telemetry_repository,
)
from services.api.app.monitoring.metrics import (
    TELEMETRY_EVENTS_FAILED_TOTAL,
    TELEMETRY_EVENTS_RECEIVED_TOTAL,
)
from services.api.app.repositories.telemetry import TelemetryRepository
from services.api.app.schemas.telemetry import (
    TelemetryEventCreate,
    TelemetryEventResponse,
)
from services.event_processor.producer import TelemetryProducer
from services.event_processor.storage import HotStorage

router = APIRouter(tags=["Telemetry Events"])
logger = logging.getLogger(__name__)


@router.post(
    "/events",
    response_model=TelemetryEventResponse,
    status_code=status.HTTP_201_CREATED,
)
def ingest_telemetry_event(
    event_in: TelemetryEventCreate,
    repo: TelemetryRepository = Depends(get_telemetry_repository),
    producer: TelemetryProducer = Depends(get_producer),
) -> TelemetryEventResponse:
    """Ingest, stream, and persist a telemetry event into the platform pipeline."""
    TELEMETRY_EVENTS_RECEIVED_TOTAL.inc()
    # 1. Persist to relational database
    saved_event = repo.create(event_in)

    # 2. Forward event to Kinesis / Streaming ingestion layer
    try:
        producer.send_event(event_in)
    except Exception:
        # Database persistence remains the accepted local ingestion path, but a
        # streaming failure is always observable and never silently discarded.
        TELEMETRY_EVENTS_FAILED_TOTAL.labels(reason="stream_publish_error").inc()
        logger.exception(
            "Telemetry stream publish failed",
            extra={"event": "telemetry_stream_publish_failed"},
        )

    return TelemetryEventResponse.model_validate(saved_event)


@router.get("/events", response_model=list[TelemetryEventResponse])
def list_telemetry_events(
    service: str | None = None,
    skip: int = 0,
    limit: int = 100,
    repo: TelemetryRepository = Depends(get_telemetry_repository),
) -> list[TelemetryEventResponse]:
    """Retrieve telemetry events from primary database, optionally filtered by service."""
    if service:
        events = repo.list_by_service(service=service, skip=skip, limit=limit)
    else:
        events = repo.list_all(skip=skip, limit=limit)
    return [TelemetryEventResponse.model_validate(e) for e in events]


@router.get("/events/hot", response_model=list[TelemetryEventCreate])
def get_hot_telemetry_events(
    service: str,
    limit: int = 50,
    hot_store: HotStorage = Depends(get_hot_storage),
) -> list[TelemetryEventCreate]:
    """Retrieve recent realtime telemetry events from Hot Storage (DynamoDB / Cache)."""
    return hot_store.get_latest_events(service=service, limit=limit)
