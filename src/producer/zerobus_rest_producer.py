"""Lab 03: small, safe REST example for Zerobus Ingest.

Usage:
    python -m src.producer.zerobus_rest_producer --dry-run
    python -m src.producer.zerobus_rest_producer

Uses the same table and OAuth service principal as Lab 02.
Never logs secrets or bearer tokens.
"""

from __future__ import annotations

import argparse
import os
import uuid
from datetime import datetime, timezone
from urllib.parse import quote

import requests
from dotenv import load_dotenv


def env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value or "<" in value:
        raise ValueError(f"Configure {name} in .env")
    return value


def make_records(count: int = 3) -> list[dict]:
    now = datetime.now(timezone.utc).isoformat()
    return [
        {
            "event_id": f"rest-lab03-{uuid.uuid4()}",
            "vehicle_id": f"V{123+i}",
            "fuse_id": ("F03", "F07", "F12")[i],
            "current_a": round(6.0 + i * 1.3, 2),
            "voltage_v": round(12.4 - i * .1, 2),
            "switch_state": i % 2,
            "event_ts": now,
        }
        for i in range(count)
    ]


def authorization_details(table_name: str) -> list[dict]:
    parts = table_name.split(".")
    if len(parts) != 3 or not all(parts):
        raise ValueError("ZEROBUS_TABLE_NAME must be catalog.schema.table")
    catalog, schema, _ = parts
    return [
        {
            "type": "unity_catalog_privileges",
            "privileges": ["USE CATALOG"],
            "object_type": "CATALOG",
            "object_full_path": catalog,
        },
        {
            "type": "unity_catalog_privileges",
            "privileges": ["USE SCHEMA"],
            "object_type": "SCHEMA",
            "object_full_path": f"{catalog}.{schema}",
        },
        {
            "type": "unity_catalog_privileges",
            "privileges": ["SELECT", "MODIFY"],
            "object_type": "TABLE",
            "object_full_path": table_name,
            "operations": ["zerobuswrite"],
        },
    ]


def send(records: list[dict]) -> None:
    import json

    table = env("ZEROBUS_TABLE_NAME")
    workspace = env("DATABRICKS_WORKSPACE_URL").rstrip("/")
    endpoint = env("ZEROBUS_SERVER_ENDPOINT").rstrip("/")
    workspace_id = env("DATABRICKS_WORKSPACE_ID")
    if not workspace_id.isdigit():
        raise ValueError("DATABRICKS_WORKSPACE_ID must be numeric")

    token_response = requests.post(
        f"{workspace}/oidc/v1/token",
        auth=(env("DATABRICKS_CLIENT_ID"), env("DATABRICKS_CLIENT_SECRET")),
        data={
            "grant_type": "client_credentials",
            "scope": "all-apis",
            "resource": f"api://databricks/workspaces/{workspace_id}/zerobusDirectWriteApi",
            "authorization_details": json.dumps(authorization_details(table)),
        },
        timeout=30,
    )
    token_response.raise_for_status()
    token = token_response.json().get("access_token")
    if not token:
        raise RuntimeError("OAuth response did not include access_token")

    response = requests.post(
        f"{endpoint}/zerobus/v1/tables/{quote(table, safe='.')}/insert",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        json=records,
        timeout=30,
    )
    response.raise_for_status()
    print(f"REST returned HTTP {response.status_code}; submitted {len(records)} records.")
    print("Verify them in Databricks SQL; query visibility can lag durable acceptance.")


def main() -> None:
    import json

    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    records = make_records()
    if args.dry_run:
        for record in records:
            print(json.dumps(record))
    else:
        try:
            send(records)
        except requests.HTTPError as exc:
            response = exc.response
            status = response.status_code if response is not None else "unknown"
            raise RuntimeError(
                f"REST request failed with HTTP {status}. "
                "Review authorization, table name, payload or network access."
            ) from None


if __name__ == "__main__":
    main()
