"""Telemetry generator for normal operations and simulated incidents."""

import random
from datetime import UTC, datetime

from services.api.app.schemas import TelemetryEvent
from services.simulator.incidents import IncidentScenario, get_scenario_parameters


class TelemetrySimulator:
    """Generates deterministic synthetic telemetry data for testing and demonstration."""

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.rng = random.Random(seed)

    def generate_event(
        self,
        service: str = "payment-api",
        endpoint: str = "/api/payment",
        scenario: IncidentScenario | str = IncidentScenario.NORMAL,
    ) -> TelemetryEvent:
        """Generate a single telemetry event modulated by the specified scenario."""
        params = get_scenario_parameters(scenario)

        base_cpu = self.rng.uniform(20.0, 35.0) * params.get("cpu_multiplier", 1.0)
        base_mem = self.rng.uniform(30.0, 45.0) * params.get("memory_multiplier", 1.0)
        base_lat = self.rng.uniform(20.0, 80.0) + params.get("latency_add_ms", 0.0)

        cpu_percent = min(max(base_cpu, 0.0), 100.0)
        memory_percent = min(max(base_mem, 0.0), 100.0)
        latency_ms = max(base_lat, 1.0)

        error_prob = params.get("error_prob", 0.01)
        if self.rng.random() < error_prob:
            status_code = self.rng.choice([500, 502, 503, 504])
        else:
            status_code = 200

        queue_depth = 10 + params.get("queue_depth_add", 0)

        return TelemetryEvent(
            timestamp=datetime.now(UTC),
            service=service,
            endpoint=endpoint,
            status_code=status_code,
            latency_ms=round(latency_ms, 2),
            cpu_percent=round(cpu_percent, 2),
            memory_percent=round(memory_percent, 2),
            request_rate=round(self.rng.uniform(10.0, 50.0), 1),
            queue_depth=queue_depth,
            deployment_version="v1.0.0",
            instance_id=f"pod-{self.rng.randint(1000, 9999)}",
            environment="dev",
            region="us-east-1",
        )


def main() -> None:
    """Run telemetry simulator continuously for demonstration."""
    simulator = TelemetrySimulator()
    print("Running Telemetry Simulator (Ctrl+C to stop)...")
    for _ in range(5):
        event = simulator.generate_event()
        print(
            f"[{event.timestamp.isoformat()}] {event.service} {event.endpoint} -> {event.status_code} ({event.latency_ms}ms)"
        )


if __name__ == "__main__":
    main()
