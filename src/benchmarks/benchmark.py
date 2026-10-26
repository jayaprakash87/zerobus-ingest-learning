"""Small, capped benchmark of gRPC SDK ingestion.

Reports client enqueue and durability barrier timing separately.
This is not a production load generator or a published Zerobus benchmark.
"""
from __future__ import annotations
import argparse
import csv
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from src.producer.efuse_producer import required_env


def make_event(run_id: str, n: int) -> dict:
    return {
        "event_id": f"bench06-{run_id}-{n}",
        "vehicle_id": f"V{123 + n % 5}",
        "fuse_id": f"F{[3, 7, 12, 17][n % 4]:02d}",
        "current_a": round(6.0 + (n % 25) / 4, 2),
        "voltage_v": 12.2,
        "switch_state": n % 2,
        "event_ts": datetime.now(timezone.utc).isoformat(),
    }


def send(run_id: str, count: int) -> dict:
    from zerobus.sdk.shared import RecordType, StreamConfigurationOptions, TableProperties
    from zerobus.sdk.sync import ZerobusSdk

    sdk = ZerobusSdk(required_env("ZEROBUS_SERVER_ENDPOINT"), required_env("DATABRICKS_WORKSPACE_URL"))
    stream = sdk.create_stream(
        required_env("DATABRICKS_CLIENT_ID"),
        required_env("DATABRICKS_CLIENT_SECRET"),
        TableProperties(required_env("ZEROBUS_TABLE_NAME")),
        StreamConfigurationOptions(record_type=RecordType.JSON),
    )
    started = time.perf_counter()
    try:
        last = None
        bytes_sent = 0
        for i in range(count):
            record = make_event(run_id, i)
            bytes_sent += len(json.dumps(record, separators=(",", ":")).encode())
            last = stream.ingest_record_offset(record)
        enqueued = time.perf_counter()
        if last is not None:
            stream.wait_for_offset(last)
        acknowledged = time.perf_counter()
    finally:
        stream.close()
    return {
        "run_id": run_id,
        "records": count,
        "payload_bytes": bytes_sent,
        "enqueue_seconds": round(enqueued - started, 5),
        "ack_seconds": round(acknowledged - started, 5),
        "records_per_ack_second": round(count / max(acknowledged - started, 1e-9), 2),
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", default="results/benchmark.csv")
    args = parser.parse_args()
    if not 1 <= args.count <= 1000:
        parser.error("count must be 1..1000; lab limits protect against accidental load/cost")
    run_id = uuid4().hex[:12]
    if args.dry_run:
        print(json.dumps({"run_id": run_id, "records": args.count,
                          "first_record": make_event(run_id, 0)}, indent=2))
        return
    summary = send(run_id, args.count)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(summary)
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        if not exists:
            writer.writeheader()
        writer.writerow(summary)
    print(json.dumps(summary, indent=2))
    print(f"Local result appended to {path}; validate table visibility separately.")


if __name__ == "__main__":
    main()
