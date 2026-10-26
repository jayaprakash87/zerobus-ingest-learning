# Lab 01 — Zerobus prerequisites and workspace setup

**Objective:** Prepare the target table and identity before attempting ingestion.

## Step 1 — Check regional availability

Zerobus availability is **region-specific**. Consult [Databricks ingestion availability](https://docs.databricks.com/aws/en/ingestion/zerobus-ingest) before proceeding. Do not guess an endpoint or pay for an unrelated messaging service.

## Step 2 — Identify your workspace URL and Zerobus endpoint

From your Databricks browser URL, record the workspace **host** without query parameters or `/o=<id>`.

The Zerobus endpoint is separate. Follow the official **Get your workspace URL and Zerobus Ingest endpoint** section linked above. A typical AWS endpoint follows:

```text
https://<workspace-id>.zerobus.<region>.cloud.databricks.com
```

Provider-specific naming can differ; follow the documentation for your cloud and region.

## Step 3 — Select destination catalog/schema

Navigate to **Catalog** / Catalog Explorer. Choose a learning catalog and schema with table-creation permissions. Examples throughout this repository use:

```text
workspace.bronze
```

Use your own catalog/schema consistently. Do not create a separate Zerobus database; the target is a regular Unity Catalog **managed Delta table**.

## Step 4 — Create the Delta table BEFORE ingestion

Open Databricks **SQL Editor** (or a SQL notebook), edit and execute [sql/01_create_table.sql](../../sql/01_create_table.sql).

Target schema:

```text
event_id         STRING
vehicle_id       STRING
fuse_id          STRING
current_a        DOUBLE
voltage_v        DOUBLE
switch_state     INT
event_ts         STRING
```

The explicit `event_id` is for detecting duplicates during reliability labs. Using a string event timestamp keeps this first ingestion simple; we can explore stricter types later.

Validate with:

```sql
DESCRIBE DETAIL workspace.bronze.efuse_events_zerobus;
```

Verify the table is **managed** and uses **DELTA**.

## Step 5 — Create a Databricks service principal

Go to **Settings → Identity and access → Service principals → Manage → Add service principal** (the exact UI wording can vary).

Create a dedicated learning identity and generate an OAuth secret. Save its **application/client ID** and **secret** locally. Never paste these into Git.

## Step 6 — Grant least-required privileges

Using an authorized SQL identity, replace the names and ID:

```sql
GRANT USE CATALOG ON CATALOG workspace TO `<application-id>`;
GRANT USE SCHEMA ON SCHEMA workspace.bronze TO `<application-id>`;
GRANT SELECT, MODIFY ON TABLE workspace.bronze.efuse_events_zerobus TO `<application-id>`;
```

Zerobus token acquisition requires the relevant table privileges for this OAuth route. Your own user also needs permission to query the table during validation.

## Step 7 — Prepare the local Python environment

Clone this repository, open a terminal in its root and run:

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a local `.env` based on [`.env.example`](../../.env.example) and set:

```text
ZEROBUS_SERVER_ENDPOINT
DATABRICKS_WORKSPACE_URL
ZEROBUS_TABLE_NAME
DATABRICKS_CLIENT_ID
DATABRICKS_CLIENT_SECRET
ZEROBUS_EVENT_COUNT=10
```

No cloud resources are created by these local commands.

## Step 8 — Preflight checklist

- [ ] Zerobus supported in the workspace region
- [ ] Endpoint and workspace URL are distinct, correctly entered values
- [ ] Managed Delta table exists, with matching columns
- [ ] Service principal exists and has the required grants
- [ ] Client ID/secret stored only locally
- [ ] SDK installed into Python environment

**Stop here if any check fails.** The next lab writes records to Databricks.

## Troubleshooting

- **Table not found:** check the three-part table name and region/workspace.
- **Permission denied:** check `USE CATALOG`, `USE SCHEMA`, `SELECT` and `MODIFY` for the service principal.
- **Unauthenticated:** check client ID, secret and endpoint values.
- **Connection failure:** check region availability, outbound firewall/proxy and hostname.

Next: [Lab 02 — Python SDK](../lab-02-python-sdk/README.md).
