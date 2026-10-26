# Zerobus ingestion mental model

```text
Application / telemetry producer
       |
       | gRPC SDK (Lab 02)
       v
Zerobus endpoint
       |
       | schema check and durable acceptance
       v
Asynchronous Delta materialization
       |
       v
Unity Catalog managed Delta table
```

Zerobus is **not** Kafka. It does not provide the same general-purpose external event-bus replay/fan-out contract. Nor does it replace application-owned event IDs, retry policies or validation.

The Delta table already exists before ingestion. Its schema is the authoritative contract. Zerobus makes accepted records durable and later queryable through materialization.

Reference: https://docs.databricks.com/aws/en/ingestion/zerobus-concepts
