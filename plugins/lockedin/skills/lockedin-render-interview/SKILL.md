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

Status: **v1.1 (skeleton)**. Skill scaffold ships with prompts and a
minimal rubric. Cross-source calibration of the rubric and a
fixture set are v1.2 targets. The skill is functional today; quality
will tighten with calibration.

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
SKILL.md
prompt-writer.md     writer-turn instruction
prompt-reviewer.md   reviewer-turn instruction (separate Claude turn)
RUBRIC.md            5-dimension scoring contract (calibration v1.2)
```

## Calibration status

The rubric and prompts here are v1.1 foundational. Cross-source
calibration (interview-coaching guides, hiring-manager interviews,
behavioural interview research) is the v1.2 target. Until then the
LLM reviewer turn is self-consistent against the rubric, but the
rubric itself has not been validated against an external corpus the
way the jaso and resume-en rubrics have.
