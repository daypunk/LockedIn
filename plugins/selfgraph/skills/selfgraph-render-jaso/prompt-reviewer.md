# prompt-reviewer.md — render-jaso reviewer turn

This is the reviewer-turn instruction for `render-jaso`. It runs in a
SEPARATE Claude turn from the writer (`prompt-writer.md`). At the start
of this turn, **re-load `RUBRIC.md` fresh** — do not rely on memory of
the rubric from the writer turn. Same-context self-evaluation inflates
scores by ~1 point.

## Inputs

- The draft 자소서 produced by the writer turn.
- The original prompt + company / role / word-limit context.
- The user's vault (read-only — for verifying that quoted slugs
  actually exist).

## Procedure

1. **Load `RUBRIC.md` (load-bearing).** Read the file fresh from disk
   in this turn. The five dimensions (`두괄식 / 구조화 / 구체성 / 표현
   / 적합성`) and their score bands are the only thing you score
   against.
   **Hard guard**: if `RUBRIC.md` content is not visible in this
   turn's context, STOP and request it before scoring. Do not score
   from memory of a prior turn — same-context scoring inflates by ~1
   point per CLAUDE.md working agreement.
2. **Banned-phrase regex** — load `banned_phrases.json`. For each
   match in the draft, the 표현 dimension drops by 1 (floor 0). Record
   each hit in `notes`.
3. **Slug verification** — for every `[[type/slug]]` reference in the
   draft, confirm the slug exists in the vault. Missing slugs reduce
   the 구체성 dimension.
4. **Score each dimension** independently on a 0.0–5.0 scale.
5. **Decide `revisions_required`** — `true` if any dimension < 4.0.
6. **Emit JSON** in the exact schema below. No prose around it.

## Output schema (strict)

```json
{
  "두괄식": 0.0,
  "구조화": 0.0,
  "구체성": 0.0,
  "표현": 0.0,
  "적합성": 0.0,
  "notes": [
    "두괄식: <one short sentence on why this score>",
    "구조화: <one short sentence on why this score>",
    "구체성: <one short sentence on why this score>",
    "표현: <one short sentence on why this score>",
    "적합성: <one short sentence on why this score>"
  ],
  "banned_phrase_hits": [],
  "missing_slugs": [],
  "revisions_required": false
}
```

- All five dimension keys must be present.
- `notes` is a list of strings, one per dimension, in the listed order.
- `banned_phrase_hits` lists each matched phrase with its surrounding
  sentence: `["열정적으로|... 열정적으로 임했습니다 ..."]` (pipe-separated).
- `missing_slugs` lists `[[type/slug]]` references that do not resolve
  in the vault.
- `revisions_required` is `true` if any dimension < 4.0 OR
  `banned_phrase_hits` non-empty OR `missing_slugs` non-empty.

## Revision feedback

If `revisions_required` is `true`, the calling skill MAY pass the JSON
back to the writer for one revision cycle. The writer reads the
`notes` and the hits, fixes them, and produces a v2 draft. The
reviewer then runs again on v2. Limit: **one revision cycle**. After
that, hand the best version + the reviewer JSON to the user and let
them decide.

## Calibration via golden fixtures

CI runs the **non-LLM portion** of the rubric (banned-phrase regex,
structural markers, length bounds) against fixtures in
`tests/fixtures/jaso/{pass,fail}/` per PR. The full LLM rubric runs
nightly (non-blocking) and surfaces score drift across model versions
as a delta alert. See `RUBRIC.md` for the band definitions and
fixture authoring guide.

## What you do NOT do here

- Rewrite the draft. The writer turn produces text; you produce the
  JSON score. The skill orchestrates the revision loop.
- Skip dimensions. Even if a dimension scores 5/5, include it in
  `notes` with a one-sentence justification.
- Add prose around the JSON. The output must parse as JSON; the
  calling skill expects to `json.loads` the entire response.
