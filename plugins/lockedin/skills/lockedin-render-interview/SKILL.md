---
name: lockedin-render-interview
description: |
  Draft an interview answer from the LockedIn vault, in English or
  Korean. Uses the same two-turn writer/reviewer pattern as the resume
  and cover letter renderers. The user asks an interview question
  (behavioural, technical, or background); the writer turn pulls
  evidence from the vault and drafts a STAR-shaped answer; the
  reviewer turn checks it against a small rubric (clarity, evidence
  density, persona fit, conciseness, tone) before the final answer
  is shown.

  Use when the user says any of <!-- ko-example -->"interview
  answer", "면접 답변", "STAR 답변", "behavioral question", "tell me
  about a time…"<!-- /ko-example -->, or names a question and asks
  for an answer drawn from their experience.
  Output: a single answer in markdown, with cited entities resolved
  to natural language, plus a JSON rubric score.
---

# render-interview

Status: **v1.2 (calibrated)**. Research-based calibration complete.
RUBRIC.md ships with five cross-source-validated dimensions. A
banned_phrases.json (25 entries, each backed by 2+ sources) and
research-notes.md (7 cited sources) ship alongside the prompts.
Pass/fail fixture corpus under `tests/fixtures/interview/`.

## Use this when

- The user names an interview question and asks for an answer.
- The user pastes a job description and asks for talking points.
- The user says <!-- ko-example -->"STAR" or "behavioural" or "면접" or "기술 면접"<!-- /ko-example -->.

## Do NOT use when

- The user wants a full resume → `lockedin-render-resume-en`.
- The user wants a Korean cover letter → `lockedin-render-jaso`.
- The vault has no relevant role / project / achievement nodes.
  Seed first via `/lockedin init` or by ingesting a resume.

## Two-turn pattern

Writer turn produces the draft. Reviewer turn re-loads `RUBRIC.md`
fresh in a separate Claude turn and emits a JSON score. Same as the
other renderers; the split is load-bearing.

## Output shape

A single markdown answer, no headers. STAR (Situation / Task /
Action / Result) by default; PAR (Problem / Action / Result) when
the question is incident-shaped. One experience per paragraph with
explicit transitions, mirroring the policy in
`lockedin-render-resume-en` and `lockedin-render-jaso`.

The answer pulls evidence from the vault using slug citation
(`[[type/slug]]`); the slugs are resolved to natural language by
`lockedin/render/resolve_slugs.py` before the artifact is shown to
the user.

## Files in this directory

```
SKILL.md             (this file)
research-notes.md    7 cited sources, cross-source analysis summary
banned_phrases.json  25 entries, severity-tagged, each backed by 2+ URLs
prompt-writer.md     writer-turn instruction
prompt-reviewer.md   reviewer-turn instruction (re-loads RUBRIC.md fresh)
RUBRIC.md            5-dimension scoring contract + score bands
```

## Calibration status

v1.2 calibrated. The rubric dimensions (clarity, evidence_density,
persona_fit, conciseness, tone) are grounded in cross-source public
research from MIT CAPD, The Muse, Indeed, Harvard Business Review,
Yale OCS, The Interview Guys, and Big Interview. The banned_phrases.json
contains 25 entries across four categories (weak_ownership, trait_claim,
rehearsed_non_answer, vague_filler), each backed by 2+ independent
sources. Pass and fail fixture corpus is at
`tests/fixtures/interview/{pass,fail}/` (3 pass, 3 fail).
