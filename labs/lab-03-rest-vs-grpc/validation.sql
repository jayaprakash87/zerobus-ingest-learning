-- Lab 03: use the SAME table for both protocols.
-- Change the table name if your Lab 01 target differs.

SELECT
  CASE
    WHEN event_id LIKE 'rest-lab03-%' THEN 'REST'
    WHEN event_id LIKE 'grpc-lab03-%' THEN 'gRPC SDK'
    ELSE 'Earlier labs / other'
  END AS ingestion_method,
  COUNT(*) AS records
FROM workspace.bronze.efuse_events_zerobus
GROUP BY 1
ORDER BY 1;

-- Lab 03-only rows
SELECT event_id, vehicle_id, fuse_id, current_a, voltage_v, switch_state, event_ts
FROM workspace.bronze.efuse_events_zerobus
WHERE event_id LIKE 'rest-lab03-%'
   OR event_id LIKE 'grpc-lab03-%'
ORDER BY event_id;

-- Duplicate event identifiers
SELECT event_id, COUNT(*) AS copies
FROM workspace.bronze.efuse_events_zerobus
GROUP BY event_id
HAVING COUNT(*) > 1;
