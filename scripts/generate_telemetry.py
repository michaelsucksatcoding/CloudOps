"""Generate synthetic telemetry dataset for experiments and training."""

import argparse
import json
from pathlib import Path

from services.simulator.telemetry import TelemetrySimulator


def generate_dataset(output_path: str, count: int = 1000, seed: int = 42) -> None:
    """Generate telemetry JSON records and write to file."""
    simulator = TelemetrySimulator(seed=seed)
    events = [simulator.generate_event().model_dump(mode="json") for _ in range(count)]

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)

    print(f"Generated {count} telemetry events to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate synthetic telemetry dataset."
    )
    parser.add_argument(
        "--output",
        default="data/samples/telemetry_sample.json",
        help="Output file path",
    )
    parser.add_argument("--count", type=int, default=500, help="Number of events")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()
    generate_dataset(args.output, args.count, args.seed)
