"""Telemetry event processor core logic for validation, routing, and dual-tier storage."""

from __future__ import annotations

import base64
import json
import logging
from typing import Any

from services.api.app.monitoring.metrics import (
    TELEMETRY_EVENTS_FAILED_TOTAL,
    TELEMETRY_EVENTS_PROCESSED_TOTAL,
    TELEMETRY_EVENTS_RECEIVED_TOTAL,
)
from services.api.app.schemas.telemetry import TelemetryEventCreate
from services.event_processor.storage import (
    DataLakeStorage,
    HotStorage,
    get_data_lake_store,
    get_hot_store,
)

logger = logging.getLogger(__name__)


class TelemetryProcessor:
    """Processes, validates, and routes incoming telemetry events into hot and cold storage."""

    def __init__(
        self,
        hot_storage: HotStorage | None = None,
        data_lake_storage: DataLakeStorage | None = None,
    ) -> None:
        self.hot_storage = hot_storage or get_hot_store()
        self.data_lake_storage = data_lake_storage or get_data_lake_store()

    def process_event(self, raw_data: dict[str, Any]) -> TelemetryEventCreate:
        """Validate raw telemetry data and write to hot storage and data lake."""
        TELEMETRY_EVENTS_RECEIVED_TOTAL.inc()

        try:
            event = TelemetryEventCreate.model_validate(raw_data)
        except Exception as err:
            TELEMETRY_EVENTS_FAILED_TOTAL.labels(reason="schema_validation_error").inc()
            logger.error("Telemetry event validation failed: %s", err)
            raise ValueError(f"Invalid telemetry event schema: {err}") from err

        # Store in hot / realtime storage
        try:
            if self.hot_storage:
                self.hot_storage.put_event(event)
        except Exception as err:
            TELEMETRY_EVENTS_FAILED_TOTAL.labels(reason="hot_storage_error").inc()
            logger.error("Failed to write event to hot storage: %s", err)

        # Store in cold data lake storage
        try:
            if self.data_lake_storage:
                self.data_lake_storage.save_event(event)
        except Exception as err:
            TELEMETRY_EVENTS_FAILED_TOTAL.labels(reason="data_lake_storage_error").inc()
            logger.error("Failed to write event to data lake: %s", err)

        TELEMETRY_EVENTS_PROCESSED_TOTAL.labels(status="success").inc()

        logger.info(
            "Processed telemetry event: service=%s endpoint=%s status=%d latency=%.1fms",
            event.service,
            event.endpoint,
            event.status_code,
            event.latency_ms,
            extra={
                "event": "telemetry_processed",
                "service_target": event.service,
                "endpoint": event.endpoint,
                "status_code": event.status_code,
                "duration_ms": event.latency_ms,
            },
        )
        return event

    def process_batch(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        """Process a batch of Kinesis or raw records."""
        processed_events: list[TelemetryEventCreate] = []
        errors: list[str] = []

        for idx, record in enumerate(records):
            try:
                # Handle standard Kinesis record wrapper if present
                if "kinesis" in record and "data" in record["kinesis"]:
                    payload_raw = base64.b64decode(record["kinesis"]["data"]).decode(
                        "utf-8"
                    )
                    payload = json.loads(payload_raw)
                elif "data" in record and isinstance(record["data"], str):
                    payload = json.loads(record["data"])
                else:
                    payload = record

                event = self.process_event(payload)
                processed_events.append(event)
            except Exception as err:
                error_msg = f"Record [{idx}] error: {err}"
                logger.error(error_msg)
                errors.append(error_msg)

        return {
            "processed": len(processed_events),
            "failed": len(errors),
            "events": processed_events,
            "errors": errors,
        }
