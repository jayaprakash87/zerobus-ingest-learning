"""Lab 05 — Zerobus schema contract scenarios (one record per invocation).

Reuses Lab 03's REST OAuth implementation; do not print secrets.
Set ZEROBUS_TABLE_NAME=workspace.bronze.efuse_events_schema_lab for each run.
"""

from __future__ import annotations

import argparse
import uuid
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

from src.producer.zerobus_rest_producer import send


def make_record(case: str) -> dict:
    record = {
        "event_id": f"schema05-{case}-{uuid.uuid4()}",
        "vehicle_id": "V523",
        "fuse_id": "F17",
        "current_a": 13.2,
        "event_ts": datetime.now(timezone.utc).isoformat(),
    }
    if case == "missing-optional":
        record.pop("fuse_id")
    elif case in ("extra-before", "extra-after"):
        record["temperature_c"] = 71.5
    elif case == "wrong-type":
        record["current_a"] = "NOT_A_NUMBER"
    elif case == "missing-required":
        record.pop("vehicle_id")
    return record


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True, choices=[
        "valid", "missing-optional", "extra-before",
        "extra-after", "wrong-type", "missing-required"
    ])
    args = parser.parse_args()
    expected_rejection = args.case in {"extra-before", "wrong-type", "missing-required"}
    record = make_record(args.case)
    print(f"Scenario: {args.case}; event_id={record['event_id']}")
    try:
        send([record])
    except requests.HTTPError as exc:
        # Lab 03's send currently raises requests.HTTPError for non-2xx.
        status = exc.response.status_code if exc.response is not None else None
        body = exc.response.text if exc.response is not None else ""
        try:
            parsed = exc.response.json() if exc.response is not None else {}
        except ValueError:
            parsed = {}
        code = parsed.get("error_code", "unknown") if isinstance(parsed, dict) else "unknown"
        message = parsed.get("message", "") if isinstance(parsed, dict) else ""
        # Only display the structured service error fields; never log credentials/tokens.
        print(f"Zerobus rejected request: HTTP {status}; error_code={code}")
        if message:
            print(f"Service message: {message[:1200]}")
        elif body:
            print("Service returned a non-JSON error body; inspect privately.")
        if expected_rejection and status in (400, 422) and code == "INVALID_PARAMETER_VALUE":
            print("PASS: expected schema rejection.")
            return
        raise RuntimeError(
            f"Lab 05 case '{args.case}' failed: HTTP {status}; error_code={code}. "
            "Check service message above and current Delta table schema."
        ) from None
    if expected_rejection:
        raise RuntimeError(
            "Unexpected success: schema-invalid record was not rejected. "
            "Inspect table schema and SQL results before continuing."
        )
    print("PASS: request accepted; verify Delta materialization in SQL.")


if __name__ == "__main__":
    main()
