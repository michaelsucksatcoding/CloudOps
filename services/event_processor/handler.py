"""AWS Lambda handler entry point for Kinesis event streams."""

import logging
from typing import Any

from services.api.app.config import settings
from services.api.app.monitoring.logging import setup_logging
from services.event_processor.processor import TelemetryProcessor

setup_logging(
    log_level=settings.log_level,
    service_name="cloudops-event-processor",
    environment=settings.environment,
)

logger = logging.getLogger(__name__)

# Default singleton processor for AWS Lambda warm execution environments
default_processor = TelemetryProcessor()


def lambda_handler(
    event: dict[str, Any],
    context: Any,
    processor: TelemetryProcessor | None = None,
) -> dict[str, Any]:
    """Process incoming Kinesis event batch in AWS Lambda."""
    active_processor = processor or default_processor
    records = event.get("Records", [])

    logger.info("Lambda invoked with %d Kinesis records", len(records))
    batch_result = active_processor.process_batch(records)

    return {
        "statusCode": 200,
        "processed": batch_result["processed"],
        "failed": batch_result["failed"],
        "errors": batch_result["errors"],
    }
