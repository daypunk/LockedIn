# prompt-reviewer.md — lockedin-capture reviewer turn

This is the reviewer-turn instruction for `lockedin-capture`. It runs
in a SEPARATE Claude turn from the writer (`prompt-writer.md`). At the
start of this turn, **re-load `RUBRIC.md` fresh from disk** — do not
rely on memory of the rubric from the writer turn. Same-context
self-evaluation inflates scores by approximately one point per the
CLAUDE.md working agreement.

**Hard guard**: if `RUBRIC.md` content is not visible in this turn's
context, STOP and request it before scoring. Do not score from memory.

## Inputs

- The writer's structured proposal (entity tables + edge table).
- The original user input and any provided context.
- The user's vault (read-only — for duplicate candidate detection in
  dimension 5).

## Procedure

### Step 1 — Load RUBRIC.md (load-bearing)

Read `RUBRIC.md` fresh from disk. The five dimensions
(`schema_conformance`, `edge_completeness`, `field_specificity`,
`semantic_accuracy`, `duplicate_detection`) and their score bands are
the only thing you score against.

### Step 2 — Score dimension 1: Schema Conformance

For each proposed entity, check that:
- The entity type is a recognized type from `ENTITY_TYPES`.
- Every required field for that type is populated (non-empty string,
  not placeholder text).
- Field types match the schema contracts in RUBRIC.md dimension 1.

Compute: `filled_correctly / total_required`. Apply score bands.

### Step 3 — Score dimension 2: Edge Completeness

Given the set of proposed entity types, enumerate all inferable edges
from the EDGE_SCHEMAS domain/range rules (see RUBRIC.md dimension 2
and prompt-writer.md Step 3 for the reference table).

Compare the proposed edges against the inferable set. Note any missing
edges by name. Apply score bands.

### Step 4 — Score dimension 3: Field Specificity

Load `banned_phrases.json`. Run a case-insensitive whole-phrase
regex match (`\b<phrase>\b`) against each proposed field value in the
writer's proposal. For each match:

- High-severity hit in a required field: deduct 1.0 from this
  dimension (floor 0).
- Medium-severity hit in any field: deduct 0.5.

Record each hit in `banned_phrase_hits` as
`"<phrase>|<field_name>: <field_value>"`.

### Step 5 — Score dimension 4: Semantic Accuracy

Using the mapping table in RUBRIC.md dimension 4, evaluate whether the
proposed entity types match the user's stated intent. Note any type
substitutions or omissions.

### Step 6 — Score dimension 5: Duplicate Detection and Reconciliation

Query the vault for potential duplicates:

1. For each proposed entity, search the vault under
   `<vault>/experience/<type>/` for files whose frontmatter `name` or
   `title` or `aliases` list contains a value within slug edit-distance
   2 of the proposed entity's name.
2. Also check the proposed slug directly: if
   `<vault>/experience/<type>/<proposed-slug>.md` exists, it is a
   definite candidate.
3. Collect all candidates in `duplicate_candidates`.

The reviewer surfaces candidates; the reviewer does NOT decide. The
ReconcileNegotiator agent asks the user. Score dimension 5 based on
whether candidates were found and surfaced correctly (see RUBRIC.md
dimension 5 bands).

If any entity would be written to the vault without surfacing a clear
duplicate, dimension 5 = 0.0 and `revisions_required` = true
regardless of other scores.

### Step 7 — Compute total and decide revisions_required

`total = mean(d1, d2, d3, d4, d5)`

`revisions_required` is `true` if:
- Any dimension < 4.0, OR
- `banned_phrase_hits` is non-empty, OR
- `duplicate_candidates` contains entries that the writer did not flag
  in the proposal (missed candidates = dedup failure).

### Step 8 — Emit JSON

Output the JSON below with no surrounding prose. The calling skill
expects `json.loads` on the entire response.

## Output schema (strict)

```json
{
  "schema_conformance": 0.0,
  "edge_completeness": 0.0,
  "field_specificity": 0.0,
  "semantic_accuracy": 0.0,
  "duplicate_detection": 0.0,
  "total": 0.0,
  "notes": [
    "schema_conformance: <one sentence rationale>",
    "edge_completeness: <one sentence rationale>",
    "field_specificity: <one sentence rationale>",
    "semantic_accuracy: <one sentence rationale>",
    "duplicate_detection: <one sentence rationale>"
  ],
  "banned_phrase_hits": [],
  "duplicate_candidates": [],
  "missing_edges": [],
  "revisions_required": false
}
```

- All five dimension keys must be present with 0.0–5.0 values.
- `total` is the arithmetic mean of the five dimensions, rounded to
  two decimal places.
- `notes` is a list of exactly five strings, one per dimension in the
  listed order.
- `banned_phrase_hits` lists each matched phrase with its field,
  pipe-separated: `["TODO|headline: TODO"]`.
- `duplicate_candidates` lists each vault candidate as
  `"[[type/slug]] — <brief description of match signal>"`.
  An empty list means the vault query ran and found no matches.
  The list must be present (not `null`) even when empty.
- `missing_edges` lists inferable edges that the writer omitted:
  `["project→produced→achievement: project/x + achievement/y"]`.
- `revisions_required` follows the gate rules in Step 7.

## Revision cycle

If `revisions_required` is `true`, the skill orchestrator passes the
JSON back to the writer for one revision cycle. The writer reads
`notes`, `banned_phrase_hits`, `missing_edges`, and
`duplicate_candidates`, then re-proposes. The reviewer runs again on
the revised proposal. Limit: one revision cycle. After that, the best
version + the reviewer JSON goes to the user.

## What you do NOT do here

- Rewrite the writer's proposal. You score it; the writer revises.
- Skip dimensions. Include a note for every dimension even when it
  scores 5.0.
- Decide for the user on duplicates. Surface them; never merge or
  discard silently.
- Add prose around the JSON. Output must parse as JSON.
- Be lenient. A proposal with one banned phrase in a required field
  scores 3.0 on field_specificity. The rubric is the rubric.
