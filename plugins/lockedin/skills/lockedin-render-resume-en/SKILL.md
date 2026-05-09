---
name: lockedin-render-resume-en
description: |
  Render an English resume from the lockedin ontology — metric-first
  bullets in XYZ or CAR shape ("Accomplished X as measured by Y by
  doing Z" / Challenge-Action-Result), target persona (us-tech-senior
  / us-tech-mid / pm-product). Two-turn writer/reviewer pattern with a
  JSON rubric (≥80% metric density floor, action-verb diversity, no
  weak verbs).

  Use when the user says: "render resume", "make a resume",
  "us-tech-senior resume", "resume for [target]", "polish my resume".
  Output: a markdown resume quoting concrete ontology slugs plus a JSON
  rubric score.
---

# render-resume-en

Research-based calibration. Ships with full rubric, writer and
reviewer prompts, and a banned-phrase regex list. Dimension
definitions derived from cross-source consensus across 20+ US tech
resume guides. See `research-notes.md` for citations.

## Use this when

- User asks for an English resume targeting a tech / PM persona.
- User wants their existing resume "polished" against the rubric.

## Do NOT use when

- User wants a Korean cover letter → `render-jaso`.
- The vault has no project / role / achievement nodes yet → seed first.

## Required design constraints

- **Metric-first bullets** — every bullet contains a number (`%`, `x`,
  `$`, count, or duration). Rubric enforces ≥80% metric density via
  regex.
- **XYZ or CAR per bullet** — XYZ = "Accomplished X as measured by Y,
  by doing Z"; CAR = Challenge / Action / Result compressed to one
  bullet line. Active voice, quantified result. (STAR is the implicit
  story arc; XYZ/CAR is the bullet shape.)
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
research-notes.md     citations with URL + ISO date + 2-sentence gloss
RUBRIC.md             5 dimensions; score bands; fixture authoring guide
prompt-writer.md      writer turn instruction
prompt-reviewer.md    reviewer turn instruction (separate Claude context)
banned_phrases.json   regex list of weak / vague / templated phrases
```
