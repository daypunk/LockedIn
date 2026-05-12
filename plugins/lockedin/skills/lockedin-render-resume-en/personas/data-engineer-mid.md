# data-engineer-mid

## Snapshot

Mid-level data engineer with 3-6 years of experience. Owns or significantly
contributes to ETL/ELT pipelines, data warehouse modeling, and data quality
frameworks. Operates at the intersection of engineering and analytics: writes
production-grade Airflow DAGs or dbt models, manages schema evolution without
breaking downstream consumers, and takes accountability for pipeline SLAs.
Distinct from a backend-mid in that the output is queryable analytical data
rather than transactional services. Distinct from an ML engineer in that the
focus is data availability and correctness, not model training or inference.
Targets roles at companies building or maturing their data platform: from
high-growth startups normalizing their first warehouse to enterprise analytics
teams modernizing a legacy ETL estate.

## Skill cluster

Hard skills (8-12 items):
- SQL at analytical depth: window functions, lateral joins, query-plan
  interpretation, index design for OLAP queries
- dbt (Core or Cloud) — model layering (staging / intermediate / mart),
  incremental strategies, macros, packages, test coverage
- Airflow (or Prefect / Dagster) — DAG authorship, task dependencies,
  alerting, SLA miss handling
- Data warehouse: Snowflake, BigQuery, or Redshift — warehouse design,
  clustering / partitioning, cost optimization queries
- Python for pipeline orchestration and transformation logic
- Data modeling: dimensional modeling (star / snowflake schema), slowly
  changing dimensions, entity resolution
- Data quality frameworks: Great Expectations, dbt tests, anomaly detection
  on metric time series
- Git-based CI/CD for dbt and pipeline code
- Change data capture (Debezium, Fivetran, Airbyte) and event streaming
  ingestion (Kafka Connect, Kinesis Firehose)
- Column-oriented storage formats (Parquet, ORC, Delta Lake, Iceberg)

Soft / cross-functional skills (4-6 items):
- Analyst and scientist partnership: translating upstream data requests into
  pipeline contracts with explicit SLAs
- Data contract negotiation with source-system engineers (schema change
  communication protocols)
- Cost-conscious mindset: auditing warehouse slot/credit usage and proposing
  compute or storage optimizations
- Documentation culture: data dictionary maintenance, lineage annotation

## Responsibility patterns

- Designs and maintains ELT pipelines that ingest, clean, and model source
  data into warehouse-ready fact and dimension tables consumed by BI and
  analytics.
- Writes dbt models with full test coverage (not-null, unique, referential
  integrity, custom data quality assertions) and monitors test failure rates
  in CI.
- Authors and maintains Airflow DAGs with appropriate retry logic, alerting
  on SLA misses, and idempotent task design to support backfilling.
- Profiles and reduces warehouse compute costs by rewriting expensive queries,
  selecting appropriate clustering keys, and converting full-refresh models to
  incremental where data volume justifies it.
- Manages schema evolution and breaking-change communication across pipeline
  layers, maintaining a changelog and coordinating with downstream consumers
  before deploying changes.
- Implements data freshness and completeness checks that alert on-call before
  analysts surface stale or missing data to stakeholders.
- Documents data models in a data catalog or dbt docs site, including
  business-level descriptions that let analysts self-serve without escalating
  to the data engineering team.

## Tone guidance

Vocabulary register: data-platform-specific, precise, pipeline-flavored.
Bullets should name a specific tool (dbt, Airflow, Snowflake, Fivetran,
Parquet) and a concrete outcome (query runtime, pipeline SLA, warehouse cost,
test coverage rate, freshness window). Avoid server-side backend framing
for work that is fundamentally about analytical data correctness.

Lean on: Built, Reduced, Modeled, Designed, Automated, Migrated, Implemented,
Profiled, Standardized, Documented, Enforced, Shipped.

Avoid: "ETL pipeline" without specifying ELT vs. ETL and the actual tools,
"data warehouse optimization" without a cost or query-performance metric,
"worked with analysts" (masks ownership of the data contract), "big data"
(too generic and dated).

## Action verb cluster

Built, Modeled, Reduced, Automated, Migrated, Designed, Profiled, Enforced,
Standardized, Implemented, Shipped, Documented, Refactored, Established,
Instrumented, Replaced, Optimized, Deployed

## Banned phrases (persona-specific additions to global banned_phrases.json)

- "big data" — buzzword; specify the actual data volume and the tooling
- "ETL pipeline" without specifics — name the source, target, and framework
- "data-driven" — tautological in a data engineering context; remove
- "ensured data quality" — vague; describe the test framework and failure
  rate improvement
- "collaborated with stakeholders" — masks ownership; state the data contract
  or SLA you owned
- "scalable pipeline" — generic; name the volume (rows/day, GB/day) and the
  technique that made it scale
- "maintained data warehouse" — routine; replace with a specific project
  (schema migration, cost reduction, SLA improvement)

## Persona fit scoring guidance

- `data-engineer-mid` persona_fit >= 4 requires at least 1 warehouse-specific
  tool name (Snowflake, BigQuery, Redshift, dbt, Airflow) AND at least 1
  pipeline metric (volume ingested, SLA improvement, query cost reduction,
  test coverage rate, freshness window).
- A resume dominated by application-backend bullets with one line about SQL
  cannot score above 2.0.
- Evidence of data quality ownership (tests, alerts, freshness checks) is a
  strong differentiator for mid-level data engineering; its presence elevates
  persona_fit toward 4.5.
- Cost-optimization contribution (warehouse credit reduction, storage
  tiering) is a plus signal for mid-level scope.

## Quality bar examples

Before: "Maintained ETL pipelines and ensured data quality."
After: "Migrated 14 legacy Airflow DAGs to dbt incremental models, cutting
daily warehouse credit usage by 38% and reducing pipeline failure rate from
~11/week to under 2/week by adding 200+ dbt tests."

Before: "Worked with analysts to build dashboards."
After: "Modeled a star-schema fact table for order analytics (1.2B rows,
refreshed hourly) in Snowflake, reducing BI query p90 runtime from 28s to
3.1s by selecting a time-travel-compatible clustering key."

Before: "Optimized the data warehouse."
After: "Profiled 40 high-cost queries consuming ~60% of monthly Snowflake
credits; rewrote 12 with materialized staging models and query caching,
cutting the monthly bill by $18k."
