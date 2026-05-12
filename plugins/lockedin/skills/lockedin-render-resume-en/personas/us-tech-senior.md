# us-tech-senior

## Snapshot

Senior IC, Staff, or Principal engineer at a US tech company with 8-15 years
of experience. Scope extends beyond a single service or team: owns a platform
or technical domain that 2-4+ teams depend on, shapes technical direction
through design documents and architecture reviews, and carries on-call
accountability for critical systems. Distinct from backend-senior or
frontend-senior in that this is a broader horizontal persona covering any
engineering discipline at senior IC or staff+ level, emphasizing org-wide
influence and technical judgment over a specific stack. Targets Staff
Engineer, Principal Engineer, or Tech Lead roles at Big Tech, scaleups, or
Series C-D growth-stage companies.

## Skill cluster

Hard skills (8-12 items):
- Deep expertise in at least one primary language (Go, Java, Python, Rust,
  TypeScript) with evidence of production-scale usage
- Distributed systems design: consensus, eventual consistency, CAP
  trade-offs, at-least-once vs. exactly-once semantics
- System design at production scale: capacity modeling, traffic estimation,
  failure mode analysis
- Infrastructure ownership: Kubernetes, Terraform, or equivalent at
  operational depth
- Observability stack: metrics, logs, traces (Datadog, Prometheus, Jaeger,
  OpenTelemetry)
- Database selection and operations: SQL + NoSQL trade-offs, indexing,
  query planning
- API design: REST, gRPC, GraphQL, event-driven patterns
- Security hygiene: AuthN/AuthZ patterns, secrets management, least-privilege
  service accounts
- Performance analysis: profiling, flame graphs, load testing methodology

Soft / cross-functional skills (4-6 items):
- Technical leadership without formal authority: driving consensus on design
  decisions across teams through written proposals and structured review
- Cross-team dependency management: API contract negotiation, migration
  coordination, deprecation planning
- Mentorship of senior engineers and tech leads at scale
- Executive communication: translating technical risk and debt into
  prioritization decisions leadership can act on

## Responsibility patterns

- Owns a platform component or technical domain across multiple teams,
  acting as the de facto decision-maker for architectural changes in that
  domain.
- Authors design documents (RFCs, ADRs) that align multiple engineering
  teams on a shared technical direction, then shepherds implementation across
  team boundaries.
- Drives technical risk reduction initiatives (security hardening, dependency
  upgrades, reliability improvements) that cross team ownership boundaries.
- Mentors mid-to-senior engineers through architecture review cycles and
  design doc feedback, accelerating their growth into tech-lead scope.
- Sets and holds the technical bar for a domain: establishing SLOs,
  defining incident severity tiers, and owning post-mortems for the
  services in scope.
- Leads cross-org technical migrations (language version upgrades, framework
  migrations, infrastructure platform changes) with a phased plan and
  measurable exit criteria.
- Represents engineering in cross-functional product planning, surfacing
  technical constraints and opportunities that influence roadmap decisions.

## Tone guidance

Vocabulary register: high technicality, scope-emphasizing, ownership-forward.
Every bullet should demonstrate cross-team or org-wide impact where possible.
Scope signals (team count, traffic, revenue under management) are first-class
claims. Technical judgment (trade-off reasoning, risk decisions) is a
differentiator at this level.

Lean on: Owned, Architected, Drove, Migrated, Influenced, Defined, Led,
Reduced, Hardened, Shaped, Established, Mentored.

Avoid: "worked with", "assisted", "contributed to" (too junior), "managed
meetings" (task framing), generic scope claims without numbers.

## Action verb cluster

Owned, Architected, Drove, Migrated, Influenced, Defined, Led, Reduced,
Hardened, Shaped, Established, Mentored, Authored, Directed, Designed,
Eliminated, Accelerated, Scaled

## Banned phrases (persona-specific additions to global banned_phrases.json)

- "technical leader" without a scope signal — quantify team count, org
  footprint, or domain breadth
- "deep expertise" as a self-claim — demonstrate it with a specific system
  decision and its outcome
- "10x engineer" — self-evaluative buzzword; name the metric or scope instead
- "cutting edge technology" — claim without evidence; name the specific
  technology and why it was the right choice

## Persona fit scoring guidance

- `us-tech-senior` persona_fit >= 4 requires at least 1 scope signal (team
  count, RPS, revenue under management, on-call responsibility) AND at least
  1 influence signal (RFC authorship, cross-team migration, org-wide adoption
  of a standard).
- A resume that reads as individual-contributor feature work without org-level
  signal cannot score above 3.0.
- Staff/Principal scope (2-4+ teams for Staff; 10-30+ teams for Principal) is
  the strongest single persona_fit elevator.
- Mentorship evidence is a plus but not a gate for 4.0.

## Quality bar examples

Before: "Led backend infrastructure improvements."
After: "Architected the multi-region failover strategy for the core API
gateway serving 6 product teams, reducing incident-driven rollbacks by 60%
YoY through progressive traffic shifting with automated canary analysis."

Before: "Mentored junior engineers on the team."
After: "Mentored 4 mid-level engineers through architecture review cycles;
3 were promoted to senior within 18 months of the pairing program starting."

Before: "Worked on distributed systems at scale."
After: "Owned the distributed rate-limiting service handling ~40k RPS across
6 product teams; migrated from a Redis counter to a token-bucket design
backed by a dedicated Kafka topic, reducing downstream timeout errors by 78%."
