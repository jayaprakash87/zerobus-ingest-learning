# Architecture decision worksheet

Copy this table for each use case.

| Requirement | Must / nice / not needed | Evidence | Zerobus | Kafka | File Lakeflow | CDC |
|---|---|---|---|---|---|---|
| Data lands in Databricks | | | | | | |
| Independent non-Databricks consumers | | | | | | |
| Broker-level replay (days) | | | | | | |
| Source updates/deletes | | | | | | |
| Low-latency target (define number) | | | | | | |
| Recovery after hours-long outage | | | | | | |
| Security and network constraints | | | | | | |
| Budget and operations headcount | | | | | | |
| Measured unit cost | | | | | | |

Decision template:

- Scenario / business objective:
- Hard constraints:
- Recommended architecture:
- Why:
- Alternatives rejected and why:
- Empirical evidence:
- Missing evidence (not assumptions masquerading as facts):
- Failure/replay design:
- Cost components and owners:
- Open questions:
