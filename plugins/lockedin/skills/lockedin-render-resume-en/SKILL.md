---
name: lockedin-render-resume-en
description: |
  Writes an English resume from the user's experience, tuned to one
  of 10 built-in personas. Metric-first XYZ/CAR bullets, two-turn
  writer/reviewer with a 5-dimension rubric.

  Activate when the user says "render resume", "make a resume",
  "polish my resume", or names a target role. The writer turn loads
  the matching spec from ./personas/ before drafting.
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
- **Target persona** — 10 built-in personas under `./personas/`
  (us-tech-senior, us-tech-mid, pm-product, backend-senior,
  frontend-senior, mobile-senior, data-engineer-mid, ml-engineer-mid,
  designer-senior, marketing-mid). Each spec file contains tone
  guidance, action verb cluster, and persona-specific banned phrases.

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
research-notes.md           citations with URL + ISO date + 2-sentence gloss
RUBRIC.md                   5 dimensions; score bands; fixture authoring guide
prompt-writer.md            writer turn instruction
prompt-reviewer.md          reviewer turn instruction (separate Claude context)
banned_phrases.json         regex list of weak / vague / templated phrases
personas/
  us-tech-senior.md         Senior IC / Staff / Principal
  us-tech-mid.md            Mid-level IC (3-7y)
  pm-product.md             Product Manager
  backend-senior.md         Senior backend engineer, distributed systems focus
  frontend-senior.md        Senior frontend engineer, perf + design system focus
  mobile-senior.md          Senior iOS/Android engineer
  data-engineer-mid.md      Mid-level data engineer, dbt/Airflow/warehouse
  ml-engineer-mid.md        Mid-level ML engineer, classical ML productization
  designer-senior.md        Senior product / UX designer
  marketing-mid.md          Mid-level growth / product marketing manager
```
