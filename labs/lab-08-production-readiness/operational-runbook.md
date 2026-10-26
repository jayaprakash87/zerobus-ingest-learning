# Operational runbook (template)

## Daily monitoring

Check authentication failures, ingestion ack latency, records/s, pending unacked count, materialization delay, duplicate event IDs and actual usage/cost. Set alert thresholds using service SLOs and measured baselines, not guessed numbers.

## 401 / 403

Check service principal entitlement, OAuth scope, secret expiration and UC table-specific permissions. Rotate secret as required; do not paste credentials into tickets.

## 429 / 503

Throttle/rate-limit producers, inspect service quotas, retry safely with bounded backoff+jitter and confirm acknowledged vs unknown records. Escalate sustained incidents.

## SQL count lower than acknowledged count

Materialization is asynchronous. Check pipeline/service health and delayed-data warnings before resubmission. Audit by stable event ID, not only total count.

## Duplicate event IDs

Query duplicate IDs, trace source retries. Design Silver deduplication; do not destructively remove Bronze data during an incident without an approved procedure.

## Retention and stalled materialization

The Zerobus service has a bounded durable buffer-retention period for data that cannot be materialized. Inspect warning/discard events and current [quota documentation](https://docs.databricks.com/aws/en/ingestion/zerobus-quotas). Plan operational escalation before retention limits.

## Incident evidence

Capture UTC timeline, nonsecret run ID, table name, count/offset summaries, masked error category, workspace region, relevant versions and billing identifiers. Never capture tokens or sensitive payloads unnecessarily.

## Recovery

Reconcile durable acknowledgments and queried event IDs, decide replay based on business duplicates tolerance, and confirm all expected event IDs. Log approvals.

## Ownership

Assign on-call application owner, Databricks platform owner and source-data owner before go-live.
