# prompt-reviewer.md — render-resume-en reviewer turn

This is the reviewer-turn instruction for `render-resume-en`. It runs
in a SEPARATE Claude turn from the writer (`prompt-writer.md`). At the
start of this turn, **re-load `RUBRIC.md` fresh** — do not rely on
memory of the rubric from the writer turn. Same-context self-evaluation
inflates scores by ~1 point.

## Inputs

- The draft resume produced by the writer turn.
- The persona flag + target_company / target_jd_text context.
- The user's vault (read-only — for verifying that quoted slugs
  actually exist).

## Procedure

1. **Load `RUBRIC.md` (load-bearing).** Read the file fresh from disk
   in this turn. The five dimensions (`metric_density /
   action_verb_quality / structural_adherence /
   banned_phrase_cleanliness / persona_fit`) and their score bands are
   the only thing you score against.
   **Hard guard**: if `RUBRIC.md` content is not visible in this
   turn's context, STOP and request it before scoring. Do not score
   from memory of a prior turn — same-context scoring inflates by ~1
   point per CLAUDE.md working agreement.
2. **Banned-phrase regex** — load `banned_phrases.json`. For each
   match in the `phrases` array, the banned_phrase_cleanliness
   dimension drops by 1 (floor 0). Record each hit in `notes`.
   Entries in `soft_overuse` flag in `notes` but do not deduct unless
   ≥2 occurrences.
3. **Slug verification** — for every `[[type/slug]]` reference in the
   draft, confirm the slug exists in the vault. Missing slugs reduce
   the metric_density dimension (since the underlying claim becomes
   unverifiable).
4. **Persona check** — verify the resume voice matches the persona
   flag (see RUBRIC.md dimension 5 definitions).
5. **Score each dimension** independently on a 0.0–5.0 scale.
6. **Decide `revisions_required`** — `true` if any dimension < 4.0
   OR `banned_phrase_hits` non-empty OR `missing_slugs` non-empty.
7. **Emit JSON** in the exact schema below. No prose around it.

## Output schema (strict)

```json
{
  "metric_density": 0.0,
  "action_verb_quality": 0.0,
  "structural_adherence": 0.0,
  "banned_phrase_cleanliness": 0.0,
  "persona_fit": 0.0,
  "notes": [
    "metric_density: <one short sentence on why this score>",
    "action_verb_quality: <one short sentence>",
    "structural_adherence: <one short sentence>",
    "banned_phrase_cleanliness: <one short sentence>",
    "persona_fit: <one short sentence>"
  ],
  "banned_phrase_hits": [],
  "missing_slugs": [],
  "revisions_required": false
}
```

- All five dimension keys must be present.
- `notes` is a list of strings, one per dimension, in the listed
  order.
- `banned_phrase_hits` lists each matched phrase with its surrounding
  bullet, pipe-separated:
  `["responsible for|... was responsible for production deploys ..."]`.
- `missing_slugs` lists `[[type/slug]]` references that do not
  resolve in the vault.
- `revisions_required` follows the gate rules in step 6.

## Revision feedback

If `revisions_required` is `true`, the calling skill MAY pass the JSON
back to the writer for one revision cycle. The writer reads `notes`
and the hits, fixes them, and produces a v2 draft. The reviewer then
runs again on v2. Limit: **one revision cycle**. After that, hand the
best version + the reviewer JSON to the user and let them decide.

## Calibration via golden fixtures

CI runs the **non-LLM portion** of the rubric (banned-phrase regex,
structural markers, length bounds, bullet count) against fixtures in
`tests/fixtures/resume-en/{pass,fail}/` per PR. The full LLM rubric
runs nightly (non-blocking) and surfaces score drift across model
versions as a delta alert. See `RUBRIC.md` for the band definitions
and fixture authoring guide.

## What you do NOT do here

- Rewrite the draft. The writer turn produces text; you produce the
  JSON score. The skill orchestrates the revision loop.
- Skip dimensions. Even if a dimension scores 5/5, include it in
  `notes` with a one-sentence justification.
- Add prose around the JSON. The output must parse as JSON; the
  calling skill expects to `json.loads` the entire response.
- Be lenient. If the resume reads well but has 3 banned phrases, the
  cleanliness score still drops to 2.0. The rubric is the rubric.
- Reward keyword-stuffing. Hidden ATS footers, repeated keyword
  blocks, or unnatural noun stacks should drop persona_fit and
  structural_adherence. Modern ATS (2025+) uses semantic intelligence
  and so should this rubric.
