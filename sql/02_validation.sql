-- Replace workspace.bronze with your configured target.
SELECT COUNT(*) AS total_rows
FROM workspace.bronze.efuse_events_zerobus;

SELECT *
FROM workspace.bronze.efuse_events_zerobus
ORDER BY event_ts DESC
LIMIT 20;

SELECT event_id, COUNT(*) AS copies
FROM workspace.bronze.efuse_events_zerobus
GROUP BY event_id
HAVING COUNT(*) > 1;
