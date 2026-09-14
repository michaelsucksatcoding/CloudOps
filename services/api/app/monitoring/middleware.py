"""Observability middleware for request correlation, latency metrics, and access logging."""

from __future__ import annotations

import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.routing import Match

from services.api.app.monitoring.logging import request_id_context
from services.api.app.monitoring.metrics import (
    HTTP_ACTIVE_REQUESTS,
    HTTP_ERRORS_TOTAL,
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_TOTAL,
)

logger = logging.getLogger("cloudops.access")


def get_route_path(request: Request) -> str:
    """Extract parameterized route path template to prevent metric cardinality explosion."""
    for route in request.app.routes:
        match, _ = route.matches(request.scope)
        if match == Match.FULL and hasattr(route, "path"):
            return str(route.path)
    return request.url.path


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Middleware for request tracking, Prometheus metric updates, and structured logging."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # 1. Establish request correlation ID
        incoming_request_id = request.headers.get("X-Request-ID")
        request_id = incoming_request_id or uuid.uuid4().hex
        token = request_id_context.set(request_id)

        method = request.method
        route_path = get_route_path(request)
        start_time = time.perf_counter()
        status_code = 500

        # 2. Track in-flight active request gauge
        HTTP_ACTIVE_REQUESTS.labels(method=method, route=route_path).inc()

        try:
            response = await call_next(request)
            status_code = response.status_code
            # Inject correlation ID into response header
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as exc:
            HTTP_ERRORS_TOTAL.labels(
                method=method, route=route_path, error_type="UnhandledException"
            ).inc()
            logger.error(
                "Unhandled error during request processing: %s",
                exc,
                extra={
                    "request_id": request_id,
                    "event": "request_error",
                    "method": method,
                    "endpoint": route_path,
                    "status_code": 500,
                },
                exc_info=True,
            )
            raise exc
        finally:
            duration_s = time.perf_counter() - start_time
            duration_ms = round(duration_s * 1000.0, 2)

            # 3. Update Prometheus metric counters and histograms
            HTTP_ACTIVE_REQUESTS.labels(method=method, route=route_path).dec()
            HTTP_REQUESTS_TOTAL.labels(
                method=method, route=route_path, status_code=str(status_code)
            ).inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=method, route=route_path
            ).observe(duration_s)

            if status_code >= 400:
                error_class = f"{status_code // 100}xx"
                HTTP_ERRORS_TOTAL.labels(
                    method=method, route=route_path, error_type=error_class
                ).inc()

            # 4. Emit structured JSON access log
            logger.info(
                "%s %s -> %d (%.2fms)",
                method,
                request.url.path,
                status_code,
                duration_ms,
                extra={
                    "request_id": request_id,
                    "event": "http_request",
                    "method": method,
                    "endpoint": route_path,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                },
            )

            # Reset context variable
            request_id_context.reset(token)
