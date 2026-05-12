---
name: lockedin-render-ideas
description: |
  Proposes 3 to 5 next-project or career-move ideas grounded in the
  user's experience. One-paragraph pitch each, with cited entities.
  Two-turn writer/reviewer with a 5-dimension rubric.

  Activate when the user says <!-- ko-example -->"what should I work
  on next", "side project ideas", "새 프로젝트 아이디어", "career
  pivot ideas"<!-- /ko-example -->.
---

# render-ideas

Status: **v1.2 (calibrated)**. Research-based calibration complete.
RUBRIC.md ships with five cross-source-validated dimensions. A
banned_phrases.json (27 entries, each backed by 2+ sources) and
research-notes.md (7 cited sources) ship alongside the prompts.
Pass/fail fixture corpus under `tests/fixtures/ideas/`.

## Use this when

- The user asks "what should I work on next" or "ideas for side
  projects" or names a constraint and asks for proposals.
- The user wants to surface novel combinations of their existing
  skills and domains.
- The user asks for career-move pitches grounded in their actual
  experience.

## Do NOT use when

- The user wants a resume or cover letter → `render-resume-en` /
  `render-jaso`.
- The user wants an interview answer → `render-interview`.
- The vault is sparse. Seed first via `/lockedin init` or ingestion.

## Two-turn pattern

Writer turn surfaces 3 to 5 ideas. Reviewer turn re-loads `RUBRIC.md`
fresh and scores the set on five dimensions.

## Output shape

3 to 5 ideas, each one paragraph long, with a one-sentence pitch
followed by two to three sentences of rationale that cite vault
entities. Slug citations (`[[type/slug]]`) are resolved to natural
language by the orchestrator before the user sees the artifact.

## Files in this directory

```
SKILL.md             (this file)
research-notes.md    7 cited sources, cross-source analysis summary
banned_phrases.json  27 entries, severity-tagged, each backed by 2+ URLs
prompt-writer.md     writer-turn instruction
prompt-reviewer.md   reviewer-turn instruction (re-loads RUBRIC.md fresh)
RUBRIC.md            5-dimension scoring contract + score bands
```

## Calibration status

v1.2 calibrated. The rubric dimensions (feasibility, novelty,
evidence_ground, scope_match, motivation_alignment) are grounded in
cross-source public research from Atlassian, Inc., FasterCapital,
Proposify, Built In, fundsforNGOs, and arXiv. The banned_phrases.json
contains 27 entries across five categories (buzzword_opener,
vague_enthusiasm, hedging_language, unsubstantiated_claim,
comparison_shortcut), each backed by 2+ independent sources. Pass and
fail fixture corpus is at `tests/fixtures/ideas/{pass,fail}/`
(3 pass, 3 fail).
