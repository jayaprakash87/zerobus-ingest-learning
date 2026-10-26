-- Lab 04: adapt the table name if you used another learning schema.
SELECT COUNT(*) AS total_rows
FROM workspace.bronze.efuse_events_zerobus;

SELECT event_id, vehicle_id, fuse_id, event_ts
FROM workspace.bronze.efuse_events_zerobus
WHERE event_id LIKE 'reliability-lab04-%'
   OR event_id LIKE 'replay-lab04-%'
ORDER BY event_id;

SELECT
  CASE
    WHEN event_id LIKE 'reliability-lab04-%' THEN 'Reliability test'
    WHEN event_id LIKE 'replay-lab04-%' THEN 'Intentional replay demo'
    ELSE 'Earlier labs'
  END AS test_group,
  COUNT(*) AS rows_seen,
  COUNT(DISTINCT event_id) AS distinct_event_ids
FROM workspace.bronze.efuse_events_zerobus
GROUP BY 1
ORDER BY 1;

SELECT event_id, COUNT(*) AS copies
FROM workspace.bronze.efuse_events_zerobus
WHERE event_id LIKE 'replay-lab04-%'
   OR event_id LIKE 'reliability-lab04-%'
GROUP BY event_id
HAVING COUNT(*) > 1;
