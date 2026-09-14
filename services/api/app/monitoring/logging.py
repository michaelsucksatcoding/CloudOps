"""Structured JSON logging configuration with request correlation for CloudOps AI."""

from __future__ import annotations

import json
import logging
import sys
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

# Context variable for thread-safe/async-safe request correlation tracking
request_id_context: ContextVar[str | None] = ContextVar("request_id", default=None)


def get_current_request_id() -> str | None:
    """Retrieve current correlation request ID from context."""
    return request_id_context.get()


def set_current_request_id(request_id: str | None) -> None:
    """Set correlation request ID in active context."""
    request_id_context.set(request_id)


class JSONLogFormatter(logging.Formatter):
    """Formats log records as structured JSON documents."""

    def __init__(
        self,
        service_name: str = "cloudops-api",
        environment: str = "dev",
    ) -> None:
        super().__init__()
        self.service_name = service_name
        self.environment = environment

    def format(self, record: logging.LogRecord) -> str:
        """Serialize log record to single-line JSON string."""
        log_payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "service": self.service_name,
            "environment": self.environment,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include request correlation ID if present in context or record
        request_id = getattr(record, "request_id", None) or get_current_request_id()
        if request_id:
            log_payload["request_id"] = request_id

        # Include optional contextual attributes attached to log record
        for attr in (
            "event",
            "duration_ms",
            "status_code",
            "endpoint",
            "method",
            "service_target",
        ):
            if hasattr(record, attr):
                log_payload[attr] = getattr(record, attr)

        # Include exception traceback if present
        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_payload, default=str)


def setup_logging(
    log_level: str = "INFO",
    service_name: str = "cloudops-api",
    environment: str = "dev",
) -> None:
    """Configure root logger with structured JSON formatting to stdout."""
    root_logger = logging.getLogger()
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicate output
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(numeric_level)
    handler.setFormatter(
        JSONLogFormatter(service_name=service_name, environment=environment)
    )
    root_logger.addHandler(handler)

    # Suppress verbose noisy loggers if necessary
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.access").propagate = False
