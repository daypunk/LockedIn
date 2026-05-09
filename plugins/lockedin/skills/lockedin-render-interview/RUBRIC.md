# RUBRIC.md — render-interview scoring contract

The reviewer turn loads this file fresh and scores the writer's
draft against the five dimensions below.

## Calibration status

**v1.1 foundational.** The dimension definitions below were
distilled from interview-coaching practice; cross-source calibration
(against published interview research and a fixture corpus of
strong / weak answers) is the v1.2 target. Until the rubric is
calibrated, the reviewer turn produces self-consistent scores
against the bands here, but those scores are less rigorous than the
jaso and resume-en rubric scores.

## Dimensions

### 1. Clarity

The answer's main point lands within the first sentence (English) or
the first paragraph (Korean). The rest of the answer scaffolds the
lead.

| Score | Band |
| --- | --- |
| 5.0 | Lead sentence is the takeaway; entire answer reads as proof. |
| 4.0 | Takeaway arrives in the first one or two sentences. |
| 3.0 | Takeaway buried mid-paragraph. |
| 2.0 | Takeaway arrives in the second paragraph. |
| 1.0 | Takeaway implicit; reader must reconstruct. |
| 0.0 | No identifiable takeaway. |

### 2. Evidence density

Concrete entities, metrics, or named systems anchor the claim. Slug
citations (`[[type/slug]]`) count as evidence when they resolve to
real vault entries.

| Score | Band |
| --- | --- |
| 5.0 | Every claim backed by a metric or a named entity. |
| 4.0 | ≥80% of claims backed; rest are minor connective tissue. |
| 3.0 | Roughly half the claims backed. |
| 2.0 | A few concrete details; mostly generic adjectives. |
| 1.0 | No metrics, no named entities. |
| 0.0 | Generic content that could apply to any candidate. |

### 3. Persona fit

The answer's register matches the target role and the question's
shape. Engineer answers carry stack and decision detail; PM answers
carry user-outcome and stakeholder detail; designer answers carry
craft and trade-off detail.

| Score | Band |
| --- | --- |
| 5.0 | Voice matches; reviewer cannot tell it isn't hand-written for the persona. |
| 4.0 | Persona match strong; one or two sentences drift. |
| 3.0 | Persona recognisable but generic. |
| 2.0 | Wrong emphasis for persona. |
| 1.0 | Persona ignored. |
| 0.0 | Fundamentally mismatched. |

### 4. Conciseness

The answer respects the word limit and avoids filler. Length is
appropriate to the question; behavioural answers run longer than
soundbites, but neither overflow nor pad.

| Score | Band |
| --- | --- |
| 5.0 | Within ±10% of word limit; no filler. |
| 4.0 | Within ±20% of word limit; minimal filler. |
| 3.0 | Slightly over or under; some filler. |
| 2.0 | Notably over or under; obvious filler. |
| 1.0 | Way out of bounds. |
| 0.0 | Pure padding or trivially short. |

### 5. Tone

Active voice. Confident without arrogant. Past tense for past
stories. No banned phrases ("I'm a hard worker", "team player",
"passionate about...", "responsible for...").

| Score | Band |
| --- | --- |
| 5.0 | Active, confident, evidence-grounded throughout. |
| 4.0 | One or two passive or filler phrases. |
| 3.0 | Three or more weak verbs or filler phrases. |
| 2.0 | Frequent passive voice or buzzword filler. |
| 1.0 | Templated language throughout. |
| 0.0 | Off-topic or contradictory to the question. |

## Pass criterion

`revisions_required` is **false** only when ALL of:

- Every dimension ≥ 4.0.
- `missing_slugs` is empty.

## Fixture authoring guide (v1.2 target)

Place pass and fail golden fixtures under
`tests/fixtures/interview/{pass,fail}/`:

- `pass/`: 5 fixtures across question types (behavioural,
  technical, motivation, conflict, failure-recovery).
- `fail/`: 5 fixtures, each isolating ONE failure mode (no metrics,
  generic, wrong persona, banned phrases, padded).

Fixtures are not yet authored. The schema and calibration approach
follow the jaso and resume-en patterns.
