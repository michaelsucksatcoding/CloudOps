"""Tests for telemetry simulator and incident modulation."""

from services.simulator.incidents import IncidentScenario, get_scenario_parameters
from services.simulator.telemetry import TelemetrySimulator


def test_simulator_normal_event() -> None:
    """Verify normal telemetry generation adheres to schema and expected ranges."""
    simulator = TelemetrySimulator(seed=100)
    event = simulator.generate_event(scenario=IncidentScenario.NORMAL)
    assert event.service == "payment-api"
    assert event.status_code == 200
    assert 0.0 <= event.cpu_percent <= 100.0
    assert 0.0 <= event.memory_percent <= 100.0


def test_simulator_incident_modulation() -> None:
    """Verify latency spike scenario elevates response latency."""
    simulator = TelemetrySimulator(seed=200)
    event = simulator.generate_event(scenario=IncidentScenario.LATENCY_SPIKE)
    assert event.latency_ms > 1000.0


def test_scenario_parameters() -> None:
    """Verify all scenarios return expected parameter dictionary."""
    for scenario in IncidentScenario:
        params = get_scenario_parameters(scenario)
        assert "cpu_multiplier" in params
        assert "memory_multiplier" in params
        assert "error_prob" in params
