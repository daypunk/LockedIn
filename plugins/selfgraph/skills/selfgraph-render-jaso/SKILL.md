---
name: selfgraph-render-jaso
description: |
  Render a Korean 자기소개서 from the selfgraph ontology, in 두괄식 +
  STAR/PAR structure, with banned-phrase filtering and self-evaluation
  against a 5-dimension rubric. Two-turn writer/reviewer pattern emits a
  JSON score so the user knows if the draft is ready to submit.

  Use when the user says: "자소서", "자기소개서", "render jaso", "회사 X
  자소서 N번 문항", "지원동기 써줘", "성장과정 써줘", "입사 후 포부", or
  names a Korean company plus a 자소서 question. Input: company name,
  question id or text, optional 직무. Output: a Korean cover letter
  quoting concrete ontology slugs plus a JSON rubric score.
---

# render-jaso

Research-based calibration. RUBRIC.md ships with five dimensions and
score bands. prompt-writer.md, prompt-reviewer.md, and
banned_phrases.json (28 cross-source-confirmed entries) all ship.
Named human domain reviewer engagement is in progress. See
`reviewers.md` for the engagement format.

## Use this when

- User names a Korean company and asks to write a 자소서.
- User points at a 자소서 question (e.g., 지원동기 / 성장과정 / 성격의
  장단점 / 입사 후 포부).
- User asks to "polish my 자소서" against the rubric.

## Do NOT use when

- User wants an English resume → use `render-resume-en`.
- The vault is empty (no ontology nodes to quote) → seed first via
  `/selfgraph init` or `selfgraph init --fixture FILE`.

## Required design constraints (locked)

1. **두괄식** — conclusion / 핵심 / 차별점 in the first paragraph; the
   rest of the answer scaffolds the lead.
2. **구조화된 문맥** — within Korean 4-question convention (지원동기 /
   성장과정 / 성격의 장단점 / 입사 후 포부 etc.), use STAR or PAR per
   paragraph.
3. **두루뭉술한 표현 제거** — banned-phrase regex check runs **before**
   the reviewer rubric pass. See `banned_phrases.json`.
4. **초개인화된 경험 기반** — every claim quotes a concrete ontology
   node by slug (e.g., `[[role/lead-pm-fintech-2024]]`). Vague
   generalities cost the 구체성 dimension.
5. **회사·직무 fit** — query the ontology for nodes with edges to the
   target company / 직무 / industry; surface the top-3 most relevant
   before drafting.

## Two-turn writer/reviewer pattern

Run as **two separate Claude turns**:

1. **Writer turn** — produce the 자소서 draft. Quote ontology slugs.
   Apply banned-phrase filter to the draft.
2. **Reviewer turn** — clear the writer context. Re-load `RUBRIC.md`
   fresh. Score on `두괄식 / 구조화 / 구체성 / 표현 / 적합성` (0–5
   each). Emit JSON. If any dimension < 4 OR `revisions_required: true`,
   return to the writer turn once with the review notes.

Same-turn self-evaluation inflates scores by ~1 point. Do not skip the
separation.

## Final checklist

- Banned-phrase regex pass ran (and was clean) before rubric.
- Reviewer turn was a separate Claude context with fresh RUBRIC.md load.
- Output JSON has all 5 dimensions ≥ 4 (or one revise cycle ran).
- Concrete ontology slugs are quoted in the rendered text.

## Files in this directory

```
SKILL.md            (this file)
research-notes.md   citations with URL + ISO date + 2-sentence gloss
RUBRIC.md           5-dimension scoring contract + score bands
banned_phrases.json 28 cross-source-confirmed regex entries
prompt-writer.md    writer-turn prompt
prompt-reviewer.md  reviewer-turn prompt (re-loaded fresh)
reviewers.md        engagement format; v1.1 named reviewer placeholder
```
