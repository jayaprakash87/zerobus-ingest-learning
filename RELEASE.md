# Zerobus Ingest Learning — v1.0.0

## Release designation

**Learning content release**, not production service certification.

Eight labs documented in execution order, with sample producers, SQL validation, safety guidance, architecture comparisons, local offline tests and CI definitions.

## CI validation

GitHub Actions `learning-repository-ci` succeeded on commit `1cabec91e04f337d86dab68a59b40c0dbab7d1b8` (run [40324507847](https://github.com/jayaprakash87/zerobus-ingest-learning/actions/runs/40324507847)). It executes Python compilation, offline tests, safe simulations, and dry-run checks without live credentials. The latest documentation-only release note update needs its own workflow result.

## Verified by learner

- AWS `us-east-2` workspace and service principal configuration.
- Lab 02: 10 sample events successfully materialized and counted in the target table.
- Lab 03: user reported REST/gRPC comparison completed.

## Not yet verified with live workspace

- Lab 04 reliability/replay behaviors.
- Lab 05 new-table schema contract scenarios.
- Lab 06 throughput and SQL visibility measures.
- Labs 07/08 decisions and operational review.
- No live Databricks integration tests run in GitHub Actions.

**Do not interpret committed code as proof that every API branch or service behavior has been tested in your workspace.**

## Supported learning environment

- Python 3.10+ recommended.
- Zerobus availability depends on cloud/region; check official service documentation.
- Existing Unity Catalog managed Delta table and dedicated OAuth service principal.
- Linux shell examples; PowerShell substitutions where relevant.
- No required paid Kafka service or long-running compute.

## Release validation commands

```bash
python -m pip install -r requirements.txt
python -m compileall -q src tests
python -m unittest discover -s tests -v
python -m src.producer.efuse_producer --dry-run
python -m src.producer.reliability_lab --simulate
python -m src.benchmarks.benchmark --count 10 --dry-run
```

Live checks must be performed in a configured Databricks workspace by an authorized learner.

## Security

No OAuth secrets, populated `.env`, access tokens, production message payloads or private credentials belong in Git. Local benchmark outputs under `results/` are ignored. Keep production readiness sign-off separate from this educational artifact.

## Known limitations

- REST examples use direct token requests rather than a shared production token cache.
- No automated live-service integration or concurrency benchmark is run in public CI.
- Cost worksheet requires account-specific data.
- Throughput results from small runs are not representative of sustained production capacity.
- Lab 05's Beta rescue-column variant is explained but not automated.

## References

- https://docs.databricks.com/aws/en/ingestion/zerobus-ingest
- https://docs.databricks.com/aws/en/ingestion/zerobus-quotas
- https://docs.databricks.com/aws/en/ingestion/zerobus-errors
