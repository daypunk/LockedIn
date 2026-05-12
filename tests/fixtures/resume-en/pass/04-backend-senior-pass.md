---
fixture_kind: pass
persona: backend-senior
expected_score: 4.4
expected_revisions_required: false
banned_phrases_hit: []
dimensions_failed: []
notes: |
  Synthesized composite. Placeholders only (SAMPLE_USER, GLOBAL_TECH, ACME_CORP).
  Demonstrates strong persona_fit for backend-senior: distributed systems
  responsibility scope, infrastructure ownership metric, on-call evidence,
  and specific performance verbs (Owned, Architected, Hardened, Migrated).
---

## SAMPLE_USER

sample@placeholder.invalid | github.com/placeholder | Seattle, WA

---

### GLOBAL_TECH — Senior Backend Engineer (Platform Infrastructure)
*2020 – Present*

Owned the event-routing service handling ~55k RPS for 8 downstream consumers; primary on-call for the platform tier.

- Architected a dual-write migration from a legacy Cassandra cluster to CockroachDB, eliminating a single-region failure point and reducing P99 read latency from 310ms to 48ms across 3 product teams over a 9-month cutover with zero lost events.
- Hardened the circuit-breaker configuration across 12 internal gRPC services by instrumenting per-route error budgets in Prometheus; undetected cascade failures dropped from ~6/quarter to 0 in the first 6 months post-rollout.
- Reduced Kubernetes pod cold-start latency by 62% by converting the platform's runtime image from a 1.4 GB Alpine build to a distroless base with static compilation, cutting average service restart time from 22s to 8s.
- Drove the adoption of a shared Protobuf schema registry across 4 engineering teams, enforcing backward-compatibility validation in CI and preventing 3 breaking-change incidents that would have caused downstream outage.

### ACME_CORP — Software Engineer (Payments Backend)
*2017 – 2020*

- Migrated the batch settlement job from a cron-driven polling pattern to an event-driven state machine, cutting average settlement processing time from 5.5 hours to 38 minutes for a 900k daily-transaction workload.
- Instrumented distributed tracing end-to-end for the payment retry pipeline using OpenTelemetry + Jaeger, reducing mean time to diagnose production incidents from ~80 minutes to ~15 minutes.
- Eliminated a persistent memory leak in the order aggregation service by profiling heap allocation with pprof; peak RSS dropped from 4.2 GB to 1.1 GB, removing weekly OOM restarts.

---

### Skills

Go · CockroachDB · Cassandra · Kafka · Kubernetes · Terraform · Prometheus · Jaeger · OpenTelemetry
