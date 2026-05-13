---
fixture_kind: fail
scenario_summary: "Proposal creates a new project entity that is clearly a duplicate of an existing vault entity without surfacing it for reconciliation; duplicate detection failure."
entities_proposed:
  - type: project
    slug: auth-refactor-v2
edges_proposed: []
expected_score: 1.5
expected_revisions_required: true
dimensions_failed: ["duplicate_detection"]
banned_phrases_hit: []
notes: |
  Synthesized composite. Failure mode: silent duplicate creation.
  The vault already contains [[project/auth-refactor-acme-2026-05]] from
  fixture pass/01-shipped-feature.md (or an equivalent existing entry).
  The user input says "another auth refactor" and the writer proposes a
  new slug "auth-refactor-v2" without querying the vault for the existing
  [[project/auth-refactor-acme-2026-05]] entity.
  Dimension 5 (duplicate_detection) must score 0.0 because a clear
  duplicate candidate exists and was not surfaced for user decision.
  Score of 0.0 on dimension 5 = automatic revisions_required = true
  regardless of other dimension scores.
  Other dimensions are fine: fields are concrete, no banned phrases,
  edge inference is empty (single entity), semantic accuracy correct.
---

**User input (capture trigger)**:

Another auth refactor done — this time added token refresh logic.
Went live 2026-05-13.

---

### Writer proposal (FAILURE MODE: duplicate not surfaced)

## Proposed entities

| Field | Value | Source |
| --- | --- | --- |
| **type** | project | (classified: "auth refactor") |
| **slug** | auth-refactor-v2 | (writer invented new slug without vault query) |
| name | Auth refactor v2 | [source: "Another auth refactor … token refresh logic"] |
| description | Added token refresh logic to the auth service. | [source: "added token refresh logic"] |
| year | 2026 | [source: "2026-05-13"] |
| end_date | 2026-05-13 | [source: "Went live 2026-05-13"] |

## Proposed edges

(No edges. Single entity in this session.)

---

**NOTE (for test verification)**:

This fixture demonstrates the failure mode where the writer does NOT
query the vault and does NOT surface the existing
`[[project/auth-refactor-acme-2026-05]]` entry as a duplicate
candidate. The correct behavior would be:

> "I found a possible match: [[project/auth-refactor-acme-2026-05]] —
> 'auth service refactor' (same type, similar name).
> Options: [1] Merge into existing [2] Update existing [3] Create new"

The failure is detectable because:
1. `duplicate_candidates` in the reviewer JSON would be empty.
2. The vault has a same-type same-name candidate.
3. No vault query was run before proposing the new slug.
