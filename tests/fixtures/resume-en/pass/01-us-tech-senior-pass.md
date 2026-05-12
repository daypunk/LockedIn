---
fixture_kind: pass
persona: us-tech-senior
expected_score: 4.5
expected_revisions_required: false
banned_phrases_hit: []
dimensions_failed: []
notes: |
  Synthesized composite. Placeholders only. No real persons or companies.
  Senior backend SWE (8+ YoE) at ACME_CORP → GLOBAL_TECH.
  Metric-rich XYZ bullets. Ownership language (Owned, Architected, Drove).
  Multi-team scope visible. Two roles shown in reverse chronological order.
---

## JANE_DOE

jane@example-placeholder.invalid | github.com/placeholder | San Francisco, CA

---

### GLOBAL_TECH — Staff Software Engineer (Infra Platform)
*2021 – Present*

- Owned the distributed rate-limiting service handling ~40k RPS across 6 product teams, reducing downstream timeout errors by 78% over two quarters after migrating from a Redis-based counter to a token-bucket design backed by a dedicated Kafka topic.
- Architected a multi-region failover strategy for the core API gateway; cut P99 latency from 420ms to 95ms and reduced incident-driven rollbacks by 60% YoY by introducing progressive traffic shifting with automated canary analysis.
- Drove the deprecation of a 4-year-old monolithic job scheduler affecting 3 engineering teams; led the 6-month migration to a DAG-based orchestration layer, eliminating ~12 hours/week of manual intervention per team.
- Mentored 4 mid-level engineers through architecture review cycles; 3 were promoted to senior within 18 months of the mentorship pairing.

### ACME_CORP — Senior Software Engineer (Payments Backend)
*2017 – 2021*

- Built the idempotency layer for the payment retry pipeline, reducing duplicate-charge incidents from ~35/month to under 2/month across a 1.2M daily active transaction base.
- Reduced settlement batch processing time from 4 hours to 22 minutes by replacing a polling-based coordinator with an event-driven state machine, enabling same-day settlement for a new merchant tier.
- Led the PCI-DSS scope-reduction project that removed 14 microservices from audit scope, cutting annual compliance audit effort by ~30%.

---

### Skills

Go · Python · Kafka · PostgreSQL · Redis · Kubernetes · Terraform · Datadog
