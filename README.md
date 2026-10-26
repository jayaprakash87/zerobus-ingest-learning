# Zerobus Ingest Learning

Hands-on, independent experiments with **Zerobus Ingest** on Databricks. Uses synthetic eFuse telemetry and an existing Unity Catalog managed Delta table. It complements [Lakeflow Connect Learning](https://github.com/jayaprakash87/lakeflow-connect-learning).

**Release:** v1.0.0 (learning release). All eight labs are documented; only Labs 01–03 were confirmed executed by the learner. Labs 04–08 require their own live validation. See [Release readiness](RELEASE.md).

## Learning architecture

```text
eFuse application → REST / gRPC SDK → Zerobus → Unity Catalog Delta
                                └─ durable acknowledgment ≠ immediate SQL visibility
```

## Lab sequence

| Lab | Exercise | Status |
|---|---|---|
| [01 — Setup](labs/lab-01-setup/README.md) | Workspace region, target Delta table, OAuth service principal, grants | Verified by learner |
| [02 — Python SDK](labs/lab-02-python-sdk/README.md) | 10 eFuse records, durability acknowledgment and SQL query | Verified by learner: 10 rows |
| [03 — REST vs gRPC](labs/lab-03-rest-vs-grpc/README.md) | Same data contract, two client interfaces | Reported completed |
| [04 — Reliability](labs/lab-04-reliability/README.md) | Safe simulation, durability barrier and intentional replay | Ready, not live-verified |
| [05 — Schema evolution](labs/lab-05-schema-evolution/README.md) | Explicit schema contract, rejection and DDL changes | Ready, not live-verified |
| [06 — Performance/cost](labs/lab-06-throughput-cost/README.md) | Capped record batches, acknowledgment and SQL visibility | Ready, not live-verified |
| [07 — Architecture comparison](labs/lab-07-architecture-comparison/README.md) | Zerobus vs Kafka, file ingestion and CDC | Worksheet, no infrastructure required |
| [08 — Production readiness](labs/lab-08-production-readiness/README.md) | Security, operations, SLOs, failure policy | Design exercise, not production certified |

## Quick start

Python **3.10+** recommended. Copy `.env.example` to your local `.env`, then:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m src.producer.efuse_producer --dry-run
```

On Windows use `.\.venv\Scripts\Activate.ps1`.

Live writes require workspace availability, the **actual** Zerobus endpoint, service principal credentials with an appropriate OAuth scope, and Unity Catalog permissions. Refer to Lab 01. **Never commit your populated `.env`**.

## Configuration

- `ZEROBUS_SERVER_ENDPOINT`: workspace-specific Zerobus URL (not SQL warehouse URL).
- `DATABRICKS_WORKSPACE_URL`: Databricks workspace browser base URL.
- `DATABRICKS_WORKSPACE_ID`: numeric workspace ID, needed by REST examples.
- `ZEROBUS_TABLE_NAME`: fully qualified catalog.schema.table.
- `DATABRICKS_CLIENT_ID`, `DATABRICKS_CLIENT_SECRET`: dedicated service principal.
- `ZEROBUS_EVENT_COUNT`: small test sample count; `ZEROBUS_EVENT_PREFIX` optional.

## Safety and release scope

This repo is a **learning reference**, not a certified production ingestion service. Benchmarks have a per-command 1000-record safety cap; no cloud resources are provisioned automatically. Query results, quota and cost depend on your environment. SDK/REST samples may produce duplicate business events when retried or replayed; use stable event IDs and downstream deduplication.

See [Release notes](RELEASE.md), [Architecture](docs/architecture.md), [Official Zerobus documentation](https://docs.databricks.com/aws/en/ingestion/zerobus-ingest).
