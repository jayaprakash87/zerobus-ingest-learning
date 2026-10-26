# Lab 05 — Zerobus schema contracts and evolution

## Learning objective

Prove that **the Delta table schema defines the accepted payload**, and Zerobus **never auto-evolves** the target schema. Test optional fields, unexpected fields, explicit DDL evolution, wrong types and required fields.

We use a **separate table** `workspace.bronze.efuse_events_schema_lab` to protect the existing table from Labs 01–04.

## Architecture

```text
Python JSON producer
  → Zerobus REST interface
  → validate against destination Delta schema
  → reject incompatible records OR accept compatible records
  → asynchronous Delta materialization
```

The REST test client is adapted from the working Lab 03 implementation; credentials and endpoints are reused, not hardcoded.

## Step 1 — Update local code

```bash
cd ~/zerobus-ingest-learning
git pull origin main
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On PowerShell activate with `.\.venv\Scripts\Activate.ps1`.

## Step 2 — Create the isolated Delta table

In Databricks **SQL Editor** choose your SQL warehouse and execute [01_setup.sql](01_setup.sql). Change `workspace.bronze` if your learning catalog/schema differs.

The schema deliberately includes:

- `event_id STRING NOT NULL` — required
- `vehicle_id STRING NOT NULL` — required
- `fuse_id STRING` — optional
- `current_a DOUBLE` — optional
- `event_ts STRING` — optional

Keep the optional `temperature_c` field **absent** for now.

Verify:

```sql
DESCRIBE TABLE workspace.bronze.efuse_events_schema_lab;
SELECT COUNT(*) FROM workspace.bronze.efuse_events_schema_lab;
```

Initial expected count: `0`.

## Step 3 — Grant the existing service principal access

Run as an account with authority to grant table privileges:

```sql
GRANT SELECT, MODIFY
ON TABLE workspace.bronze.efuse_events_schema_lab
TO `<your-service-principal-application-id>`;
```

Your existing Lab 01 `USE CATALOG` / `USE SCHEMA` grants remain in effect if you use the same catalog/schema.

**Do not share the application secret.** OAuth tokens are scoped for the target table: this experiment will use the *new table name*, so any table-specific authorization details must reference it.

## Step 4 — Configure the local destination for this lab

Do **not** change the previously working `.env` permanently.

Run each experiment with a temporary environment variable override:

```bash
ZEROBUS_TABLE_NAME=workspace.bronze.efuse_events_schema_lab python -m src.producer.schema_lab --case valid
```

The Python script reads workspace URL, numeric workspace ID, Zerobus endpoint, client ID and client secret from your existing `.env`.

## Step 5 — Run each test in order

### A. Matching JSON

```bash
ZEROBUS_TABLE_NAME=workspace.bronze.efuse_events_schema_lab python -m src.producer.schema_lab --case valid
```

Expected HTTP success. Check SQL [03_validation.sql](03_validation.sql), then wait for materialization.

### B. Omit a nullable column

```bash
ZEROBUS_TABLE_NAME=workspace.bronze.efuse_events_schema_lab python -m src.producer.schema_lab --case missing-optional
```

Expected success; `fuse_id` should become `NULL`.

### C. Introduce an unknown column

```bash
ZEROBUS_TABLE_NAME=workspace.bronze.efuse_events_schema_lab python -m src.producer.schema_lab --case extra-before
```

Expected **client-side schema rejection**. The script reports the error category and treats an expected rejection as a passed test. Do not keep retrying invalid messages.

### D. Evolve the TABLE, then resend

First in Databricks SQL Editor execute [02_add_column.sql](02_add_column.sql):

```sql
ALTER TABLE workspace.bronze.efuse_events_schema_lab
ADD COLUMNS (temperature_c DOUBLE);
```

Then send:

```bash
ZEROBUS_TABLE_NAME=workspace.bronze.efuse_events_schema_lab python -m src.producer.schema_lab --case extra-after
```

Expected success. Existing rows show `NULL` for the newly added nullable column.

### E. Send a wrong type

```bash
ZEROBUS_TABLE_NAME=workspace.bronze.efuse_events_schema_lab python -m src.producer.schema_lab --case wrong-type
```

The payload sends a text value for `current_a DOUBLE`. Expected rejection.

### F. Omit a required column

```bash
ZEROBUS_TABLE_NAME=workspace.bronze.efuse_events_schema_lab python -m src.producer.schema_lab --case missing-required
```

The payload omits `vehicle_id STRING NOT NULL`. Expected rejection.

## Step 6 — Validation

Run [03_validation.sql](03_validation.sql). After one execution per successful case and materialization, expect:

| Event prefix | Count |
|---|---:|
| `schema05-valid-` | 1 |
| `schema05-missing-optional-` | 1 |
| `schema05-extra-before-` | 0 |
| `schema05-extra-after-` | 1 |
| `schema05-wrong-type-` | 0 |
| `schema05-missing-required-` | 0 |

**Total: 3 rows.** If the service responds with unexpected acceptance/rejection, record the response and inspect the SQL results before proceeding. Do not mistake an HTTP success response for immediate SQL visibility.

## Step 7 — Optional rescue-column extension

Zerobus also supports a **VARIANT rescue column** (currently Beta and JSON only). It can preserve otherwise nonconforming fields. This is a separate, opt-in feature; it is **not** auto schema evolution. We deliberately exclude it from the mandatory path to keep the contract experiment controlled.

See [Zerobus rescue column](https://docs.databricks.com/aws/en/ingestion/zerobus-rescue-column).

## Why this differs from Auto Loader

| Concept | Auto Loader / read_files | Zerobus |
|---|---|---|
| Source format | Files | Producer JSON records |
| New column behavior | Configurable schema evolution | Reject unless table permits it |
| Who changes destination schema? | May be automatic under selected modes | Table owner/admin updates it |
| Missing nullable columns | Depends on configured parser/schema | Accepted as NULL |
| Unexpected fields | Configurable rescue/evolution | Reject by default; optional rescue feature |
| Source contract | Schema inference and options | Existing target Delta schema |

## Troubleshooting

- **403 scope error:** OAuth secret must support the scope requested by the SDK/REST token flow. Lab 01's initial `sql`-scoped secret failed.
- **403 insufficient privilege:** grant `SELECT, MODIFY` on the **new lab table** and confirm the service principal's existing catalog/schema grants.
- **404:** ensure catalog, schema and table names match the temporary override.
- **New column test still fails with HTTP 400:** confirm `DESCRIBE TABLE workspace.bronze.efuse_events_schema_lab` includes `temperature_c DOUBLE`. Update your local repository; the schema lab now reports Zerobus's `error_code` and `message` without showing credentials. If the table schema matches, check the *actual message* rather than assuming metadata caching or retrying blindly. Do not rerun `ALTER TABLE` if the field already exists.
- **SQL shows 0 rows immediately:** asynchronous materialization; do not blindly replay.
- **Proxy/network error:** no TLS bypass. Check your corporate proxy's access to the Zerobus REST endpoint.

## Cleanup (after experiments)

```sql
DROP TABLE IF EXISTS workspace.bronze.efuse_events_schema_lab;
```

This affects **only** the isolated Lab 05 table; leave `efuse_events_zerobus` intact.

## Completion checklist

- [ ] New isolated table created
- [ ] Existing service principal granted table access
- [ ] Matching record accepted
- [ ] Missing optional field accepted as NULL
- [ ] Extra field rejected before ALTER TABLE
- [ ] Nullable `temperature_c` added explicitly
- [ ] New field accepted after ALTER TABLE
- [ ] Incompatible type rejected
- [ ] Missing required field rejected
- [ ] Final SQL counts verified

## Authoritative documentation

- [Schema management](https://docs.databricks.com/aws/en/ingestion/zerobus-schema-management)
- [Zerobus error handling](https://docs.databricks.com/aws/en/ingestion/zerobus-errors)
- [Delta ALTER TABLE](https://docs.databricks.com/aws/en/tables/update-schema)
