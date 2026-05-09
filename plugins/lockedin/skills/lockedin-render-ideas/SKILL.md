---
name: lockedin-render-ideas
description: |
  Generate new project ideas, side-project pitches, or career-move
  proposals from the LockedIn vault. The skill walks the user's
  past work, identifies under-exploited combinations of skills and
  domains, and proposes concrete next moves with a one-paragraph
  rationale grounded in the user's actual experience. Two-turn
  writer/reviewer pattern; reviewer scores feasibility, novelty,
  evidence ground, scope match, and motivation alignment.

  Use when the user says any of <!-- ko-example -->"what should I
  work on next", "ideas for side projects", "새 프로젝트 아이디어",
  "next move", "career pivot ideas", "흥미로운 조합"<!-- /ko-example -->,
  or asks for proposals derived from their own experience. Output: 3 to 5 ideas in markdown, each one
  paragraph long with cited entities resolved to natural language,
  plus a JSON rubric score for the set.
---

# render-ideas

Status: **v1.1 (skeleton)**. Skill scaffold ships with prompts and a
minimal rubric. Cross-source calibration is a v1.2 target. The skill
is functional today; the rubric has not been validated against an
external corpus the way jaso and resume-en have.

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
SKILL.md
prompt-writer.md     writer-turn instruction
prompt-reviewer.md   reviewer-turn instruction (separate Claude turn)
RUBRIC.md            5-dimension scoring contract (calibration v1.2)
```

## Calibration status

The rubric here is v1.1 foundational. Cross-source calibration
(against entrepreneur / career-coach corpora) is the v1.2 target.
Until then, the reviewer turn is self-consistent against this
rubric, but does not match the calibration density of the jaso or
resume-en rubrics.
