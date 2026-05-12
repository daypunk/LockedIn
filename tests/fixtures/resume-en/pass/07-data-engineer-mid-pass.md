---
fixture_kind: pass
persona: data-engineer-mid
expected_score: 4.3
expected_revisions_required: false
banned_phrases_hit: []
dimensions_failed: []
notes: |
  Synthesized composite. Placeholders only (JANE_DOE, SOME_COMPANY, BLUE_LABS).
  Demonstrates strong persona_fit for data-engineer-mid: dbt model migration
  with test coverage evidence, Airflow SLA metrics, Snowflake cost reduction
  with dollar delta, and pipeline freshness monitoring. Tool mentions: dbt,
  Airflow, Snowflake, Fivetran. Verbs: Migrated, Reduced, Modeled, Built,
  Automated, Profiled, Established.
---

## JANE_DOE

jane@placeholder.invalid | github.com/placeholder | Chicago, IL

---

### SOME_COMPANY — Data Engineer
*2022 – Present*

Owned ELT pipelines powering 3 BI dashboards consumed by 40+ analysts; primary contact for data quality SLA discussions with the analytics team.

- Migrated 11 legacy SQL-based ETL scripts to dbt incremental models with 180 data quality tests (not-null, unique, referential integrity, custom freshness assertions), reducing pipeline failure rate from ~9/week to under 1/week and cutting daily Snowflake credit consumption by 32%.
- Modeled a customer-lifetime-value fact table in a star schema (800M rows at peak) using Snowflake clustering on account_id and event_date; BI query p90 runtime dropped from 34s to 4.2s, eliminating analyst escalations about dashboard load time.
- Automated Airflow SLA monitoring with PagerDuty integration, paging on-call when any high-priority DAG missed its SLA window by more than 15 minutes; average time-to-alert for SLA misses dropped from ~3 hours to 8 minutes.
- Profiled 25 high-credit-cost queries consuming 55% of monthly Snowflake spend; rewrote 8 with materialized staging CTEs and appropriate clustering, reducing monthly warehouse cost by $22k over two quarters.

### BLUE_LABS — Junior Data Engineer
*2021 – 2022*

- Built the Fivetran-to-Snowflake ingestion pipeline for 6 SaaS source systems, implementing change-data-capture patterns that reduced full-refresh runs from nightly to incremental-every-4-hours and cutting ingestion lag from 24h to under 30 minutes.
- Established the dbt project's staging-intermediate-mart layer convention, improving model discoverability and onboarding time for 2 new data engineering hires.

---

### Skills

dbt (Core) · Airflow · Snowflake · Fivetran · Python · SQL · Parquet · GitHub Actions · PagerDuty
