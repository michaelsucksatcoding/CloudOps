"""Incident scenarios for simulator."""

from enum import StrEnum
from typing import Any


class IncidentScenario(StrEnum):
    """Supported deterministic incident scenarios."""

    NORMAL = "normal"
    CPU_SPIKE = "cpu_spike"
    MEMORY_PRESSURE = "memory_pressure"
    LATENCY_SPIKE = "latency_spike"
    ERROR_SPIKE = "error_spike"
    DATABASE_FAILURE = "database_failure"
    QUEUE_BACKLOG = "queue_backlog"
    DEPLOYMENT_REGRESSION = "deployment_regression"


def get_scenario_parameters(scenario: IncidentScenario | str) -> dict[str, Any]:
    """Return telemetry modulation parameters for a given incident scenario."""
    match str(scenario):
        case IncidentScenario.CPU_SPIKE:
            return {
                "cpu_multiplier": 2.8,
                "memory_multiplier": 1.1,
                "error_prob": 0.05,
                "latency_add_ms": 100.0,
            }
        case IncidentScenario.MEMORY_PRESSURE:
            return {
                "cpu_multiplier": 1.2,
                "memory_multiplier": 2.0,
                "error_prob": 0.08,
                "latency_add_ms": 150.0,
            }
        case IncidentScenario.LATENCY_SPIKE:
            return {
                "cpu_multiplier": 1.4,
                "memory_multiplier": 1.2,
                "error_prob": 0.15,
                "latency_add_ms": 1500.0,
            }
        case IncidentScenario.ERROR_SPIKE:
            return {
                "cpu_multiplier": 1.5,
                "memory_multiplier": 1.2,
                "error_prob": 0.70,
                "latency_add_ms": 300.0,
            }
        case IncidentScenario.DATABASE_FAILURE:
            return {
                "cpu_multiplier": 1.8,
                "memory_multiplier": 1.4,
                "error_prob": 0.90,
                "latency_add_ms": 2500.0,
            }
        case IncidentScenario.QUEUE_BACKLOG:
            return {
                "cpu_multiplier": 1.6,
                "memory_multiplier": 1.5,
                "error_prob": 0.10,
                "queue_depth_add": 500,
                "latency_add_ms": 600.0,
            }
        case IncidentScenario.DEPLOYMENT_REGRESSION:
            return {
                "cpu_multiplier": 1.9,
                "memory_multiplier": 1.6,
                "error_prob": 0.40,
                "latency_add_ms": 800.0,
            }
        case _:
            return {
                "cpu_multiplier": 1.0,
                "memory_multiplier": 1.0,
                "error_prob": 0.01,
                "latency_add_ms": 0.0,
            }
