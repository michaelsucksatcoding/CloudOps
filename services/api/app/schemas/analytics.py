"""Analytics response schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AnalyticsSummaryResponse(BaseModel):
    """Analytics metric summary."""

    metric_name: str
    service_id: str | None = None
    start_time: datetime
    end_time: datetime
    data_points: list[dict[str, Any]]
