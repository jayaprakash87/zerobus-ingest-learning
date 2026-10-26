-- Replace RUN_ID with the exact run ID printed by the benchmark.
SELECT COUNT(*) AS visible_records
FROM workspace.bronze.efuse_events_zerobus
WHERE event_id LIKE 'bench06-RUN_ID-%';

SELECT event_id, event_ts
FROM workspace.bronze.efuse_events_zerobus
WHERE event_id LIKE 'bench06-RUN_ID-%'
ORDER BY event_id;

SELECT
  split(event_id, '-')[1] AS run_id,
  COUNT(*) AS rows_received,
  COUNT(DISTINCT event_id) AS distinct_events
FROM workspace.bronze.efuse_events_zerobus
WHERE event_id LIKE 'bench06-%'
GROUP BY 1 ORDER BY 1;
