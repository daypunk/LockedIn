# backend-senior

## Snapshot

Senior backend engineer at scaleups or Big Tech. Typically 7-12 years of
experience owning services that handle significant production traffic. Scope
extends beyond a single service — this person carries on-call pager weight,
drives cross-team dependency decisions, and regularly authors or reviews
architecture proposals. Distinct from `us-tech-senior` (which is a broad
senior IC catch-all) in that backend-senior foregrounds distributed systems
thinking, infrastructure operations, and systems performance explicitly.
Targets companies where the backend complexity is the product challenge:
high-throughput APIs, large-scale data pipelines, distributed coordination,
multi-region deployments.

## Skill cluster

Hard skills (8-12 items):
- Go, Java, Rust, or Python at systems-programming depth
- gRPC / Protobuf
- Kafka or another durable message broker
- PostgreSQL / CockroachDB / distributed SQL at production tuning depth
- Kubernetes — not just deployment, but capacity planning and pod lifecycle
- Distributed tracing (Jaeger, OpenTelemetry)
- Infrastructure-as-code (Terraform, Pulumi)
- Redis — caching, pub/sub, rate-limiting patterns
- Load testing and capacity modeling
- Service mesh basics (Envoy, Istio, or Linkerd)
- Circuit-breaking, bulkhead, and back-pressure patterns
- Container image hardening and supply-chain hygiene

Soft / cross-functional skills (4-6 items):
- On-call ownership — writing runbooks, hosting post-mortems, tightening SLOs
- Technical mentorship of mid-level engineers through architecture review
- Cross-team dependency negotiation (API contracts, SLA discussions)
- Incident command and escalation judgment
- Design-doc authorship and structured decision-making (ADRs)

## Responsibility patterns

- Designs and owns distributed services from initial RFC through production
  operation, including on-call rotation and SLO accountability.
- Benchmarks and tunes service performance at the component level (query
  plans, serialization hot paths, GC tuning) and at the network level
  (connection pooling, retry budgets, backoff strategies).
- Drives service decomposition or consolidation decisions that affect two or
  more teams, authoring the design doc, facilitating review, and shepherding
  the migration.
- Instruments services end-to-end: structured logging, distributed traces,
  custom business metrics; writes runbooks that let on-call engineers
  diagnose incidents without requiring the author's presence.
- Leads the cross-team effort to define data contracts (Protobuf schemas,
  Avro, JSON Schema) and enforces backward-compatibility policies across the
  API surface.
- Reduces infrastructure cost by right-sizing services, profiling memory
  allocation patterns, or replacing polling with event-driven patterns.
- Reviews architecture proposals from mid-level engineers and provides
  structured written feedback that addresses correctness, operability, and
  long-term maintenance burden.

## Tone guidance

Vocabulary register: high technicality, terse, infra-flavored. Every claim
should name a specific technology or measurable outcome. Prose should read
like an architecture RFC abstract — confident, direct, no hedging.

Lean on: Owned, Architected, Hardened, Migrated, Instrumented, Profiled,
Decomposed, Enforced, Modeled, Reduced, Eliminated.

Avoid: "helped the team", "worked alongside", soft verbs that obscure
ownership ("supported", "contributed to"), managerial framing ("organized
meetings", "managed relationships"), and vague tech references ("cloud
services", "modern infrastructure", "various tools").

## Action verb cluster

Architected, Owned, Hardened, Migrated, Instrumented, Profiled, Eliminated,
Reduced, Decomposed, Enforced, Modeled, Benchmarked, Designed, Drove, Scaled,
Automated, Replaced, Shipped

## Banned phrases (persona-specific additions to global banned_phrases.json)

- "scalable solutions" — generic claim; replace with a named pattern and a
  throughput or latency metric
- "robust architecture" — too vague; name the specific resilience mechanism
- "highly available" — acceptable only when paired with a measured SLA target
- "cloud-native" — architecture buzzword; describe the actual design decision
- "best practices" — filler; cite the specific practice and its measurable
  effect
- "performance improvements" — quantify: latency percentile, throughput
  change, error-rate delta
- "worked closely with" — masks ownership; state what you owned and decided

## Persona fit scoring guidance

- `backend-senior` persona_fit >= 4 requires at least 2 distributed-systems
  verb anchors (Owned, Architected, Migrated, Decomposed, Hardened) and at
  least 1 concrete scope signal (RPS count, number of downstream consumers,
  on-call rotation, SLO target).
- A resume with only CRUD API bullets and no latency, throughput, or
  reliability metrics cannot score above 3.0 on persona_fit for this persona.
- Infrastructure ownership evidence (on-call, runbook authorship, SLO
  accountability) must appear somewhere in the experience section for a 4.0
  or above.
- Mentorship of mid-level engineers is a plus signal for senior scope but is
  not a gate; its absence does not prevent a 4.0.
- References to team size must accompany scope claims: "owned the service" is
  weaker than "owned the service; team of 3 on-call engineers".

## Quality bar examples

Before: "Improved service performance and reliability across the platform."
After: "Hardened the core API gateway's retry budget, cutting cascading-
failure incidents from ~8/month to 1/month across 4 downstream services."

Before: "Worked with the infrastructure team on Kubernetes migration."
After: "Migrated 18 services from VM-based deployments to Kubernetes, reducing
per-service provisioning time from 3 days to under 20 minutes and cutting
idle-resource cost by 41%."

Before: "Built scalable backend services."
After: "Architected the order-routing service to handle 22k RPS at p99 < 80ms
using a token-bucket rate limiter backed by Redis Cluster, eliminating the
queue-depth spikes that previously caused checkout timeouts at peak."
