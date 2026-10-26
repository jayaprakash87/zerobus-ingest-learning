"""Minimal Zerobus JSON producer for synthetic eFuse events.

Run without network: python -m src.producer.efuse_producer --dry-run
Run with configured Zerobus endpoint: python -m src.producer.efuse_producer
"""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from uuid import uuid4

from dotenv import load_dotenv


def make_records(count: int) -> list[dict]:
    now = datetime.now(timezone.utc).isoformat()
    return [
        {
            "event_id": f"{os.getenv('ZEROBUS_EVENT_PREFIX', '')}{uuid4()}",
            "vehicle_id": f"V{123 + (i % 5)}",
            "fuse_id": f"F{(3, 7, 12, 17)[i % 4]:02d}",
            "current_a": round(6.0 + i * 1.3, 2),
            "voltage_v": round(12.4 - (i % 4) * 0.1, 2),
            "switch_state": i % 2,
            "event_ts": now,
        }
        for i in range(count)
    ]


def required_env(key: str) -> str:
    value = os.getenv(key, "").strip()
    if not value or "<" in value:
        raise ValueError(f"Set {key} in your local .env file")
    return value


def main() -> None:
    import json

    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Print records without connecting")
    args = parser.parse_args()

    count = int(os.getenv("ZEROBUS_EVENT_COUNT", "10"))
    if not 1 <= count <= 1000:
        raise ValueError("ZEROBUS_EVENT_COUNT must be between 1 and 1000")
    records = make_records(count)
    if args.dry_run:
        for record in records:
            print(json.dumps(record))
        return

    # Import lazily: dry-run works without installing the Databricks SDK.
    from zerobus.sdk.sync import ZerobusSdk
    from zerobus.sdk.shared import RecordType, StreamConfigurationOptions, TableProperties

    sdk = ZerobusSdk(
        required_env("ZEROBUS_SERVER_ENDPOINT"),
        required_env("DATABRICKS_WORKSPACE_URL"),
    )
    options = StreamConfigurationOptions(record_type=RecordType.JSON)
    stream = sdk.create_stream(
        required_env("DATABRICKS_CLIENT_ID"),
        required_env("DATABRICKS_CLIENT_SECRET"),
        TableProperties(required_env("ZEROBUS_TABLE_NAME")),
        options,
    )
    try:
        final_offset = None
        for record in records:
            final_offset = stream.ingest_record_offset(record)
            print(f"queued event_id={record['event_id']} offset={final_offset}")
        if final_offset is not None:
            stream.wait_for_offset(final_offset)
            print(f"Durability acknowledged through offset {final_offset}")
    finally:
        stream.close()


if __name__ == "__main__":
    main()
