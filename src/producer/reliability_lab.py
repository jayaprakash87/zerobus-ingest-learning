"""Lab 04: safe Zerobus acknowledgment / replay exercises.

--simulate: deterministic local demonstration, no Databricks calls.
--dry-run: print the 3 generated records, no Databricks calls.
--live: send 3 events and wait once for the final offset.
--replay-demo: intentionally send identical events twice (optional).
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from uuid import uuid4

from dotenv import load_dotenv

from src.producer.efuse_producer import required_env


def build_records(prefix: str, n: int) -> list[dict]:
    now = datetime.now(timezone.utc).isoformat()
    return [
        {
            "event_id": f"{prefix}{uuid4()}",
            "vehicle_id": f"V{200 + i}",
            "fuse_id": "F17",
            "current_a": 12.5 + i,
            "voltage_v": 12.2,
            "switch_state": 1,
            "event_ts": now,
        }
        for i in range(n)
    ]


def simulate() -> None:
    scenarios = [
        ("No write, no ack", False, False),
        ("Durable and acknowledged", True, True),
        ("Durable but ack lost", True, False),
    ]
    print("Local simulation only: no network, no Delta writes")
    for label, durable, acknowledged in scenarios:
        copies = int(durable)
        if not acknowledged:
            # Naive app-level resend, assuming the retry is durably accepted.
            copies += 1
        print(f"{label}: server_durable={durable}, client_saw_ack={acknowledged}, "
              f"copies_after_blind_replay={copies}")
    print("Moral: unknown acknowledgment != confirmed rejection.")


def send(records: list[dict]) -> None:
    # Lazy SDK import keeps local --simulate runnable without service access.
    from zerobus.sdk.shared import RecordType, StreamConfigurationOptions, TableProperties
    from zerobus.sdk.sync import ZerobusSdk

    sdk = ZerobusSdk(
        required_env("ZEROBUS_SERVER_ENDPOINT"),
        required_env("DATABRICKS_WORKSPACE_URL"),
    )
    stream = sdk.create_stream(
        required_env("DATABRICKS_CLIENT_ID"),
        required_env("DATABRICKS_CLIENT_SECRET"),
        TableProperties(required_env("ZEROBUS_TABLE_NAME")),
        StreamConfigurationOptions(record_type=RecordType.JSON),
    )
    try:
        last_offset = None
        for record in records:
            last_offset = stream.ingest_record_offset(record)
            print(f"queued event_id={record['event_id']} offset={last_offset}")
        if last_offset is not None:
            stream.wait_for_offset(last_offset)
            print(f"Durability acknowledged through offset {last_offset}")
    finally:
        stream.close()


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--simulate", action="store_true")
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--live", action="store_true")
    group.add_argument("--replay-demo", action="store_true")
    args = parser.parse_args()

    if args.simulate:
        simulate()
        return
    if args.replay_demo:
        records = build_records("replay-lab04-", 2)
        print("Intentional duplicate replay: same event IDs submitted twice.")
        for _ in range(2):
            send(records)
        return

    records = build_records("reliability-lab04-", 3)
    if args.dry_run:
        for record in records:
            print(json.dumps(record))
    else:
        send(records)


if __name__ == "__main__":
    main()
