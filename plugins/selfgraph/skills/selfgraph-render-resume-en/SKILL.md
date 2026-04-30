---
name: selfgraph-render-resume-en
description: |
  Render an English resume from the selfgraph ontology — metric-first
  bullets, STAR/PAR structure, target persona (us-tech-senior /
  us-tech-mid / pm-product). Two-turn writer/reviewer pattern with a JSON
  rubric (≥80% metric density, action-verb diversity, no vague verbs).

  Use when the user says: "render resume", "make a resume",
  "us-tech-senior resume", "resume for [target]", "polish my resume".
  Output: a markdown resume quoting concrete ontology slugs plus a JSON
  rubric score.
---

# render-resume-en

Status: **placeholder**.

## Use this when

- User asks for an English resume targeting a tech / PM persona.
- User wants their existing resume "polished" against the rubric.

## Do NOT use when

- User wants a Korean cover letter → `render-jaso`.
- User wants a portfolio website → `render-portfolio`.
- The vault has no project / role / achievement nodes yet → seed first.

## Required design constraints

- **Metric-first bullets** — every bullet contains a number (`%`, `x`,
  `$`, count, or duration). Rubric enforces ≥80% metric density via
  regex.
- **STAR / PAR per bullet** — situation/problem implied or stated, action
  active-voice, result quantified.
- **Active voice** — banned: "was responsible for", "helped to", "worked
  on", "was involved in".
- **No keyword stuffing** — ATS-friendly via real verbs and metrics, not
  hidden keywords.
- **Target persona** — `--target us-tech-senior`, `us-tech-mid`,
  `pm-product` each have tuned tone and bullet density.

## Two-turn pattern

Same writer/reviewer split as `render-jaso`:

1. Writer turn produces the resume markdown.
2. Reviewer turn re-loads `RUBRIC.md` fresh, runs the metric-density
   regex, scores action-verb diversity, ATS keyword coverage, vagueness
   banlist. Emits JSON.

## Final checklist

- Metric-density regex passed (≥80% bullets contain a number).
- Reviewer turn was a separate Claude context with fresh RUBRIC.md load.
- Concrete ontology slugs quoted (project / role / achievement).
- Active voice; no banned phrases.

## Files in this directory

```
SKILL.md
research-notes.md   citations with URL + ISO date + 2-sentence gloss
RUBRIC.md           (TODO) metric / verb / ATS / vagueness scoring
prompt-writer.md    (TODO)
prompt-reviewer.md  (TODO)
```
