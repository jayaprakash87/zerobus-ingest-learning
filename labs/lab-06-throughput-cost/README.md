# Lab 06 — Throughput, acknowledgment latency and cost

**Status:** runnable in your AWS us-east-2 environment; live performance numbers are **not** provided, because they require execution in your workspace.

## Objective

Measure separately:
- **Enqueue duration:** time to queue N JSON records into the gRPC SDK.
- **Durability duration:** time through `wait_for_offset(last_offset)`.
- **Query visibility delay:** elapsed time from durable acknowledgment until Delta SQL shows the full batch (manual SQL observations).
- **Cost:** use actual billable usage and pricing for your account, not a hardcoded per-record assumption.

**These are different metrics.** Latency measured on a laptop behind a corporate HTTP proxy is not representative of colocated production producers.

## Step 1 — Pull and activate

```bash
cd ~/zerobus-ingest-learning
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt
```

Reuse your working OAuth and endpoint configuration from Labs 01–05. Keep `ZEROBUS_TABLE_NAME=workspace.bronze.efuse_events_zerobus` for this lab (do **not** use the Lab 05 isolated schema table).

## Step 2 — Baseline in Databricks SQL

```sql
SELECT COUNT(*) AS rows_before FROM workspace.bronze.efuse_events_zerobus;
```

No table recreation or full refresh is necessary.

## Step 3 — Preview, with no network

```bash
python -m src.benchmarks.benchmark --count 10 --dry-run
```

Preview must not call Zerobus or write any local CSV.

## Step 4 — Run small capped tests

Each invocation generates a unique `run_id`; do not blindly rerun a failed request without checking what was materialized.

```bash
python -m src.benchmarks.benchmark --count 10
python -m src.benchmarks.benchmark --count 100
python -m src.benchmarks.benchmark --count 500
```

Maximum allowed per command is 1000 records to guard against unintended cost. Test sequentially, starting with 10. This is a **single gRPC stream** benchmark, not a concurrency/load test.

The output is a **local, git-ignored** `results/benchmark.csv` containing run ID, count, payload bytes, enqueue time, and durability acknowledgment time.

## Step 5 — Validate each run and visibility

Run [validation.sql](validation.sql). Replace `RUN_ID` with the printed ID:

```sql
SELECT COUNT(*)
FROM workspace.bronze.efuse_events_zerobus
WHERE event_id LIKE 'bench06-RUN_ID-%';
```

Expected row count equals the test's `--count` after materialization. Query once immediately after acknowledgment and again after a short interval, recording **when** the expected count becomes visible. SQL polling intervals, query execution time, and clock differences affect precision.

## Step 6 — Analyze responsibly

Compare results across the 10/100/500 runs. For a fair benchmark, run multiple repetitions **later**, on controlled hardware and network. Keep payload size, producer region, and load constant. Separate cold connection setup, throughput, durability barrier and Delta SQL availability.

```text
client enqueue       ≠ server durability acknowledgment
server durability    ≠ Delta query visibility
client throughput    ≠ provisioned Zerobus service quota
```

For scale, design a separate dedicated concurrency experiment with explicit quotas, budget and abort limits; do not start unbounded concurrent streams on your corporate network.

## Step 7 — Cost worksheet

Fill in [cost-worksheet.md](cost-worksheet.md) using actual Databricks usage/billing screens. The sample rows are **hypothetical**, not measured.

Cost evaluation must consider ingestion billable units/rate, producer compute, network egress, Delta storage, downstream SQL queries and any service-specific billing minimums. Do not assume a global flat price applies to your plan.

## Cleanup

Keep your target table for later labs. The script produces only local CSV artifacts under `results/` and ingests capped events. Delete local CSV if no longer needed; use event ID prefixes for filtering instead of truncating the table.

## Completion checks

- [ ] Dry run succeeded
- [ ] 10 event benchmark acknowledged and SQL-verified
- [ ] 100 event benchmark acknowledged and SQL-verified
- [ ] 500 event benchmark acknowledged and SQL-verified
- [ ] Query visibility measured separately from durability
- [ ] Actual account costs inspected
- [ ] No claim of production throughput derived from these tiny tests

Reference: [Zerobus quotas](https://docs.databricks.com/aws/en/ingestion/zerobus-quotas), [Use Zerobus Ingest](https://docs.databricks.com/aws/en/ingestion/zerobus-ingest).
