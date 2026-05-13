---
name: lockedin-capture
description: |
  Converts in-session capture intents ("save this", "log this", "track
  this", "absorb this") into structured vault entries via a two-turn
  writer/reviewer pattern with duplicate detection and reconciliation.
  Writer proposes entity/edge structure; reviewer scores against five
  rubric dimensions and surfaces duplicate candidates for user decision.

  Activate when the user signals explicit capture intent from their
  current work session, or after a successful ingest where new entities
  are being proposed. Also activate when the user says "remember this",
  "capture this", "add this to my vault", or describes something they
  just shipped, learned, decided, or discussed.
---

# lockedin-capture

Dedicated capture skill for in-session work moments. Promotes capture
from an implicit sub-role of the main `lockedin` skill into a
first-class calibrated flow with its own writer/reviewer contract,
matching the rigor of `lockedin-render-jaso` and
`lockedin-render-resume-en`.

Capture quality determines vault quality. Vault quality determines
render quality. This skill owns that first link.

## Use this skill when

- The user says "save this", "log this", "track this", "absorb this",
  "remember this", "capture this", or "add this to my vault".
- The user describes a thing they just did: shipped a feature,
  attended a meeting, made a decision, learned something, completed a
  project milestone.
- The user pastes notes, a git log excerpt, a PR description, a Slack
  summary, or any short text and says to save it.
- The main `lockedin` skill detects capture intent during a session
  and routes here.

## Do NOT use this skill when

- The user is doing coding, debugging, or writing without any signal
  that they want to persist the work moment to the vault.
- The user asks to render an artifact (resume, jaso, ideas) — route to
  the appropriate render skill instead.
- The user wants to query their vault without adding anything — use the
  main `lockedin` skill's query flow.
- The user wants to audit a document — use `lockedin-audit`.

## Execution model

```
User input
    │
    ▼
1. Writer turn (prompt-writer.md)
   - Read user input + any provided context
   - Propose entity types, fields, edge structure
   - Run _infer_edges() mentally from EDGE_SCHEMAS domain/range
   - Quote source phrases from user input
   - Output: structured proposal (markdown table)
    │
    ▼
2. ValidatorDeterm (lockedin validate --dry-run)
   - Deterministic field-type and required-field check
   - Catches schema errors before LLM reviewer sees the proposal
    │
    ▼
3. Reviewer turn (prompt-reviewer.md) — SEPARATE Claude context
   - Re-load RUBRIC.md fresh (not from writer-turn memory)
   - Score 5 dimensions independently
   - Query vault for duplicate candidates (slug similarity, alias match)
   - Output: JSON score + candidates + suggested revisions
    │
    ▼
4. ReconcileNegotiator (if duplicates surfaced)
   - Present candidates to user as a numbered list
   - Ask one question: merge / update / create new
   - Never auto-merge, never auto-create-duplicate
    │
    ▼
5. write-before-confirm
   - State what will be written: "Saving 2 entries — meeting X, decision Y. OK?"
   - On confirmation: call write_entity for each proposed entity
   - Edges written atomically with entities
```

The write-before-confirm step applies even if the user has granted
write permission earlier in the session. No silent vault mutations.

## Rubric dimensions

Full definitions and score bands in `RUBRIC.md`. Summary:

1. **Schema conformance** — required fields populated correctly.
2. **Edge completeness** — all inferable edges from EDGE_SCHEMAS present.
3. **Field specificity** — values carry concrete information; no placeholders.
4. **Semantic accuracy** — entity types match the user's stated intent.
5. **Duplicate detection + reconciliation** — candidates surfaced and
   resolved with user; never silent-merge or silent-create-duplicate.

Pass criterion: every dimension >= 4, no silent duplicate creation.

## Reconciliation policy

- **Never silent-merge**: do not fold a new entity into an existing one
  without presenting the match and asking the user.
- **Never silent-create-duplicate**: do not write a new entity when a
  candidate with matching slug, name, or aliases already exists in the
  vault without asking the user first.
- **Surface candidates**: when the vault has a likely duplicate
  (slug-distance <= 2, same type, matching name or alias), present it
  as: *"I found a possible match: `[[type/slug]]` — same project? Merge
  into it, update it, or create a separate entry?"*
- **One question, one candidate at a time**: if multiple duplicates
  exist, handle them sequentially.

## Output

After the writer/reviewer cycle and user confirmation:

- Confirmed vault entries, one markdown file per entity under
  `<vault>/experience/<type>/<slug>.md`.
- Edges encoded in each entity file's `links:` frontmatter block.
- `EXPERIENCE.md` regenerated at the vault root (auto via
  `write_entity`).
- Reviewer JSON score stored at
  `<vault>/metrics/capture/<iso-timestamp>.json` for drift tracking.

## Files in this directory

```
SKILL.md            (this file)
RUBRIC.md           5 dimensions; score bands; fixture authoring guide
prompt-writer.md    writer-turn instruction
prompt-reviewer.md  reviewer-turn instruction (separate Claude context)
AGENTS.md           four agents: Writer, ValidatorDeterm, Reviewer, ReconcileNegotiator
TOOLS.md            deterministic tools the skill uses
banned_phrases.json phrases that indicate low-quality field values
research-notes.md   sources informing capture design rationale
```
