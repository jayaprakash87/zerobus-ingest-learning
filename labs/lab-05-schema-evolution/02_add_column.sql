-- Run ONLY after the extra-before scenario has been rejected.
ALTER TABLE workspace.bronze.efuse_events_schema_lab
ADD COLUMNS (temperature_c DOUBLE);

DESCRIBE TABLE workspace.bronze.efuse_events_schema_lab;
