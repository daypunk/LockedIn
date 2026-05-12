# prompt-reviewer.md — render-interview reviewer turn

This is the reviewer-turn instruction for `render-interview`. It
runs in a SEPARATE Claude turn from the writer.

## Procedure

1. **Load `RUBRIC.md` (load-bearing).** Re-load RUBRIC.md from disk
   fresh in this reviewer turn; do not rely on context from any
   writer turn. The five dimensions and their score bands are the
   only thing you score against.
   **Hard guard**: if `RUBRIC.md` content is not visible in this
   turn's context, STOP and request it before scoring.
2. **Slug verification.** For every `[[type/slug]]` reference,
   confirm the slug resolves in the vault. Missing slugs reduce the
   evidence_density dimension.
3. **Score each dimension** independently on a 0.0–5.0 scale.
4. **Decide `revisions_required`** — `true` if any dimension < 4.0
   OR `missing_slugs` non-empty.
5. **Emit JSON** in the schema below. No prose around it.

## Output schema (strict)

```json
{
  "clarity": 0.0,
  "evidence_density": 0.0,
  "persona_fit": 0.0,
  "conciseness": 0.0,
  "tone": 0.0,
  "notes": [
    "clarity: <one short sentence>",
    "evidence_density: <one short sentence>",
    "persona_fit: <one short sentence>",
    "conciseness: <one short sentence>",
    "tone: <one short sentence>"
  ],
  "missing_slugs": [],
  "revisions_required": false
}
```

## Revision feedback

If `revisions_required` is `true`, the calling skill MAY pass the
JSON back to the writer for one revision cycle. Limit: one revision.

## What you do NOT do

- Rewrite the draft.
- Skip dimensions.
- Add prose around the JSON.
