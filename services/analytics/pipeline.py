"""Analytics ETL and data processing pipeline."""

import logging
from typing import Any

import pandas as pd

from services.analytics.feature_engineering import extract_features

logger = logging.getLogger(__name__)


class AnalyticsPipeline:
    """ETL Pipeline for batch and stream telemetry processing."""

    def run_batch_pipeline(self, raw_records: list[dict[str, Any]]) -> pd.DataFrame:
        """Process batch of raw telemetry events into analytics features."""
        if not raw_records:
            return pd.DataFrame()

        df = pd.DataFrame(raw_records)
        logger.info("Processing %d telemetry records in analytics pipeline", len(df))
        return extract_features(df)
