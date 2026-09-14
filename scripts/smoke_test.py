"""Automated post-deployment smoke test suite for CloudOps AI.

Validates core API health endpoints, readiness probes, and telemetry services.
Designed for execution in CI/CD pipelines (e.g. GitHub Actions) or local verification.
"""

from __future__ import annotations

import argparse
import sys
import time
from typing import Any, TypedDict

import httpx


class EndpointCheck(TypedDict):
    """Configuration for an individual endpoint health check."""

    path: str
    key: str | None
    value: Any


def test_endpoint(
    client: httpx.Client,
    url: str,
    expected_status: int = 200,
    check_json_key: str | None = None,
    expected_value: Any = None,
) -> bool:
    """Execute a single HTTP GET check with verification of status code and optional body keys."""
    try:
        response = client.get(url)
        if response.status_code != expected_status:
            print(
                f"  [FAIL] {url} returned status {response.status_code} "
                f"(expected {expected_status}): {response.text[:200]}"
            )
            return False

        if check_json_key is not None:
            data = response.json()
            actual = data.get(check_json_key)
            if expected_value is not None and actual != expected_value:
                print(
                    f"  [FAIL] {url} JSON key '{check_json_key}' was '{actual}' "
                    f"(expected '{expected_value}')"
                )
                return False

        print(f"  [PASS] {url} (HTTP {response.status_code})")
        return True
    except Exception as exc:
        print(f"  [ERROR] {url} connection failure: {exc}")
        return False


def run_smoke_tests(base_url: str, retries: int = 5, interval: float = 3.0) -> bool:
    """Execute end-to-end health and service smoke tests with retries."""
    base = base_url.rstrip("/")
    print(f"\n[SMOKE TEST] Initiating smoke verification against: {base}")

    endpoints: list[EndpointCheck] = [
        {"path": "/health/live", "key": "status", "value": "ok"},
        {"path": "/health/ready", "key": "status", "value": "ok"},
        {"path": "/health", "key": "status", "value": "ok"},
        {"path": "/services", "key": None, "value": None},
        {"path": "/metrics", "key": None, "value": None},
    ]

    with httpx.Client(timeout=10.0) as client:
        # Wait for service readiness with retries
        ready = False
        for attempt in range(1, retries + 1):
            try:
                res = client.get(f"{base}/health/live")
                if res.status_code == 200:
                    print(f"Service alive on attempt {attempt}/{retries}")
                    ready = True
                    break
            except Exception:
                pass
            print(f"Waiting for endpoint readiness (attempt {attempt}/{retries})...")
            time.sleep(interval)

        if not ready:
            print(
                f"[FAIL] Base endpoint {base}/health/live not reachable after {retries} attempts."
            )
            return False

        print("\nVerifying all target endpoints:")
        all_passed = True
        for ep in endpoints:
            target_url = f"{base}{ep['path']}"
            passed = test_endpoint(
                client=client,
                url=target_url,
                expected_status=200,
                check_json_key=ep["key"],
                expected_value=ep["value"],
            )
            if not passed:
                all_passed = False

        if all_passed:
            print("\n[SUCCESS] All smoke test validations passed successfully!\n")
        else:
            print("\n[FAILURE] One or more smoke tests failed.\n")

        return all_passed


def main() -> None:
    """CLI entry point for smoke testing."""
    parser = argparse.ArgumentParser(
        description="CloudOps AI Deployment Smoke Test Suite"
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL of target CloudOps AI API instance (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=5,
        help="Number of initial retry attempts for endpoint readiness (default: 5)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=3.0,
        help="Delay in seconds between retries (default: 3.0)",
    )
    args = parser.parse_args()

    success = run_smoke_tests(
        base_url=args.base_url,
        retries=args.retries,
        interval=args.interval,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
