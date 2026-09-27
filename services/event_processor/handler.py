"""Event processor entry point: PostgreSQL consumer for the telemetry pipeline."""

import logging
import time
from datetime import datetime

from sqlalchemy.orm import Session

from services.api.app.config import settings
from services.api.app.database import SessionLocal
from services.api.app.monitoring.logging import setup_logging
from services.api.app.repositories.telemetry import TelemetryRepository
from services.api.app.schemas.telemetry import TelemetryEventCreate
from services.event_processor.processor import TelemetryProcessor

POLL_INTERVAL_SECONDS = 5
POLL_BATCH_SIZE = 100

setup_logging(
    log_level=settings.log_level,
    service_name="cloudops-event-processor",
    environment=settings.environment,
)

logger = logging.getLogger(__name__)

# Default singleton processor shared by the long-lived worker.
default_processor = TelemetryProcessor()


def process_pending_events(
    session: Session,
    processor: TelemetryProcessor,
    after: datetime | None,
    limit: int = POLL_BATCH_SIZE,
) -> tuple[int, datetime | None]:
    """Process telemetry rows persisted after a watermark.

    Returns the number of successfully processed events and the new watermark.
    The rows themselves are left untouched: PostgreSQL remains the durable
    system of record, while the processor routes each event into the hot store
    and the data lake.
    """
    entities = TelemetryRepository(session).list_after_created_at(
        after=after, limit=limit
    )
    if not entities:
        return 0, after

    records = [
        TelemetryEventCreate.model_validate(entity, from_attributes=True).model_dump(
            mode="json"
        )
        for entity in entities
    ]
    result = processor.process_batch(records)
    watermark = entities[-1].created_at
    return int(result["processed"]), watermark


def main() -> None:
    """Consume telemetry persisted in PostgreSQL as a long-lived worker.

    The API validates and persists every accepted telemetry event to PostgreSQL
    before publishing it to the in-process producer. Because that producer is
    process-local, this worker bridges the API and processor processes by
    consuming the durable PostgreSQL rows and routing them through the same
    TelemetryProcessor. A ``created_at`` watermark ensures each row is routed
    once. See docs/architecture/event-processing.md for the durability
    limitation this design carries.
    """
    logger.info("Starting CloudOps event processor (PostgreSQL consumer)")
    processor = default_processor
    watermark: datetime | None = None

    try:
        while True:
            try:
                with SessionLocal() as session:
                    processed, watermark = process_pending_events(
                        session, processor, watermark
                    )
                if processed:
                    logger.info(
                        "Routed %d telemetry event(s) into hot storage and data lake",
                        processed,
                    )
            except Exception:
                # Never let a transient database/storage failure kill the worker.
                logger.exception("Event processing cycle failed; retrying")
            time.sleep(POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        logger.info("Event processor shutting down")


if __name__ == "__main__":
    main()
