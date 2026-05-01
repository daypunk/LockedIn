# reviewers.md — render-jaso domain reviewer

The 자소서 rubric is culturally specific. v1.0 ships with
**research-based calibration** — dimension definitions and bands were
derived from cross-source consensus across 9+ Korean job-application
guides, including HR-survey-based banned-phrase frequency data. v1.1
calibration target: a named human domain reviewer walks through the
golden fixture set (`tests/fixtures/jaso/{pass,fail}/`) with
`RUBRIC.md` and confirms the score bands cleanly separate good from
bad.

## Status

**v1.0** — research-based calibration; named human reviewer
**awaited** for v1.1. The renderer is fully functional today;
calibration is the polish step.

## Reviewer profile (target)

- Has read or written successful 자소서 in the past 2 years.
- Has worked in or hired for at least 2 industries from the v1 target
  set (IT 대기업, 외국계, 금융, 제조, 스타트업).
- Comfortable reading 5 pass + 5 fail fixtures and noting where the
  rubric over- or under-rates each. ~2–3 hour async engagement.

## Engagement format

1. Reviewer reads `RUBRIC.md`
   (`plugins/selfgraph/skills/selfgraph-render-jaso/RUBRIC.md`).
2. Reviewer scores each fixture on the five dimensions independently.
3. Reviewer's scores compared to `expected_dimensions` in fixture
   frontmatter. Disagreements documented in a follow-up
   `reviewers-notes.md`.
4. Rubric band definitions refined based on disagreements (rubric
   chases the reviewer, not vice-versa).
5. Reviewer signs off; their name and a fallback contact channel are
   committed below in this file with the v1.1 release.

## Onboarding

If you fit the reviewer profile, please open an issue using the
[Korean reviewer onboarding template](../../../../.github/ISSUE_TEMPLATE/korean_reviewer_onboarding.yml).
The maintainer will reach out privately to coordinate the engagement.

## v1.0 calibration sources (research-based)

The current rubric and banned-phrase list draw from cross-source
consensus across:

- 워크넷 (한국고용정보원) 자기소개서 작성 가이드.
- 잡코리아 자소서 작성법 / 합격자소서 / 인사담당자 평가 article 군.
- 사람인 자기소개서 가이드.
- 링커리어 자소서 작성 팁 article 군.
- 캐치 (catch.co.kr) 합격 자소서 분석 시리즈.
- 하이잡 (haijob.co.kr) 항목별 작성법 시리즈.
- 경향신문 / 한국일보 / 한경 매거진 인사담당자 인터뷰 기사
  (성실 49.2% / 노력 36.3% / 책임감 28.5% 등 진부 단어 통계).
- brunch.co.kr 커리어 작가 시리즈 (jobplanet / careernerds /
  jobcheatkey 등).
- 학회·매거진 발표 자료 (한경 매거진 KKK STAR 시리즈 등).

These sources informed:

- The 5 dimensions of `RUBRIC.md` and their score bands.
- The cross-source confirmed banned-phrase list in
  `banned_phrases.json` (each entry verified across 3+ sources).
- The structural conventions in `prompt-writer.md` (두괄식 + STAR +
  ontology slug references + 회사 fit signal).
- The fixture coverage matrix (5 industries × 5 failure modes).

## Fallback channel

If no human reviewer is named by a v1.1 release, the skill ships with
the v1.0 research-based calibration intact. The HUD surfaces the
calibration status via the SKILL.md description; end users can still
use the renderer and see the disclaimer in the reviewer-turn JSON
output's `notes` array.

## Names (filled in with v1.1 release)

```
Reviewer:           [v1.1 — open call via .github/ISSUE_TEMPLATE/korean_reviewer_onboarding.yml]
Industries covered: [v1.1]
Engagement date:    [v1.1]
Fallback contact:   [v1.1]
```
