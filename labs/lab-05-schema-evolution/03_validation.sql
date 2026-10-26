-- Run after all cases; adjust catalog/schema if needed.
SELECT
 CASE
  WHEN event_id LIKE 'schema05-valid-%' THEN 'A valid'
  WHEN event_id LIKE 'schema05-missing-optional-%' THEN 'B missing optional'
  WHEN event_id LIKE 'schema05-extra-before-%' THEN 'C unexpected column before DDL'
  WHEN event_id LIKE 'schema05-extra-after-%' THEN 'D new column after DDL'
  WHEN event_id LIKE 'schema05-wrong-type-%' THEN 'E wrong type'
  WHEN event_id LIKE 'schema05-missing-required-%' THEN 'F missing required'
  ELSE 'Other'
 END AS scenario,
 COUNT(*) AS rows
FROM workspace.bronze.efuse_events_schema_lab
GROUP BY 1 ORDER BY 1;

SELECT event_id, vehicle_id, fuse_id, current_a, temperature_c, event_ts
FROM workspace.bronze.efuse_events_schema_lab
ORDER BY event_id;

SELECT COUNT(*) AS total_rows
FROM workspace.bronze.efuse_events_schema_lab;
