# reviewers.md — render-jaso domain reviewer

The 자소서 rubric is culturally specific. To ship v1 of `render-jaso`,
at least one named human reviewer must walk through the golden fixture
set (`tests/fixtures/jaso/{pass,fail}/`) with `RUBRIC.md` and confirm
that the score bands cleanly separate good from bad. Without a named
reviewer the LLM's self-evaluation is the only signal, which is not
enough for a domain this culturally embedded.

## Status

**TBD.** This file ships as a placeholder; v1 release of `render-jaso`
is blocked until the reviewer is identified and signs off.

## Reviewer profile (target)

- Has read or written successful 자소서 in the past 2 years.
- Has worked in or hired for at least 2 industries from the v1 target
  set (IT 대기업, 외국계, 금융, 제조, 스타트업).
- Comfortable reading 5 pass + 5 fail fixtures and noting where the
  rubric over- or under-rates each. ~2–3 hour engagement.

## Engagement format (proposed)

1. Reviewer reads `RUBRIC.md` (`selfgraph/skill/render-jaso/RUBRIC.md`).
2. Reviewer scores each fixture on the five dimensions independently.
3. Reviewer's scores compared to `expected_dimensions` in fixture
   frontmatter. Disagreements documented in a follow-up
   `reviewers-notes.md`.
4. Rubric band definitions refined based on disagreements (rubric
   chases the reviewer, not vice-versa).
5. Reviewer signs off; their name and a fallback contact channel are
   committed below in this file before the v1 release.

## Fallback channel

If no reviewer is named by the time v1 ships, the skill marks itself
as "v0.1 — rubric uncalibrated" in the SKILL.md description and the
HUD shows a warning state when `render-jaso` is invoked. End users
can still use it; they just see the disclaimer.

## Names (filled in by maintainer)

```
Reviewer:           TBD
Industries covered: TBD
Engagement date:    TBD
Fallback channel:   TBD
```
