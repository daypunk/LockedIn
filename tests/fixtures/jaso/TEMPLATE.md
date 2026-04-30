---
# Fixture authoring template for tests/fixtures/jaso/{pass,fail}/
#
# Required frontmatter:
expected_dimensions:
  두괄식: 4       # 0–5 expected band
  구조화: 4
  구체성: 4
  표현: 4
  적합성: 4
expected_revisions_required: false
prompt: 지원동기            # canonical slot or company-specific question
company: <company>          # target company at the time of writing
industry: <industry>        # IT 대기업 / 외국계 / 금융 / 제조 / 스타트업
notes: |
  Why this is a known good (or known bad) sample. One paragraph.
  Cite the source (anonymized link to Linkareer / 사람인 / etc., or
  "self-authored composite") and the failure mode it isolates if any.
---

자소서 본문은 여기에. 한 문항당 1 fixture. 한국어 자연스럽게.
구체 ontology 슬러그를 인용하려면 [[type/slug]] 형식.

CI's non-LLM portion checks: banned-phrase regex against
`banned_phrases.json`, structural markers (paragraph count,
length bounds), and that the labeled `expected_dimensions` are
plausible (rubric reviewer pass produces scores within ±0.5 of
expected for `pass/` fixtures, and below 4 on at least one
dimension for `fail/` fixtures).

Authoring policy:
- `pass/` should span 5 industries (IT 대기업, 외국계, 금융, 제조,
  스타트업).
- `fail/` should each isolate ONE failure mode: templated phrasing,
  passive voice, generic / no-company-fit, missing structure,
  missing metrics.
- Sources can be:
  - Public 합격 자소서 from Linkareer (anonymized; remove names)
  - Self-authored composites the domain reviewer signs off on
- Do NOT include real names, contact info, or anything PII-heavy.
- Keep the body under 1500 자 per fixture.
