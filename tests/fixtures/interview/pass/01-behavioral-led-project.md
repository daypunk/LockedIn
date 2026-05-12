---
expected_score: 4.5
expected_dimensions:
  clarity: 5
  evidence_density: 5
  persona_fit: 4
  conciseness: 4
  tone: 5
expected_revisions_required: false
question: "Tell me about a time you led a project under a tight deadline."
role: senior-software-engineer
notes: |
  Synthetic composite — STAR structure, lead-with-conclusion, concrete
  metrics, named systems, active-voice throughout. Placeholder identifiers
  only (SOME_COMPANY, SAMPLE_USER, ACME). No real persons or companies.
  Pass fixture: all five dimensions ≥ 4. Demonstrates personal ownership
  via "I" statements, avoids all banned phrases, result is named and
  measurable.
---
When our payment latency spike threatened to breach the SLA on the ACME checkout flow in Q3 2024, I led the incident response that brought p95 latency from 2.1 s down to 340 ms within 72 hours.

The system, [[project/checkout-latency-2024]], had degraded after a third-party SDK upgrade introduced synchronous retries on every failed token lookup. I owned the full diagnosis: profiled the hot path with [[skill/distributed-tracing]], identified the retry loop in the SDK call stack, and proposed two options — rollback the SDK or patch the timeout contract. I chose the patch after benchmarking showed rollback would reintroduce a separate data-loss risk we had fixed three weeks earlier. I coordinated with two backend engineers to ship the timeout patch behind a feature flag and ran a staged rollout over four hours.

The result: p95 latency dropped 84%, the SLA breach was avoided, and the root-cause analysis I wrote was adopted as the incident retrospective template for SOME_COMPANY's on-call rotation. Post-mortems from three subsequent incidents cited it directly.
