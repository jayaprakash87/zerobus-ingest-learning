# Lab 03 — Zerobus REST API vs gRPC SDK

## Goal

Send the **same eFuse event schema** to the **existing** `workspace.bronze.efuse_events_zerobus` table through two Zerobus interfaces:

- **REST:** stateless HTTPS POST, with an explicitly requested OAuth access token.
- **gRPC:** the Python SDK from Lab 02, with a persistent ingestion stream and offset acknowledgments.

No new table, Kafka broker or Lakeflow pipeline is required.

**Prerequisite:** Labs 01–02 succeeded. Your first ten records are already queryable; do not drop or reset the table.

## Architecture

```text
                    Zerobus ingest service
REST producer ──HTTP POST──────┐
                               ├── durable acceptance ──► Delta materialization
gRPC Python SDK ──gRPC stream──┘                    workspace.bronze.efuse_events_zerobus
```

## Step 1 — Pull current repository files

From the project root (the directory containing `requirements.txt`):

```bash
git pull origin main
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell use `.\.venv\Scripts\Activate.ps1` instead of `source`.

## Step 2 — Verify local configuration

Reuse your working `.env` from Lab 02:

```dotenv
ZEROBUS_SERVER_ENDPOINT=https://<workspace-id>.zerobus.us-east-2.cloud.databricks.com
DATABRICKS_WORKSPACE_URL=https://dbc-fafc8ffb-aefa.cloud.databricks.com
ZEROBUS_TABLE_NAME=workspace.bronze.efuse_events_zerobus
DATABRICKS_CLIENT_ID=<your-service-principal-application-id>
DATABRICKS_CLIENT_SECRET=<your-working-oauth-secret>
ZEROBUS_EVENT_COUNT=10
```

Add **one new variable**:

```dotenv
DATABRICKS_WORKSPACE_ID=<numeric-workspace-id>
```

Find the workspace ID in your Databricks browser URL as the numeric `o=` parameter. Do not use the `dbc-...` hostname as the ID.

The OAuth secret must permit **`all-apis`**: the earlier `sql`-scoped secret failed with 403. Never put secrets or access tokens into version control or chat.

## Step 3 — Check the destination table before sending

In Databricks SQL Editor:

```sql
SELECT COUNT(*) FROM workspace.bronze.efuse_events_zerobus;
```

Record the count. If the table has only the original Lab 02 records, expect **10**. If you've run the producer additional times, use the actual count as your baseline.

## Step 4 — Inspect exactly what the REST program will send

```bash
python -m src.producer.zerobus_rest_producer --dry-run
```

It generates **three** events with `event_id` prefixes `rest-lab03-`. It **does not call the network**.

## Step 5 — Send the three records over REST

```bash
python -m src.producer.zerobus_rest_producer
```

The program:

1. Requests an OAuth token from `<workspace-url>/oidc/v1/token` with `grant_type=client_credentials`, `scope=all-apis`, workspace-specific `resource`, and Unity Catalog `authorization_details`.
2. Sends a JSON **array** to `<zerobus-endpoint>/zerobus/v1/tables/<catalog.schema.table>/insert`.
3. Checks HTTP status and displays a concise result; it **never prints the access token or secret**.

The documented REST success response is **HTTP 200** with an empty JSON response.

If the corporate proxy prevents REST requests, collect the HTTP status/error locally and review your proxy configuration. Do not disable TLS certificate verification.

## Step 6 — Verify the REST records in Delta

In Databricks SQL Editor run:

```sql
SELECT event_id, vehicle_id, fuse_id, current_a, event_ts
FROM workspace.bronze.efuse_events_zerobus
WHERE event_id LIKE 'rest-lab03-%'
ORDER BY event_id;
```

Expected: **three rows** after asynchronous materialization.

Check:

```sql
SELECT COUNT(*) AS rest_rows
FROM workspace.bronze.efuse_events_zerobus
WHERE event_id LIKE 'rest-lab03-%';
```

Do not blindly resend because a successful HTTP response can precede SQL visibility.

## Step 7 — Send three comparable records using the gRPC SDK

The Lab 02 SDK producer already works. For this experiment we add a protocol tag and an adjustable count:

```bash
ZEROBUS_EVENT_COUNT=3 ZEROBUS_EVENT_PREFIX=grpc-lab03- \
python -m src.producer.efuse_producer
```

For Windows PowerShell:

```powershell
$env:ZEROBUS_EVENT_COUNT="3"
$env:ZEROBUS_EVENT_PREFIX="grpc-lab03-"
python -m src.producer.efuse_producer
```

The SDK opens a stream, queues events, waits for the last durability offset and closes it. This exercises a different protocol with the same target schema.

## Step 8 — Validate both paths side by side

Run [validation.sql](validation.sql).

Expected after materialization, for a **single run of each path**:

```text
REST    3 rows
gRPC    3 rows
```

The table's total count should grow by six relative to Step 3 (assuming no other writers).

## Step 9 — Compare the semantics

| Question | REST API | gRPC SDK |
|---|---|---|
| Transport | Stateless HTTP POST | Persistent gRPC stream |
| Payload in this lab | JSON array | JSON records |
| Authentication | Explicit OAuth token request | SDK performs token management |
| Success signal | HTTP 200 | Offset durability acknowledgment |
| Stream progress visible | No SDK stream offset | `ingest_record_offset`, `wait_for_offset` |
| Intended workload | Intermittent/lightweight writers | Sustained high-volume streaming |
| Materialization | Asynchronous | Asynchronous |
| Destination | Same Delta table | Same Delta table |

**This is a functional protocol comparison, not a meaningful performance benchmark.** Six small events cannot establish throughput or cost superiority.

## Common failures

- **403 `all-apis` scope not assigned:** regenerate a secret with the appropriate scope; the BI Tools `sql` scope is not sufficient.
- **403 table privileges:** check service principal entitlement and `USE CATALOG`, `USE SCHEMA`, `SELECT`, `MODIFY`.
- **404:** check the precise three-part table name.
- **400:** compare JSON column names/types with the existing table.
- **Proxy/TLS failure:** confirm corporate egress rules and configured proxy; do not bypass certificate checking.
- **200 but zero rows immediately:** materialization is asynchronous; query again before resending.

## Lab completion checklist

- [ ] New workspace ID variable configured
- [ ] Existing Delta table count recorded
- [ ] REST dry run generated three records
- [ ] REST returned HTTP 200
- [ ] REST records became queryable
- [ ] gRPC SDK sent three records and received durability acknowledgment
- [ ] Both protocol-tagged counts equal three
- [ ] Differences explained in your own words

## Next

Lab 04 — client reliability, retries and duplicate detection.

**Official sources:** [Use Zerobus Ingest](https://docs.databricks.com/aws/en/ingestion/zerobus-ingest), [API protocols](https://docs.databricks.com/aws/en/ingestion/zerobus-api-protocols).
