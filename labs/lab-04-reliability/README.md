# Lab 04 — Durability, retries, and duplicate detection

**Status: ready for self-run; not yet executed.** Builds on completed Labs 01–03 in AWS `us-east-2`.

## Learning objective

Distinguish four events: (1) record queued locally, (2) durability acknowledged, (3) record queryable in Delta, (4) application-level confirmation that a business event is unique. Zerobus SDK has **automatic transient recovery by default**, but the service provides **at-least-once**, not universal end-to-end deduplication.

We will **not** deliberately disconnect a corporate network or corrupt a working Databricks environment. Start with safe, deterministic demonstrations, then validate with three live records.

### Expected flow

```text
Application creates a stable event_id
    |
    +--> SDK queues record / assigns stream offset
    |         |
    |         +--> in-flight buffer holds unacknowledged record
    |                     |
    |                     +--> Zerobus acknowledges durable offset
    |                                      |
    |                                      +--> Delta materialization (later)
    |
    +--> application decides whether/how to replay ambiguous records
```

## Step 1 — Update your local checkout

From repo root:

```bash
git pull origin main
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Use `.\.venv\Scripts\Activate.ps1` instead of `source` on PowerShell.

Reuse your working `.env`. It must include `ZEROBUS_SERVER_ENDPOINT`, `DATABRICKS_WORKSPACE_URL`, `ZEROBUS_TABLE_NAME`, `DATABRICKS_CLIENT_ID`, `DATABRICKS_CLIENT_SECRET`. **Never commit or share credentials.**

## Step 2 — Record the baseline in Databricks SQL

Go to **SQL Editor**, select a SQL warehouse and run:

```sql
SELECT COUNT(*) AS rows_before FROM workspace.bronze.efuse_events_zerobus;
```

Record your actual result. The original Lab 02 had 10 rows; Lab 03 may have added 6. Other earlier tests may make your baseline larger.

## Step 3 — Simulate ambiguous acknowledgment with ZERO network calls

```bash
python -m src.producer.reliability_lab --simulate
```

This simulates three possibilities: no acknowledgment and no write, successful acknowledgment, and **a durable record whose acknowledgment was lost**. It shows why blind replay can create two copies with the same `event_id`.

No Databricks data is written in this step.

## Step 4 — Live chunk durability test (3 new records)

Preview first:

```bash
python -m src.producer.reliability_lab --dry-run
```

Then ingest:

```bash
python -m src.producer.reliability_lab --live
```

What the program does:

1. Generates **three** records with unique `event_id` values beginning `reliability-lab04-`.
2. Creates the same JSON SDK stream used in Lab 02.
3. Calls `ingest_record_offset()` on each record.
4. Calls `wait_for_offset()` **only for the final offset**.
5. Closes the stream in `finally`, performing a graceful flush.

This tests acknowledgment of a **chunk**, not a separate round trip for each record. Waiting on the last offset is the recommended efficient approach. Automatic transient recovery is an SDK feature and need not be manually implemented. See [Message blocking and acknowledgment](https://docs.databricks.com/aws/en/ingestion/zerobus-message-blocking) and [Recovery patterns](https://docs.databricks.com/aws/en/ingestion/zerobus-recovery).

**Important:** The live test does not induce an outage; it verifies the happy-path durability barrier. Network recovery under a fault is **not** proven by a successful run.

## Step 5 — Inspect the output

Run [validation.sql](validation.sql) in Databricks SQL Editor. The count of `reliability-lab04-%` records should be **3** after asynchronous materialization on the first execution.

If the total does not change immediately after durability acknowledgment, requery later. **Do not blindly run the command again**; each execution generates new event IDs, so rerunning it adds more records.

If you ran the lab multiple times, compare each printed `event_id` with SQL rather than expecting exactly three total prefixed rows.

## Step 6 — Controlled replay to observe duplicates (optional)

This step **intentionally inserts duplicates** into your learning table; do it only if you're comfortable with that. It is not necessary to pass the lab.

1. Use the optional explicit replay mode:

   ```bash
   python -m src.producer.reliability_lab --replay-demo
   ```

2. The program writes the **same two events with stable IDs** in two separate acknowledged streams.
3. Query `validation.sql` to find `replay-lab04-%` event IDs with `COUNT(*) > 1`.

This is an application replay demonstration, **not evidence that the SDK's built-in recovery duplicated records**. It proves that blindly submitting the same business event again can cause duplicate business records. Keep this optional demo isolated to the learning table.

## Step 7 — Understand transient vs permanent failure

| Case | SDK behavior | Application behavior |
|---|---|---|
| Brief network interruption | Attempts built-in recovery | Observe errors/metrics; avoid competing manual retries |
| Graceful close | Flushes pending records | Close in `finally` |
| Invalid credentials / revoked permission | Non-retriable error | Fix identity/permissions; don't loop indefinitely |
| Ambiguous acknowledgment | No reliable external visibility without reconciliation | Preserve stable event ID; reconcile before replay |
| Terminal stream failure with unacknowledged records | SDK exposes recovery APIs | Preserve/replay unacknowledged records per documented sequence |

For genuine terminal failures, see official [Recovery and retry patterns](https://docs.databricks.com/aws/en/ingestion/zerobus-recovery). The Python SDK supports `get_unacked_records()` and `recreate_stream()` **under specific closed/failed-stream conditions**. Do not invoke them indiscriminately on an active stream; follow the SDK's error-state rules.

## Step 8 — What "exactly once" would require

Zerobus provides **at-least-once delivery semantics**. A stable `event_id` enables downstream **business-event deduplication**, for example a Silver table choosing one record per event ID; it does not make the Bronze table automatically unique.

An idempotent downstream pattern uses `event_id` as a deduplication key and records recovery decisions. A primary key-like field in an ordinary Delta table alone is not a universal enforced uniqueness guarantee.

## Completion checklist

- [ ] Baseline SQL count recorded
- [ ] Failure/acknowledgment simulation understood
- [ ] Live dry-run checked
- [ ] Three new records successfully acknowledged
- [ ] Records queryable in Delta
- [ ] Understood that acknowledgment != immediate SQL visibility
- [ ] Understood SDK auto-recovery vs application replay
- [ ] (Optional) Replay demonstration and duplicate check

## Success criteria

You can explain **queued vs durable vs queryable**, why automatic retry exists, why lost acknowledgments can be ambiguous, why business deduplication is separate, and why the SDK should own transient reconnection rather than a homemade retry loop.

Next: **Lab 05 — Schema contracts and evolution.**
