# Lab 07 — Zerobus vs Kafka vs Lakeflow Connect

## Objective

Make an architecture decision, not a marketing comparison. Reuse the same synthetic eFuse schema and business requirements from the [Lakeflow Connect Learning](https://github.com/jayaprakash87/lakeflow-connect-learning) repository.

## The three architectures

```text
A. Zerobus push
eFuse application → Zerobus → Unity Catalog Delta table

B. Kafka event backbone
eFuse application → Kafka broker → Kafka connector → Delta table
                        └────→ independent consumer (alerts, operational systems)

C. File-based Lakeflow ingestion
eFuse application → files in object storage → Lakeflow ingestion → Delta table
```

PostgreSQL CDC is a fourth pattern: operational database → WAL/logical replication → CDC → Delta.

## Step 1 — Define your requirements

Fill in [decision-worksheet.md](decision-worksheet.md) *before* looking at the comparison matrix. Example cases:

- **Case A:** telemetry only needs to land in the lakehouse, low-latency, with no independent operational consumers.
- **Case B:** same telemetry must feed a real-time alerting system, a customer API and the lakehouse; consumers need independent replay.
- **Case C:** a vendor exports daily archives to object storage.
- **Case D:** a PostgreSQL operational table must synchronize updates and deletes.

## Step 2 — Map interface ownership

| Concern | Zerobus | Kafka + Lakeflow | Incremental files | PostgreSQL CDC |
|---|---|---|---|---|
| Producer integrates with | Zerobus SDK/REST | Kafka producer | Object storage | Database |
| Independent message broker | Not required | Required | Not required | Not required |
| Fan-out to non-lakehouse consumers | Not an event bus | Strong native fit | Downstream orchestration | Source-specific |
| Source replay retention | Not a general-purpose log | Kafka retention | Retained original files | Database WAL/slot; retention constraints |
| Source capture | Application push | Producer publish | File discovery | Database change log |
| Delete/update capture | App design | Event design | File semantics | CDC protocol |
| Authentication | OAuth + UC grants | Broker security + connector | Cloud/source connection | DB replication + connector |
| Destination | UC managed Delta table | UC Delta via connector | UC Delta via connector | UC Delta via connector |
| State/recovery owner | SDK + Zerobus + app-level reconciliation | Kafka + consumer/checkpoint | File discovery checkpoint | CDC gateway/replication |
| Primary operational risks | Producer retries, duplicate events, producer coupling to Databricks | Broker operations, retention, lag | File immutability, late arrivals | WAL retention, network, replication slot |
| Typical fit | Lakehouse-first direct ingestion | Independent event platform | Batch/periodic files | Database row-change sync |

## Step 3 — Run one evidence-based comparison

For your workspace, use **actual outcomes** from the Zerobus labs; do **not** invent missing Kafka benchmark data.

Create a small evidence sheet:

| Fact | Zerobus measured | Kafka measured | Notes |
|---|---|---|---|
| First 10 records ingested | Yes (Lab 02) | Run Lab 06 Kafka before filling | |
| REST vs gRPC functional | Yes (Lab 03) | N/A | |
| Durability acknowledgment behavior | Lab 04 | Inspect broker ack + sink commit separately | |
| End-to-end latency | Record from Lab 06 | Not measured unless Kafka actually deployed | |
| Cost | Account billing | Kafka + connector + network bill | |
| Recovery/duplicates | Lab 04 | Kafka offsets + consumer semantics | |

## Step 4 — Score the requirements

Use [decision-worksheet.md](decision-worksheet.md). Score architectures only against **explicitly assigned requirements**; do not make performance or price claims without comparable measurements.

A transparent decision rule:
- Choose **Zerobus** when the data's primary consumer is Databricks, producers can authenticate/communicate with it, and broker-level fan-out/replay is not required.
- Choose **Kafka** when an independent event distribution layer, multiple consumer groups or time-bounded broker replay is essential.
- Choose **object-storage + Lakeflow** for periodic/immutable file deliveries.
- Choose **CDC** for row-level operational database changes.

## Step 5 — Failure and cost review

Discuss an unavailable destination:
- Zerobus clients need backpressure/buffering/failure policies and service-specific retention awareness.
- Kafka producers/consumers can be decoupled by topic retention, subject to broker availability and retention/size limits.
- File producers can publish immutable objects even while Databricks pipelines are stopped.
- Database CDC source WAL must be consumed before retention/disk risks accumulate.

Compare **total cost of ownership**: brokers, connector compute, network traffic, client compute, operational staffing, retention and Delta storage. No absolute winner can be asserted without figures.

## Exercise and acceptance

Document a 1-page recommendation for each case with *assumptions, rejected alternatives, risk and mitigation*. Mark unknown figures explicitly. This lab does not provision Kafka infrastructure and does not require a paid Kafka account.

- [ ] Defined case requirements first
- [ ] Selected one architecture per case
- [ ] Used only observed metrics
- [ ] Captured independent consumer/replay requirements
- [ ] Captured failures, costs, security and data governance
- [ ] Explained why Zerobus is not simply a Kafka replacement

References:
- [Zerobus interfaces](https://docs.databricks.com/aws/en/ingestion/zerobus-ingest)
- [Zerobus quotas](https://docs.databricks.com/aws/en/ingestion/zerobus-quotas)
