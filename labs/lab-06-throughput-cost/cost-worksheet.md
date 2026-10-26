# Cost and capacity observation sheet

**Do not present estimated numbers as measured Databricks prices.** Capture account-specific figures.

| Measure | Unit | Actual source / observation |
|---|---|---|
| Ingested records | count | benchmark.csv + SQL |
| Payload bytes | bytes | benchmark.csv (JSON payload only, excluding protocol overhead) |
| Zerobus billable usage | provider unit | Databricks billing/usage |
| Zerobus price | currency / billable unit | Your contract/pricing |
| Producer compute | currency | Your infrastructure |
| Network egress | currency | Source cloud/proxy |
| Delta storage | currency | Your storage billing |
| SQL validation | currency | SQL warehouse usage |

Cost per million messages = attributable total currency cost / processed records × 1,000,000.

Do not interpret a tiny 10–500 record test as statistically valid unit economics, especially where fixed overhead dominates.
