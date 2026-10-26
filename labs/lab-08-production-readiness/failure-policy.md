# Failure classification policy

| Failure | Treatment | Additional consideration |
|---|---|---|
| 401 unauthenticated | Refresh/fix credentials; bounded re-auth | Never log access token |
| 403 permission denied | Stop and fix grants | Do not retry same bad privilege configuration |
| 400 invalid schema/payload | Quarantine and fix producer/schema | Do not repeatedly retry permanent invalid data |
| 429 resource exhausted | Reduce concurrency, backoff with jitter | Apply per-client retry budget |
| 503 unavailable | Backoff with jitter | Outage SLO, durable producer-side spool if necessary |
| 500 internal | Investigate; follow Databricks guidance | Do not reflexively retry non-idempotent submission |
| Ambiguous success / timeout | Reconcile event IDs first | Duplicate deliveries are possible |
| SDK stream terminal state | SDK documented recovery sequence | Inspect unacked records; avoid bypassing internal SDK recovery |

For SDK-managed transient failures, avoid introducing an independent retry loop that sends fresh events while the SDK is already recovering.

### Application-level recovery contract

- Each source event receives a **stable** `event_id` before first transmission.
- Pending events are retained until durable acknowledgment or explicit reconciliation under the required durability SLO.
- Retried events keep the same ID and payload.
- Downstream Silver processing deduplicates by `event_id`; the Bronze table can contain duplicates.
- Operators can reconstruct a missing event set and safely trigger controlled replay.
