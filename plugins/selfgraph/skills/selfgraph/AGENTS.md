# selfgraph sub-roles

The skill operates with four sub-roles. Each is a hat the agent puts on for
a specific phase of the user flow. They are not separate Claude sessions —
just disciplined context shifts.

## Interviewer

**Purpose**: gather missing ontology nodes via Q&A.
**Triggers**: `/selfgraph init`, ambiguities surfaced during ingest, gaps
detected during render.
**Discipline**:
- Ask one question at a time. Never batch.
- Confirm before writing — show the proposed entity and ask "save this?"
- Question bank lives at `selfgraph/skill/templates/<domain>/questions.yaml`.
- Stop when the template's required fields are all filled OR the user
  signals "enough."

## Ingester

**Purpose**: read user-supplied documents and propose ontology mutations.
**Triggers**: `/selfgraph ingest <path>`.
**Discipline**:
- Always emit a typed diff before writing (`additions`, `modifications`,
  `ambiguities`).
- For `.pdf`, prefer pypdf; fall back to pdfminer.six on Korean-text
  glitches.
- For `.docx`, use python-docx; preserve paragraph and heading boundaries.
- Hand any `ambiguities` to the Interviewer rather than guessing.

## Renderer

**Purpose**: produce artifacts (jaso, resume_en, portfolio, graph) from the
ontology.
**Triggers**: `/selfgraph render <kind>`.
**Discipline**:
- Two-turn writer/reviewer pattern. The writer turn produces a draft. The
  reviewer turn re-loads `RUBRIC.md` fresh and emits JSON scores.
  Same-turn self-evaluation inflates scores by ~1 point — do not skip the
  second turn.
- Quote concrete ontology nodes by slug when generating user-facing text.
  Vague generalities are rejected by the rubric.
- For `jaso`, banned-phrase regex check runs before scoring. The
  banned-phrase list itself lives in `render-jaso/banned_phrases.json`.

## GraphCurator

**Purpose**: keep the graph clean — merge duplicates, suggest missing
edges, surface stale nodes.
**Triggers**: passively after ingest; explicitly via `/selfgraph validate`.
**Discipline**:
- Never merge or rename without user confirmation.
- Surface dangling references (a node's `links:` points to a missing slug)
  as a single batch report, not one-by-one.
