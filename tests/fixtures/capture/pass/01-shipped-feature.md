---
fixture_kind: pass
scenario_summary: "User shipped an auth refactor feature for ACME_CORP; captures project + achievement + skill cluster with correct edges."
entities_proposed:
  - type: project
    slug: auth-refactor-acme-2026-05
  - type: achievement
    slug: auth-latency-cut-65pct
  - type: skill
    slug: go-lang
edges_proposed:
  - subject: auth-refactor-acme-2026-05
    predicate: produced
    object: auth-latency-cut-65pct
  - subject: auth-refactor-acme-2026-05
    predicate: uses_skill
    object: go-lang
expected_score: 4.5
expected_revisions_required: false
dimensions_failed: []
banned_phrases_hit: []
notes: |
  Synthesized composite. Placeholders only: ACME_CORP, SAMPLE_USER.
  All required fields populated with concrete values from user input.
  Two inferable edges present: produced + uses_skill.
  Semantic accuracy correct: project + achievement + skill, not topic alone.
---

**User input (capture trigger)**:

I just shipped the auth service refactor for ACME_CORP. Replaced the
session-token lookup with a Redis-backed cache. P95 auth latency dropped
from 340ms to 118ms in staging, roughly 65% cut. Used Go throughout.
Merged to main today, 2026-05-13.

---

### Writer proposal

## Proposed entities

| Field | Value | Source |
| --- | --- | --- |
| **type** | project | (classified: "shipped the auth service refactor") |
| **slug** | auth-refactor-acme-2026-05 | (derived from name + date) |
| name | auth service refactor | [source: "auth service refactor for ACME_CORP"] |
| description | Replaced session-token lookup with a Redis-backed cache to reduce auth latency. | [source: "Replaced the session-token lookup with a Redis-backed cache"] |
| year | 2026 | [source: "today, 2026-05-13"] |
| end_date | 2026-05-13 | [source: "Merged to main today, 2026-05-13"] |
| keywords | ["Redis", "Go", "auth", "caching", "performance"] | [source: "Redis-backed cache", "Used Go"] |

---

| Field | Value | Source |
| --- | --- | --- |
| **type** | achievement | (classified: quantified outcome present) |
| **slug** | auth-latency-cut-65pct | (derived from headline) |
| headline | Reduced P95 auth latency by 65% via Redis cache replacement | [source: "P95 auth latency dropped from 340ms to 118ms … roughly 65% cut"] |
| metric | P95 auth latency | [source: "P95 auth latency"] |
| delta | -65% (340ms → 118ms) | [source: "dropped from 340ms to 118ms in staging, roughly 65% cut"] |
| timeframe | 2026-05-13 | [source: "today, 2026-05-13"] |
| evidence | Measured in staging environment post-merge. | [source: "in staging"] |

---

| Field | Value | Source |
| --- | --- | --- |
| **type** | skill | (classified: explicit technology mention) |
| **slug** | go-lang | (derived from name) |
| name | Go | [source: "Used Go throughout"] |
| level | | (not stated in input) |

## Proposed edges

| Subject slug | Predicate | Object slug | Rationale |
| --- | --- | --- | --- |
| auth-refactor-acme-2026-05 | produced | auth-latency-cut-65pct | inferred: project → produced → achievement |
| auth-refactor-acme-2026-05 | uses_skill | go-lang | inferred: project → uses_skill → skill |
