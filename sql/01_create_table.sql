-- Edit catalog/schema to match your workspace before running.
-- Run in Databricks SQL with permission to create a managed table.
-- IMPORTANT: Target is a Unity Catalog managed DELTA table.

CREATE TABLE IF NOT EXISTS workspace.bronze.efuse_events_zerobus (
  event_id STRING,
  vehicle_id STRING,
  fuse_id STRING,
  current_a DOUBLE,
  voltage_v DOUBLE,
  switch_state INT,
  event_ts STRING
)
USING DELTA;

DESCRIBE DETAIL workspace.bronze.efuse_events_zerobus;
