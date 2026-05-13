# RUBRIC.md — lockedin-capture scoring contract

The reviewer turn (`prompt-reviewer.md`) loads this file fresh at the
start of the reviewer turn and scores the writer's proposal against the
five dimensions below. Output schema is defined in `prompt-reviewer.md`;
this file defines the score bands and the fixture authoring guide.

Do not rely on memory of this file from the writer turn. Same-context
self-evaluation inflates scores by approximately one point per the
CLAUDE.md working agreement.

## Dimensions

### 1. Schema Conformance

Required fields per entity type are populated; field types match the
contract in `lockedin/ontology/schema.py`. Score is computed across all
proposed entities in a single capture session:

`score = populated_required_fields_correctly / total_required_fields_across_all_proposed_entities`

Required fields by entity type (subset; see schema.py for full list):

| Entity type | Required fields |
| --- | --- |
| person | name |
| company | name |
| role | title |
| project | name |
| achievement | headline |
| skill | name |
| education | institution |
| certificate | name |
| publication | name |
| volunteer | organization |
| language | language |
| document | filename |
| meeting | title |
| decision | headline |
| topic | name |

Field type violations (e.g., a date field containing free text) count
as incorrectly populated for scoring purposes.

| Score | Band |
| --- | --- |
| 5.0 | All required fields populated; all field types match schema. |
| 4.0 | All required fields present; at most one field type mismatch (non-required field). |
| 3.0 | One required field missing OR two field type mismatches. |
| 2.0 | Two required fields missing OR three+ field type mismatches. |
| 1.0 | Half or more required fields missing or wrong type. |
| 0.0 | No required fields populated or entity type is unrecognized. |

### 2. Edge Completeness

Every inferable edge from `lockedin/ontology/schema.py` EDGE_SCHEMAS
domain/range rules is present given the set of entities proposed in
this capture session.

"Inferable" means: two entities exist in the session whose types
satisfy the domain and range of a known edge predicate. Example: if
both `project` and `achievement` are proposed, the `produced` edge
(domain: project, range: achievement) is inferable and must be present.

`score = proposed_inferable_edges / max_inferable_edges`

Max-inferable-edges is the count of valid (domain, predicate, range)
triples constructible from the session's entity set.

| Score | Band |
| --- | --- |
| 5.0 | All inferable edges present. |
| 4.0 | At most one inferable edge missing. |
| 3.0 | Two inferable edges missing. |
| 2.0 | Three inferable edges missing OR a clearly load-bearing edge (e.g., project→achievement `produced`) absent. |
| 1.0 | Four+ inferable edges missing. |
| 0.0 | No edges proposed despite entities that clearly warrant them. |

### 3. Field Specificity

Values carry concrete information rather than placeholders or vague
filler. Banned-phrase list (`banned_phrases.json`) drives the regex
gate. Required-field specificity is weighted higher than optional-field
specificity.

Scoring deducts for each high-severity banned phrase hit in a required
field (−1 per hit, floor 0). Medium-severity hits in optional fields
deduct 0.5.

| Score | Band |
| --- | --- |
| 5.0 | Zero banned-phrase hits. All values are specific and concrete. |
| 4.0 | Zero high-severity hits; at most one medium-severity hit in an optional field. |
| 3.0 | One high-severity hit in any field OR two medium-severity hits. |
| 2.0 | Two high-severity hits OR four medium-severity hits. |
| 1.0 | Three+ high-severity hits. Most fields read as placeholders. |
| 0.0 | Entire proposal is placeholder language (TODO, TBD, [fill in]). |

### 4. Semantic Accuracy

Proposed entity types match the user's stated intent. The skill must
map user language to the correct schema type. Common mapping errors:

- User says "I just shipped a feature" → `project` + `achievement`.
  Wrong: a bare `topic` or a single `skill`.
- User says "I had a 1:1 with my manager" → `meeting` (extended
  definition: any structured interaction), optionally `person` for
  the manager.
  Wrong: `decision` alone (unless a decision was explicitly made).
- User says "I learned about event sourcing today" → `topic` with a
  concrete summary.
  Wrong: `skill` (event sourcing is a learning topic, not a skill
  claim, unless the user asserts proficiency).
- User says "we decided to deprecate module X" → `decision` with
  headline + context.
  Wrong: `project` alone.
- User says "I got promoted to senior" → `role` with new title + date.
  Wrong: `achievement` alone (both can be appropriate, but `role` is
  the primary entity).

| Score | Band |
| --- | --- |
| 5.0 | All entity types match user intent; no type substitutions or omissions. |
| 4.0 | Types correct; one optional secondary entity that could strengthen the graph omitted. |
| 3.0 | One primary entity type wrong (e.g., topic instead of project+achievement). |
| 2.0 | Two primary entity types wrong or a significant entity cluster missing entirely. |
| 1.0 | The proposed entity set broadly misrepresents the user's intent. |
| 0.0 | No recognizable mapping to the schema; entities invented without semantic grounding. |

### 5. Duplicate Detection and Reconciliation

If the vault already contains entities that are likely duplicates of
entities proposed in this session (slug similarity, alias match,
same-type same-name), they must be surfaced to the user for a decision.
The reviewer queries the vault for candidates; the skill asks the user.

- **Score 5.0**: all duplicate candidates surfaced; user made an
  explicit choice for each; no entity written without user decision.
- **Score 4.0**: at least one candidate surfaced and resolved; vault
  query was run.
- **Score 3.0**: vault query was run; some candidates surfaced but one
  candidate that should have been surfaced was missed.
- **Score 2.0**: vault query ran but no candidates surfaced despite
  clear matches.
- **Score 1.0**: vault not queried; duplicates possible but check
  skipped.
- **Score 0.0**: an entity was written to the vault that is a clear
  duplicate of an existing entity without any user decision.
  **This is an automatic fail: `revisions_required` = true regardless
  of other dimension scores.**

`score = candidates_surfaced_and_resolved / candidates_that_should_have_been_surfaced`

Any score of 0.0 on this dimension (silent duplicate creation) sets
`revisions_required` to `true` regardless of total.

## Pass criterion

`revisions_required` is **false** only when ALL of:

- Every dimension >= 4.0.
- `banned_phrase_hits` is empty.
- No silent duplicate was created (dimension 5 > 0.0).

One revision cycle is permitted: the reviewer JSON is passed back to
the writer, which fixes and re-proposes. After the revision cycle, the
best version is handed to the user with the score for their decision.

## Total score

`total = mean(dimension_1, dimension_2, dimension_3, dimension_4, dimension_5)`

## Fixture authoring guide

Place pass and fail golden fixtures under
`tests/fixtures/capture/{pass,fail}/`:

```
tests/fixtures/capture/
  pass/
    01-shipped-feature.md      (project + achievement + skill; correct edges)
    02-1on1-meeting.md         (meeting + person + decision; correct edges)
    03-architecture-learning.md (topic; concrete summary)
  fail/
    01-placeholder-fields.md   (schema/specificity failure — TODO in required field)
    02-missing-edges.md        (edge completeness failure — produced edge absent)
    03-silent-dupe.md          (dedup failure — existing entity not surfaced)
```

Each fixture is plain markdown with frontmatter:

```yaml
---
fixture_kind: pass          # or fail
scenario_summary: "..."     # one sentence describing the capture scenario
entities_proposed:
  - type: project
    slug: some-project
  - type: achievement
    slug: some-achievement
edges_proposed:
  - subject: some-project
    predicate: produced
    object: some-achievement
expected_score: 4.5         # mean of 5 dimensions
expected_revisions_required: false
dimensions_failed: []       # for fail fixtures: list dimension names
banned_phrases_hit: []      # for fail fixtures: list matched phrases
notes: |
  Why this is a known good/bad sample. Cite the failure mode it
  isolates if a fail fixture.
---

{Synthesized user input that triggers capture}

---

### Writer proposal

{Proposed entity structure as markdown table or YAML block}
```

## Calibration status (v0.1)

Foundational. Calibrated against internal design rationale
(`lockedin/ontology/schema.py`, `docs/ontology-spec.md`, CLAUDE.md
working agreements). A named human reviewer walkthrough of the golden
fixtures is recommended before v1 release to confirm band thresholds.
Until then, the LLM reviewer turn is self-consistent against this
rubric, and the fixture set provides ground truth.
