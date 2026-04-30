# RUBRIC.md — render-jaso scoring contract

The reviewer turn (`prompt-reviewer.md`) loads this file fresh and
scores the writer's draft against the five dimensions below. Output
schema is defined in `prompt-reviewer.md`; this file is the score
bands and the fixture authoring guide.

## Dimensions

### 1. 두괄식 (lead-with-conclusion)

The first paragraph contains the conclusion / 핵심 / 차별점. The rest
of the answer scaffolds the lead.

| Score | Band |
| --- | --- |
| 5.0 | Lead sentence is the thesis. Whole answer reads as proof. |
| 4.0 | Conclusion arrives within first 1–2 sentences. |
| 3.0 | Conclusion is in the first paragraph but buried mid-paragraph. |
| 2.0 | Conclusion arrives in the second paragraph. |
| 1.0 | Conclusion not stated, or arrives at the very end. |
| 0.0 | No identifiable conclusion. |

### 2. 구조화 (STAR / PAR / 4-question structure adherence)

Each body paragraph maps to one structural slot:

- For numbered prompts (지원동기 / 성장과정 / 등), the answer fits the
  named slot.
- Within each answer, paragraphs follow STAR (Situation / Task /
  Action / Result) or PAR (Problem / Action / Result).

| Score | Band |
| --- | --- |
| 5.0 | All paragraphs cleanly map to STAR/PAR; transitions explicit. |
| 4.0 | Most paragraphs map; one transition implicit but recoverable. |
| 3.0 | Half the paragraphs map; the rest read as continuous prose. |
| 2.0 | Structure is implied but a reviewer has to look for it. |
| 1.0 | Continuous prose, no discernible per-paragraph structure. |
| 0.0 | No structure at all (one block of text, no logical sequence). |

### 3. 구체성 (concreteness, ontology-grounded)

Numeric metrics, named projects, named technologies, named people.
Quoted ontology slugs (`[[role/lead-pm-fintech-2024]]`) count as
concrete and resolvable.

| Score | Band |
| --- | --- |
| 5.0 | Every claim backed by a metric or a named ontology node. |
| 4.0 | ≥80% of claims backed; rest are minor connective tissue. |
| 3.0 | Roughly half the claims backed; mix of concrete and vague. |
| 2.0 | A few concrete details; mostly generic adjectives. |
| 1.0 | No metrics, no names; just adjectives. |
| 0.0 | Generic content that could apply to any candidate. |

### 4. 표현 (no banned phrases, active voice)

Banned-phrase regex check (`banned_phrases.json`) is the gate. Each
hit reduces this dimension's score by 1.0 (floor 0). Active vs.
passive voice contributes the rest.

| Score | Band |
| --- | --- |
| 5.0 | Zero banned-phrase hits; consistently active voice. |
| 4.0 | Zero hits; one or two passive-voice sentences. |
| 3.0 | One banned-phrase hit; active voice otherwise. |
| 2.0 | Two banned-phrase hits OR consistent passive voice. |
| 1.0 | Three+ banned-phrase hits. |
| 0.0 | Templated language throughout. |

### 5. 적합성 (company / role fit)

The answer references at least one specific fact about the target
company / role / industry. A generic answer that could apply to any
company tops out at 2.0.

| Score | Band |
| --- | --- |
| 5.0 | Multiple specific company / role facts woven into the spine. |
| 4.0 | One specific company fact + one role fact. |
| 3.0 | One specific company fact OR one role fact. |
| 2.0 | Generic; could apply to any company in the industry. |
| 1.0 | Generic; could apply to any company anywhere. |
| 0.0 | Off-topic or contradictory to the role. |

## Pass criterion

`revisions_required` is **false** only when ALL of:

- Every dimension ≥ 4.0.
- `banned_phrase_hits` is empty.
- `missing_slugs` is empty (every quoted ontology slug resolves).

Otherwise the writer turn gets one revision cycle (max).

## Fixture authoring guide

Place 합격 (pass) and 불합격 (fail) golden fixtures under
`tests/fixtures/jaso/`:

```
tests/fixtures/jaso/
  pass/
    01-it-daekiyeop-1.md          (지원동기, IT 대기업, 합격)
    02-startup-pm-1.md            (1번 문항, 스타트업 PM, 합격)
    ...
  fail/
    01-templated-passive.md       (banned phrase + passive voice)
    02-no-company-fit.md          (generic content)
    ...
```

Each fixture is plain markdown with frontmatter:

```
---
expected_dimensions: { 두괄식: 4, 구조화: 4, 구체성: 4, 표현: 4, 적합성: 4 }
expected_revisions_required: false
prompt: 지원동기
company: <company>
notes: |
  Why this is a known good/bad sample.
---
<the 자소서 text>
```

Target sizes:

- 5 pass fixtures across 5 industries (IT 대기업, 외국계, 금융, 제조,
  스타트업).
- 5 fail fixtures, each isolating one failure mode (templated, passive
  voice, generic, missing structure, missing metrics).

CI's non-LLM portion checks banned phrases, structural markers, length
bounds. Nightly LLM portion records full rubric scores per fixture per
model version and alerts on ≥0.5 drift vs. the prior baseline.

## Refinement protocol

When the reviewer turn lands non-cleanly on a fixture (good fixture
scores < 4 on some dimension, or bad fixture scores ≥ 4 across the
board), refine THIS file's band definitions until separation is clean.
Do not retroactively change fixture labels — fixtures are the ground
truth, the rubric chases them.
