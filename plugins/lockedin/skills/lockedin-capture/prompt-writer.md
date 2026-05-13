# prompt-writer.md — lockedin-capture writer turn

This is the writer-turn instruction for `lockedin-capture`. The
reviewer turn lives in `prompt-reviewer.md` and runs in a SEPARATE
Claude turn with `RUBRIC.md` re-loaded fresh. Do not collapse the two
turns — same-context self-evaluation inflates scores by approximately
one point per the CLAUDE.md working agreement.

## Inputs

- **user_input** (required): the user's natural-language statement or
  pasted text describing what happened. Could be a sentence ("I just
  shipped the auth refactor"), a paragraph, a git log excerpt, a PR
  description, or a Slack thread summary.
- **context** (optional): supporting material provided by the user or
  injected by the skill orchestrator:
  - current file being edited
  - recent git log (`git log --oneline -10`)
  - README excerpt for the current project
  - clipboard content
- **vault_snapshot** (optional): a brief summary of existing vault
  entities relevant to the user's input (provided by orchestrator via
  `lockedin experience <slug>` or a targeted vault read). Used to
  ground entity proposals in already-existing nodes.

## Procedure

### Step 1 — Classify the capture intent

Read the user input and identify the primary capture intent. Map to
the closest schema types using the semantic accuracy rules in RUBRIC.md
dimension 4. Common mappings:

| User language | Primary entity types |
| --- | --- |
| "shipped X", "launched X", "deployed X" | `project` + `achievement` |
| "had a 1:1", "met with", "attended" | `meeting` (+ `person` if named) |
| "we decided to", "decided not to" | `decision` (+ `meeting` if via meeting) |
| "learned about", "read about", "studied" | `topic` |
| "got promoted", "joined as", "started at" | `role` (+ `company`) |
| "built a side project", "open-sourced" | `project` |
| "got certified", "completed course" | `certificate` or `education` |
| "wrote an article", "gave a talk" | `publication` |

When in doubt, prefer a cluster of two related entities over a single
over-general one. A shipped feature is almost always `project` +
`achievement`, not just `project`.

### Step 2 — Extract field values from user input

For each proposed entity, populate its required fields first, then
optional fields where the user input contains a source value.

**Do NOT invent field values.** If a required field has no source in
the user input, leave it as an explicit empty string `""` in the
proposal — do NOT fill with "TODO", "TBD", "[fill in]", "unknown", or
any other placeholder. Empty strings are honest gaps; placeholders are
quality failures.

**Quote source phrases.** In the proposal output, annotate each filled
field value with the source phrase from the user input that grounded
it, in brackets: `value [source: "…phrase from input…"]`. This makes
the proposal auditable. The final vault write strips the annotations.

Required fields by entity type are listed in RUBRIC.md dimension 1.
Full field contracts are in `lockedin/ontology/schema.py`.

### Step 3 — Run _infer_edges() mentally

Given the set of proposed entities, identify all valid edges from the
EDGE_SCHEMAS domain/range rules in `lockedin/ontology/schema.py`.

An edge is valid if:
- `entity_a.type` is in `edge.domain`
- `entity_b.type` is in `edge.range`
- The edge semantically fits the user's stated relationship.

Write every valid inferable edge into the proposal. Do NOT omit edges
because they feel obvious — obvious edges are exactly what this step
catches.

Key edges to always check:

| If session has… | Infer edge… |
| --- | --- |
| `project` + `achievement` | `project` → `produced` → `achievement` |
| `project` + `skill` | `project` → `uses_skill` → `skill` |
| `role` + `achievement` | `role` → `produced` → `achievement` |
| `role` + `skill` | `role` → `uses_skill` → `skill` |
| `person` + `meeting` | `person` → `attended` → `meeting` |
| `meeting` + `decision` | `meeting` → `made` → `decision` |
| `person` + `decision` | `person` → `made` → `decision` |
| `person` + `company` | `person` → `held_role_at` → `company` |
| `meeting` + `topic` | `meeting` → `covers` → `topic` |
| any entity + `document` | entity → `derived_from` → `document` |

### Step 4 — Write the structured proposal

Output a structured proposal in the following format. Use markdown
tables for entity fields and a separate section for edges.

```markdown
## Proposed entities

| Field | Value | Source |
| --- | --- | --- |
| **type** | project | (classified from input) |
| **slug** | <proposed-slug> | (derived from name) |
| name | <project name> [source: "…"] | |
| description | <extracted description> [source: "…"] | |
| year | <year if stated> | |
| ... | | |

---

| Field | Value | Source |
| --- | --- | --- |
| **type** | achievement | (classified from input) |
| **slug** | <proposed-slug> | |
| headline | <one-line summary> [source: "…"] | |
| metric | <metric if stated> [source: "…"] | |
| ... | | |

## Proposed edges

| Subject slug | Predicate | Object slug | Rationale |
| --- | --- | --- | --- |
| <project-slug> | produced | <achievement-slug> | inferred: project→achievement |
| <project-slug> | uses_skill | <skill-slug> | inferred: project→skill |
```

### Step 5 — Slug proposal rules

Slugs are lowercase kebab-case, max 40 characters, derived from the
entity name:

- `project/payment-refactor-2026-05`
- `achievement/auth-latency-cut-78pct`
- `meeting/1on1-manager-2026-05-13`
- `decision/deprecate-legacy-scheduler`
- `topic/event-sourcing`

If the vault_snapshot shows a similar existing slug, propose using
the existing slug for the entity and flag it clearly in the proposal:
*"This entity may match existing `[[type/existing-slug]]` — see
duplicate candidate note."*

### Step 6 — Do NOT do these things

- **Do not score yourself.** The reviewer turn scores. Do not include
  a self-assessment of the proposal quality in this turn's output.
- **Do not ask the user questions in this turn.** Unresolvable
  ambiguities are noted in the proposal for the reviewer to surface.
  Questions come after the reviewer turn, via the
  ReconcileNegotiator.
- **Do not write to the vault.** This is a proposal. No filesystem
  writes happen until after user confirmation.
- **Do not use placeholder text.** Required field with no source =
  leave it empty in the proposal, not "TBD".
- **Do not invent metrics.** If the user said "improved performance"
  without a number, the `delta` field stays empty.
- **Do not collapse multiple distinct experiences into one entity.**
  Two shipped features = two `project` entities, not one with a
  vague merged name.

## Output format

The writer turn's output is handed directly to the reviewer turn and
later shown to the user after review. Emit only the structured proposal
defined in Step 4. No surrounding chat ("Here is my proposal…"). No
self-evaluation. No revision notes.
