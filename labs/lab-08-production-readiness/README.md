# Lab 08 — Production readiness

## Purpose

Turn the working Zerobus learning pipeline into a **reviewable production design**, without pretending that the current small Python producer is production-hardened.

## Step 1 — Separate environments and permissions

Keep dev/test/prod distinct. Use dedicated service principals, least-privilege UC table grants and secrets managed by approved secure tooling. The lab's local `.env` is **development-only**. Rotate credentials and use workload federation where supported and appropriate.

Do not place tokens, passwords, endpoint-internal addresses or personal event data in logs or Git.

## Step 2 — Define the ingestion contract

Use the existing schema including `event_id`. Specify timestamp encoding, field nullability, version compatibility, payload-size limits and producer behavior on rejected records. Adopt explicit DDL migration and compatibility procedures from Lab 05.

Specify data quality checks and quarantine/rescue policy if appropriate. The learning table's `event_id` is an application convention, **not** an automatically enforced uniqueness constraint.

## Step 3 — Define failure/retry rules

See [failure-policy.md](failure-policy.md).

- Wait for a durability acknowledgment before declaring a batch accepted.
- Let the SDK manage normal transient recovery.
- Use bounded exponential backoff + jitter only around operations it is safe to retry, guided by error classification.
- A lost acknowledgment creates an ambiguous outcome: **do not blindly replay** without stable IDs and reconciliation.
- Preserve unacknowledged records durably if business loss tolerance requires it.
- Dead-letter schema-invalid/unauthorized data (with redacted payloads) rather than infinite retries.

## Step 4 — Observability

See [operational-runbook.md](operational-runbook.md). Include:
- producer enqueue throughput;
- durable acknowledgments and timeouts;
- service errors by class (401/403/429/503);
- in-flight queue/backpressure;
- elapsed time until records are visible in the Delta table;
- end-to-end missing/duplicate `event_id` counts;
- storage/materialization delay warnings and discard events.

Do not confuse successful client enqueue with committed, queryable lakehouse records.

## Step 5 — Capacity and costs

Use Lab 06 measured client results to begin an evaluation. Repeat tests from a controlled regional producer using realistic payload size, concurrency and sustained durations. Confirm current quotas and service availability. Instrument billable usage and alert on budget.

Do not infer production readiness from a 10-record demonstration.

## Step 6 — Security and compliance review

- Identity scoped to specific tables.
- Encryption/TLS always enforced; never disable certificate checking.
- Secrets never printed or pushed to Git.
- Audit service principal grants and secret rotation.
- Data classification, retention, deletion and privacy controls established.
- Network egress and proxy behavior documented.
- Production deployment requires organizational security review.

## Step 7 — Operations and deployment

Create a runbook, incident owners, deployment rollback path, alert thresholds, support contacts, environment config and change management policy. Do not delete the destination table to fix a consumer issue.

## Production review checklist

See [release-checklist.md](release-checklist.md). Do not mark a feature validated solely because code exists. Record **local tests**, **Databricks live integration tests** and **operational sign-off** separately.

## Completion exercise

Write a concise architecture-decision record: when to use Zerobus vs Kafka, and why. Add a working production reference only after security, SLO and reliability tests are met.

References:
- [Zerobus error handling](https://docs.databricks.com/aws/en/ingestion/zerobus-errors)
- [Zerobus quotas](https://docs.databricks.com/aws/en/ingestion/zerobus-quotas)
