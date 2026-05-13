---
fixture_kind: fail
scenario_summary: "Capture proposal uses TODO and TBD in required fields; schema conformance and field specificity failure."
entities_proposed:
  - type: project
    slug: some-project
  - type: achievement
    slug: some-achievement
edges_proposed:
  - subject: some-project
    predicate: produced
    object: some-achievement
expected_score: 2.0
expected_revisions_required: true
dimensions_failed: ["schema_conformance", "field_specificity"]
banned_phrases_hit: ["TODO", "TBD", "unknown"]
notes: |
  Synthesized composite. Failure mode: placeholder text in required fields.
  project.name = "TODO" → required field, high-severity banned phrase.
  achievement.headline = "TBD" → required field, high-severity banned phrase.
  achievement.metric = "unknown" → high-severity banned phrase.
  These are schema_conformance failures (required field value is placeholder)
  and field_specificity failures (banned_phrase_hits non-empty).
  The proposal contains valid edges, so dimension 2 (edge_completeness) is fine.
  Dimension 4 (semantic_accuracy) is fine: project + achievement is the correct
  type mapping even though the values are placeholders.
  Overall: dimensions 1 and 3 should score ≤ 2.0; revisions_required = true.
---

**User input (capture trigger)**:

Save this — I did something at work today. It was a project and some kind of result.

---

### Writer proposal (FAILURE MODE: placeholders in required fields)

## Proposed entities

| Field | Value | Source |
| --- | --- | --- |
| **type** | project | (classified from input) |
| **slug** | some-project | |
| name | TODO | (no name found in input — should have been left empty, not TODO) |
| description | TBD | (no description found — should have been left empty) |

---

| Field | Value | Source |
| --- | --- | --- |
| **type** | achievement | (classified from input) |
| **slug** | some-achievement | |
| headline | TBD | (no headline found — should have been left empty, not TBD) |
| metric | unknown | (no metric stated — should have been left empty) |
| delta | | |

## Proposed edges

| Subject slug | Predicate | Object slug | Rationale |
| --- | --- | --- | --- |
| some-project | produced | some-achievement | inferred: project → produced → achievement |
