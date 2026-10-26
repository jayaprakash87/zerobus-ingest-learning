# Zerobus Ingest — Hands-on Learning

A small, reproducible learning project exploring how producers **push events directly to Databricks Delta tables** using Zerobus Ingest.

Uses the synthetic eFuse telemetry model from [Lakeflow Connect Learning](https://github.com/jayaprakash87/lakeflow-connect-learning), but remains an independent repository.

## Start here

1. [Lab 01 — Setup](labs/lab-01-setup/README.md) — availability, table, identity, endpoint.
2. [Lab 02 — Python SDK](labs/lab-02-python-sdk/README.md) — send 10 events, wait for durability acknowledgments, query the Delta table.

Later labs (planned; not yet implemented): REST vs gRPC; retries and recovery; schema contracts; throughput and cost; Kafka comparison; production design.

## Learning architecture

```text
Python eFuse producer
        │
        ▼
Zerobus gRPC endpoint
        │
        ▼
Durable ingestion and asynchronous materialization
        │
        ▼
Unity Catalog managed Delta table
```

**Important:** A successful durability acknowledgment is not identical to immediate SQL query visibility.

## Getting started

- Python 3.9+
- Zerobus available in your Databricks workspace region
- A Unity Catalog managed Delta table (create it before sending data)
- Databricks service principal with `USE CATALOG`, `USE SCHEMA`, `SELECT`, and `MODIFY` grants
- OAuth client ID and secret, kept out of Git

See [Lab 01](labs/lab-01-setup/README.md), then [Lab 02](labs/lab-02-python-sdk/README.md).

## Official reference

[Databricks — Use Zerobus Ingest](https://docs.databricks.com/aws/en/ingestion/zerobus-ingest)

## Safety and cost

Run small samples and inspect your Databricks billing. This repository does not create cloud resources automatically. Never commit OAuth client secrets, access tokens or populated `.env` files.
