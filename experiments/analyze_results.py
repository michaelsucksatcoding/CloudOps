"""Derive a compact CSV summary and SVG figures from measured raw results."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results" / "local-evaluation-results.json"


def run() -> None:
    """Write chart SVGs from the local evaluation result file."""
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    scenarios = result["ml_scenarios"]
    baseline = 300
    bars: list[str] = []
    for index, item in enumerate(scenarios):
        x = 40 + index * 105
        bar_height = item["detection_rate"] * 230
        bars.append(
            f'<rect x="{x}" y="{baseline - bar_height:.1f}" width="64" height="{bar_height:.1f}" fill="#2563eb"/>'
            f'<text x="{x + 32}" y="{baseline + 18}" text-anchor="middle" font-size="10">{item["scenario"]}</text>'
            f'<text x="{x + 32}" y="{baseline - bar_height - 6:.1f}" text-anchor="middle" font-size="11">{item["detection_rate"]:.0%}</text>'
        )
    (ROOT / "results" / "scenario-detection-rate.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="360" viewBox="0 0 900 360">'
        '<text x="20" y="28" font-size="18">Simulator scenario detection rate</text>'
        f'<line x1="30" y1="{baseline}" x2="870" y2="{baseline}" stroke="#333"/>'
        + "".join(bars)
        + "</svg>",
        encoding="utf-8",
    )
    rows = [
        "requests,p50_latency_ms,p95_latency_ms,p99_latency_ms,throughput_requests_per_second,error_rate"
    ]
    for item in result["api_performance"]:
        rows.append(",".join(str(item[key]) for key in rows[0].split(",")))
    (ROOT / "results" / "api-performance.csv").write_text(
        "\n".join(rows) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    run()
