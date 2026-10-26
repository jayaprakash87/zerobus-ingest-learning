# Lab 02 — Send your first 10 eFuse events

**Objective:** Send 10 records over the Python Zerobus SDK and verify them in a Delta table.

Complete [Lab 01](../lab-01-setup/README.md) first.

## Step 1 — Check configuration

Verify the local `.env` is complete, the target Delta table is already present, and the service principal has table privileges. Set `ZEROBUS_EVENT_COUNT=10`.

## Step 2 — Preview events WITHOUT any network call

From the repository root:

```bash
python -m src.producer.efuse_producer --dry-run
```

This prints the exact shape of the 10 synthetic events and requires no Databricks credentials.

## Step 3 — Ingest records

```bash
python -m src.producer.efuse_producer
```

The client opens a stream, queues 10 JSON records, waits for **durability acknowledgment** of the last sent offset, and closes the stream.

## Step 4 — Validate in Databricks SQL

Open the SQL Editor. Run [sql/02_validation.sql](../../sql/02_validation.sql), after replacing the catalog/schema with your target.

To identify just this invocation, copy the generated `event_id` values printed in your terminal and filter:

```sql
SELECT * FROM workspace.bronze.efuse_events_zerobus
WHERE event_id IN ('<id-from-your-run>');
```

Expected: 10 new event IDs, with matching data types.

**Important:** Acknowledgment means the data is durable at the Zerobus service, not necessarily that the Delta table can be queried immediately. Allow for asynchronous materialization, then re-query. Avoid blindly resending records while waiting.

## Step 5 — Observe responsibilities

| Question | Observation |
|---|---|
| Did we create a Kafka broker? | No |
| Did we create a managed Delta table first? | Yes |
| Who implements the eFuse producer? | Us |
| Who authenticates the producer? | Databricks OAuth/service principal |
| Who validates incoming schema? | Zerobus |
| Who durably accepts the record? | Zerobus |
| Who materializes the record into Delta? | Zerobus |
| Who decides retry/idempotency strategy? | Our application, informed by SDK semantics |

## Troubleshooting

- **401 / unauthenticated:** incorrect client ID/secret or token flow.
- **403 / permission denied:** missing UC grants.
- **400 / invalid input:** compare JSON keys/types with target schema; don't keep retrying invalid messages.
- **Transient service errors:** investigate and retry with backoff; avoid unbounded retry loops and careless duplicate submissions.

## Cleanup

The producer uses no permanent local resources. To remove the lab's cloud data, delete the target **only after** you no longer need it for later labs:

```sql
DROP TABLE workspace.bronze.efuse_events_zerobus;
```

Next labs will explore retries, duplicates and protocol differences.
