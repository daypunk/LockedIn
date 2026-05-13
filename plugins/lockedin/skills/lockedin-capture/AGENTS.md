# AGENTS.md — lockedin-capture

Four agents participate in the capture flow. They are not separate
Claude sessions — they are disciplined context shifts within the skill
orchestration, each with a clear responsibility boundary.

## Writer

**Purpose**: read the user's capture input and produce a structured
entity/edge proposal.

**Runs**: writer turn, inside Claude Code on the user's subscription.

**Inputs**:
- User's natural-language input describing the work moment.
- Optional context: current file, git log excerpt, README, clipboard.
- Optional vault snapshot: existing entities relevant to this input.

**Discipline**:
- Classify intent to entity types using the semantic accuracy rules in
  `RUBRIC.md` dimension 4.
- Populate required fields from user input only. Empty string for
  missing values — never placeholder text.
- Quote source phrases from user input for each field (auditable).
- Run `_infer_edges()` mentally from EDGE_SCHEMAS domain/range pairs.
- Output structured proposal only; no self-evaluation; no vault writes.

**Failure modes to avoid**:
- Inventing field values not present in user input.
- Using placeholder text (TODO, TBD, [fill in], unknown).
- Collapsing two experiences into one entity.
- Omitting inferable edges because they feel obvious.

---

## ValidatorDeterm

**Purpose**: run deterministic field-type and required-field checks on
the writer's proposal before the reviewer LLM sees it.

**Runs**: deterministic CLI step (`lockedin validate --dry-run` or
equivalent schema check). No LLM needed.

**Inputs**: the writer's proposed entity structure (serialized to
temporary markdown or JSON).

**Discipline**:
- Check that every proposed entity type is in `ENTITY_TYPES`.
- Check that required fields are present and non-empty.
- Check field types match the `FieldSpec.type` contract.
- Exit with a structured error list on failure; pass silently on clean.

**Why this exists**: catches mechanical schema errors before the
reviewer LLM spends tokens on a structurally broken proposal. Runs
fast (no LLM call); ensures the reviewer's scoring starts from a
schema-valid baseline.

---

## Reviewer

**Purpose**: score the writer's proposal against the five RUBRIC.md
dimensions and surface duplicate candidates.

**Runs**: reviewer turn, SEPARATE Claude context from the writer turn.
`RUBRIC.md` is re-loaded fresh at the start of this turn.

**Inputs**:
- Writer's structured proposal.
- Original user input and context.
- Vault (read-only) for dimension 5 duplicate query.

**Discipline**:
- Re-load `RUBRIC.md` before scoring. Never score from memory of a
  prior turn.
- Score each dimension independently on 0.0–5.0.
- Query vault for duplicate candidates (slug match, alias match,
  same-type same-name).
- Output JSON only. No prose, no rewriting.

**Failure modes to avoid**:
- Skipping the RUBRIC.md reload.
- Deciding on duplicates for the user (surface candidates; do not merge).
- Scoring leniently because the proposal "looks good". The rubric
  bands are the standard.

---

## ReconcileNegotiator

**Purpose**: handle the user-facing conversation when duplicate
candidates exist, and confirm the final vault write.

**Runs**: after the reviewer emits `duplicate_candidates`, when the
list is non-empty.

**Inputs**: reviewer JSON (specifically `duplicate_candidates`).

**Discipline**:
- Present each candidate as a numbered choice:
  ```
  I found a possible match for [type/proposed-slug]:
    [[project/existing-slug]] — "Existing Project Name" (same type,
    similar name)
  
  Options:
    [1] Merge into existing entity (update its fields with new info)
    [2] Update existing entity only (overwrite changed fields)
    [3] Create new separate entry
  ```
- Handle one candidate at a time. Do not batch multiple decisions.
- After all candidates are resolved, confirm the full write:
  *"Saving N entries: [list]. OK?"*
- Never write without explicit user confirmation.
- After confirmation, call `write_entity` for each approved entity,
  write edges in `links:` frontmatter, and trigger master view refresh.

**Failure modes to avoid**:
- Silent-merge: writing into an existing entity without asking.
- Silent-create: writing a new entity when a clear duplicate exists
  without asking.
- Batching multiple duplicate decisions into one question.
