# RUBRIC.md — render-ideas scoring contract

The reviewer turn loads this file fresh and scores the set of ideas
against the five dimensions below. The rubric judges the set as a
whole, not each idea individually.

## Calibration status

**v1.1 foundational.** Dimension definitions below were distilled
from career-coaching and entrepreneur-advice practice. Cross-source
calibration (against a corpus of strong / weak idea sets generated
from real career graphs) is the v1.2 target. Until calibrated, the
reviewer turn produces self-consistent scores; those scores are less
rigorous than the jaso or resume-en rubric scores.

## Dimensions

### 1. Feasibility

Each idea respects the stated constraint (time, capital, skill,
audience). Wishful pitches that ignore the user's actual runway lose
points.

| Score | Band |
| --- | --- |
| 5.0 | Every idea is doable under the stated constraint within a clear horizon. |
| 4.0 | One idea is a stretch but the rest are doable. |
| 3.0 | Two ideas are stretchy; one is doable. |
| 2.0 | Most ideas ignore the constraint. |
| 1.0 | None of the ideas respect the user's actual runway. |
| 0.0 | Pure fantasy. |

### 2. Novelty

A good idea uses the user's existing skills in a combination they
have not used before. A bad idea recapitulates their last role with
a new label.

| Score | Band |
| --- | --- |
| 5.0 | Every idea sits in an unused skill / domain combination. |
| 4.0 | Most ideas surface novel combinations; one is adjacent to existing work. |
| 3.0 | Half the ideas are novel; half restate existing work. |
| 2.0 | Most ideas just rename existing work. |
| 1.0 | All ideas are repackaged versions of one project. |
| 0.0 | Generic ideas that could apply to anyone. |

### 3. Evidence ground

Each idea cites concrete vault entities (skills, projects,
achievements, decisions). Generic appeals to the user's
"experience" without naming entries lose points.

| Score | Band |
| --- | --- |
| 5.0 | Every idea cites at least two distinct vault entities and explains the connection. |
| 4.0 | Each idea cites at least one entity; the connection is explicit. |
| 3.0 | Some ideas cite entities; others speak in generalities. |
| 2.0 | Few ideas cite entities; the rest are abstract. |
| 1.0 | Almost no vault citations. |
| 0.0 | No grounding in user's actual experience. |

### 4. Scope match

The set spans different combinations rather than three variants of
the same idea. The user gets diversity, not redundancy.

| Score | Band |
| --- | --- |
| 5.0 | Each idea sits in a distinct skill × domain quadrant. |
| 4.0 | Three ideas span breadth; one overlaps slightly. |
| 3.0 | Two ideas overlap noticeably. |
| 2.0 | Three variants of the same idea. |
| 1.0 | All ideas restate one pitch. |
| 0.0 | One idea repeated with cosmetic changes. |

### 5. Motivation alignment

Ideas are framed around what the user said they care about (in the
vault: decisions, learning topics, recent project choices), not what
the LLM thinks they should care about.

| Score | Band |
| --- | --- |
| 5.0 | Each idea draws a clear thread to a stated motivation in the vault. |
| 4.0 | Most ideas align; one is reasonable but the connection is implicit. |
| 3.0 | Half the ideas align; the rest are speculative. |
| 2.0 | Few ideas track the user's stated motivations. |
| 1.0 | The set ignores motivation cues entirely. |
| 0.0 | Set actively contradicts the user's stated direction. |

## Pass criterion

`revisions_required` is **false** only when ALL of:

- Every dimension ≥ 4.0.
- `missing_slugs` is empty.

## Fixture authoring guide (v1.2 target)

Place pass and fail golden fixtures under
`tests/fixtures/ideas/{pass,fail}/`:

- `pass/`: 5 idea-set fixtures across constraint types (8-week side
  project, weekend prototype, career pivot, freelance launch, OSS
  contribution).
- `fail/`: 5 fixtures, each isolating ONE failure mode (infeasible,
  derivative, ungrounded, redundant, motivation-mismatch).

Fixtures not yet authored. Approach mirrors jaso and resume-en.
