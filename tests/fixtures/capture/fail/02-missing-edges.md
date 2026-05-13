---
fixture_kind: fail
scenario_summary: "Proposal captures project and achievement with correct fields but omits the required produced edge; edge completeness failure."
entities_proposed:
  - type: project
    slug: payment-retry-refactor
  - type: achievement
    slug: duplicate-charge-reduction-2026
edges_proposed: []
expected_score: 2.5
expected_revisions_required: true
dimensions_failed: ["edge_completeness"]
banned_phrases_hit: []
notes: |
  Synthesized composite. Failure mode: missing inferable edge.
  project.name = "Payment retry refactor" — valid, concrete, no banned phrases.
  achievement.headline = "Reduced duplicate charge incidents from 35/month to 2/month" — valid.
  Both required fields populated correctly. Schema conformance and field specificity pass.
  Semantic accuracy correct: project + achievement.
  FAILURE: no edges proposed despite project + achievement pair clearly warranting
  the "produced" edge (domain: project/role, range: achievement).
  edge_completeness dimension should score 0.0 (zero proposed, one inferable).
  revisions_required = true due to dimension 2 < 4.0.
---

**User input (capture trigger)**:

Finished the payment retry refactor for ACME_CORP's billing service.
The idempotency layer I added cut duplicate charge incidents from about
35 per month down to under 2. Merged yesterday, 2026-05-12.

---

### Writer proposal (FAILURE MODE: missing produced edge)

## Proposed entities

| Field | Value | Source |
| --- | --- | --- |
| **type** | project | (classified: "payment retry refactor") |
| **slug** | payment-retry-refactor | (derived from name) |
| name | Payment retry refactor | [source: "payment retry refactor for ACME_CORP's billing service"] |
| description | Added an idempotency layer to the payment retry pipeline to prevent duplicate charge incidents. | [source: "idempotency layer I added"] |
| year | 2026 | [source: "2026-05-12"] |
| end_date | 2026-05-12 | [source: "Merged yesterday, 2026-05-12"] |

---

| Field | Value | Source |
| --- | --- | --- |
| **type** | achievement | (classified: quantified outcome present) |
| **slug** | duplicate-charge-reduction-2026 | (derived from headline) |
| headline | Reduced duplicate charge incidents from 35/month to under 2/month | [source: "cut duplicate charge incidents from about 35 per month down to under 2"] |
| metric | duplicate charge incidents per month | [source: "duplicate charge incidents from about 35 per month"] |
| delta | -94% (35/month → <2/month) | [source: "from about 35 per month down to under 2"] |
| timeframe | 2026-05 | [source: "2026-05-12"] |

## Proposed edges

(No edges proposed — this is the failure mode being tested.
The writer should have inferred: payment-retry-refactor → produced →
duplicate-charge-reduction-2026 from EDGE_SCHEMAS: produced has
domain=(project, role), range=(achievement).)
