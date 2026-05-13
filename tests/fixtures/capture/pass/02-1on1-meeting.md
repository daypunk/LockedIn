---
fixture_kind: pass
scenario_summary: "User logged a 1:1 with their manager at GLOBAL_TECH; captures meeting + person + decision with correct edges."
entities_proposed:
  - type: meeting
    slug: 1on1-manager-global-tech-2026-05-12
  - type: person
    slug: manager-global-tech
  - type: decision
    slug: focus-on-infra-platform-q2-2026
edges_proposed:
  - subject: manager-global-tech
    predicate: attended
    object: 1on1-manager-global-tech-2026-05-12
  - subject: 1on1-manager-global-tech-2026-05-12
    predicate: made
    object: focus-on-infra-platform-q2-2026
expected_score: 4.5
expected_revisions_required: false
dimensions_failed: []
banned_phrases_hit: []
notes: |
  Synthesized composite. Placeholders only: GLOBAL_TECH, SAMPLE_USER, MANAGER_NAME.
  All required fields populated: meeting.title, person.name, decision.headline.
  Two inferable edges present: attended (person→meeting) and made (meeting→decision).
  Semantic accuracy correct: meeting (extended definition) + person + decision.
---

**User input (capture trigger)**:

Logged my weekly 1:1 with MANAGER_NAME at GLOBAL_TECH yesterday (2026-05-12).
45 minutes. We agreed I'll spend Q2 focused on the infra platform team's
reliability work rather than the product surface. MANAGER_NAME confirmed
this changes my H1 goals — reliability OKR now primary. Next 1:1 in two weeks.

---

### Writer proposal

## Proposed entities

| Field | Value | Source |
| --- | --- | --- |
| **type** | meeting | (classified: "1:1 with MANAGER_NAME") |
| **slug** | 1on1-manager-global-tech-2026-05-12 | (derived from type + date) |
| title | Weekly 1:1 with MANAGER_NAME at GLOBAL_TECH | [source: "weekly 1:1 with MANAGER_NAME at GLOBAL_TECH"] |
| date | 2026-05-12 | [source: "yesterday (2026-05-12)"] |
| duration_minutes | 45 | [source: "45 minutes"] |
| agenda | ["Q2 focus alignment", "H1 goal update"] | [source: "focused on the infra platform … changes my H1 goals"] |
| summary | Agreed to shift Q2 focus to infra platform reliability; H1 reliability OKR becomes primary goal. | [source: "We agreed I'll spend Q2 focused on the infra platform team's reliability work … reliability OKR now primary"] |

---

| Field | Value | Source |
| --- | --- | --- |
| **type** | person | (classified: named individual mentioned) |
| **slug** | manager-global-tech | (derived from role + org) |
| name | MANAGER_NAME | [source: "MANAGER_NAME at GLOBAL_TECH"] |
| current_role | | (not stated in input) |

---

| Field | Value | Source |
| --- | --- | --- |
| **type** | decision | (classified: "We agreed … MANAGER_NAME confirmed") |
| **slug** | focus-on-infra-platform-q2-2026 | (derived from headline) |
| headline | Shift Q2 focus to infra platform reliability; reliability OKR becomes primary H1 goal | [source: "We agreed I'll spend Q2 … reliability OKR now primary"] |
| date | 2026-05-12 | [source: "2026-05-12"] |
| context | Weekly 1:1 with manager; previously on product surface work. | [source: "rather than the product surface"] |
| rationale | Manager confirmed the shift aligns with team Q2 reliability objectives. | [source: "MANAGER_NAME confirmed this changes my H1 goals"] |

## Proposed edges

| Subject slug | Predicate | Object slug | Rationale |
| --- | --- | --- | --- |
| manager-global-tech | attended | 1on1-manager-global-tech-2026-05-12 | inferred: person → attended → meeting |
| 1on1-manager-global-tech-2026-05-12 | made | focus-on-infra-platform-q2-2026 | inferred: meeting → made → decision |
