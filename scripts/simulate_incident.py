"""Run simulated incident telemetry generator."""

import argparse
import time

from services.simulator.incidents import IncidentScenario
from services.simulator.telemetry import TelemetrySimulator


def run_incident_simulation(
    scenario: str, count: int = 10, interval: float = 0.5
) -> None:
    """Simulate incident telemetry output."""
    simulator = TelemetrySimulator()
    print("==================================================")
    print(f" SIMULATED INCIDENT: {scenario.upper()}")
    print("==================================================")

    for i in range(count):
        event = simulator.generate_event(scenario=scenario)
        print(
            f"[{i + 1}/{count}] {event.timestamp.isoformat()} | {event.service} | Status: {event.status_code} | Latency: {event.latency_ms}ms | CPU: {event.cpu_percent}%"
        )
        if interval > 0:
            time.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate operational incident.")
    parser.add_argument(
        "--scenario",
        default="latency_spike",
        choices=[s.value for s in IncidentScenario],
        help="Incident scenario to simulate",
    )
    parser.add_argument(
        "--count", type=int, default=10, help="Number of telemetry events"
    )
    parser.add_argument(
        "--interval", type=float, default=0.2, help="Seconds between events"
    )
    args = parser.parse_args()
    run_incident_simulation(args.scenario, args.count, args.interval)
