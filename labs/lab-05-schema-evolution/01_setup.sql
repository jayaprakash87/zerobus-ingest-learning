-- Run once in Databricks SQL Editor. Adjust catalog/schema as needed.
-- Isolated Lab 05 destination; do not alter Labs 01–04 table.
CREATE TABLE IF NOT EXISTS workspace.bronze.efuse_events_schema_lab (
  event_id STRING NOT NULL,
  vehicle_id STRING NOT NULL,
  fuse_id STRING,
  current_a DOUBLE,
  event_ts STRING
) USING DELTA;

DESCRIBE TABLE workspace.bronze.efuse_events_schema_lab;
SELECT COUNT(*) AS initial_rows FROM workspace.bronze.efuse_events_schema_lab;
