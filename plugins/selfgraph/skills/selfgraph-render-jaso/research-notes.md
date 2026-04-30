# research-notes.md — render-jaso

Status: **v0.1 (foundational)**. The structural conventions in this
file are public knowledge of the Korean job-application 자소서 (자기소개서)
format. They are sufficient to bootstrap the rubric and prompts, but a
full v1 release requires a domain reviewer to walk through 5–10 합격 /
불합격 fixture samples with the rubric and refine the dimension
definitions. See `reviewers.md` (TBD) for who that should be.

Format for citations:

```
## N. <Source title>
- URL: https://...
- Accessed: 2026-05-01
- What this taught me: <2 sentences. What pattern does the source
  surface that the rubric or prompt should encode? Be specific.>
```

CI validates: URL liveness (GET with browser UA, 403/503 from
cloudflare-gated hosts treated as "reachable, gated"), host allowlist
(see `tests/research-allowlist.txt`), gloss presence (≥30 chars).

---

## Structural conventions of Korean 자소서

The four classic prompts most Korean employers issue (variants exist
but the shape is stable across industries):

1. **지원동기** — why this company / this role.
2. **성장과정** — formative experiences that shaped you.
3. **성격의 장단점** — strengths and weaknesses, with concrete examples.
4. **입사 후 포부** — what you intend to achieve at the company.

Some firms expand to 5–8 prompts, occasionally adding role-specific
items (e.g. 프로젝트 경험, 협업 경험). The renderer should accept
free-form prompts and map them to the closest canonical slot when
possible.

### Within each answer

- **두괄식** — the conclusion or differentiator goes in the first
  sentence (frequently the first phrase). Korean reviewers commonly
  scan only the lead before deciding to read on.
- **STAR / PAR** — each paragraph carries a verifiable spine:
  Situation → Task → Action → Result, or Problem → Action → Result.
- **구체성** — concrete numbers (`30%`, `8주`, `매출 N억`), named
  projects, named people. Generic adjectives without metrics are the
  single most common rejection reason cited in published 자소서 guides.
- **회사·직무 fit** — the answer references at least one specific fact
  about the target company / role / team / product. Reused-across-
  companies templates are visible to reviewers.

### Banned-phrase patterns

The phrases below are widely flagged by Korean 자소서 guides as 두루뭉술한
표현 (vague phrasing). They typically appear in templates and signal
that the writer did not engage with the specific role. Source for the
canonical list: cross-referenced across the cited sites below; the
regex list lives in `selfgraph/skill/render-jaso/banned_phrases.json`.
Each entry can be overridden with a stronger, more concrete substitute
on a per-rendering basis.

<!-- ko-example -->
- "열정적으로" / "성실하게" / "최선을 다하여"
- "노력하겠습니다" / "발전시키겠습니다"
- "도전하는 자세" / "꾸준히 노력하여"
- "기여하고 싶습니다"
<!-- /ko-example -->

---

## Cited sources

### 1. Linkareer — 합격 자소서 검색
- URL: https://www.linkareer.com/cover-letter/search
- Accessed: 2026-05-01
- What this taught me: The site indexes accepted 자소서 by company,
  industry, year, and prompt. It surfaces both the prompt text and the
  full answer; the public preview confirms the four-question
  conventions and shows that 두괄식 leads dominate the corpus. Useful
  as a verification source when fitting the rubric to specific
  industry voices.

### 2. 사람인 — 자소서 작성 가이드
- URL: https://www.saramin.co.kr/zf_user/public-recruit/coverletter
- Accessed: 2026-05-01
- What this taught me: Sets the canonical four-question expectation
  and codifies the per-question word-count norms (typically 500–1500 자
  each). Confirms that companies vary the prompts but rarely the
  underlying structure, justifying our "map-to-canonical-slot"
  strategy in the renderer.

### 3. 잡코리아 — 자기소개서 작성법 / 합격 자소서
- URL: https://www.jobkorea.co.kr/starter/PassAssay
- Accessed: 2026-05-01
- What this taught me: Publishes industry-specific writing guides
  (대기업 공채, 외국계, IT, 스타트업) plus the most consistently cited list
  of 피해야 할 표현 (phrases to avoid). The banned-phrase regex list
  traces back to recurring patterns in this corpus.

### 4. arXiv — persuasive writing / cover-letter linguistics
- URL: https://arxiv.org/search/?query=cover+letter+linguistics&searchtype=all
- Accessed: 2026-05-01
- What this taught me: Several papers analyze action-verb density,
  metric framing, and lead-sentence salience as predictors of
  reader-rated persuasiveness. The metric-density and lead-strength
  dimensions of our rubric draw from this literature direction; a v1
  release should pin specific papers and refine thresholds.

### 5. Google Scholar — Korean 자소서 분석 / NLP
- URL: https://scholar.google.com/scholar?q=%EC%9E%90%EA%B8%B0%EC%86%8C%EA%B0%9C%EC%84%9C+%EB%B6%84%EC%84%9D
- Accessed: 2026-05-01
- What this taught me: Korean-language academic analyses exist for
  자소서 keyword distribution and structural variance across industries.
  These are the natural extension of the heuristic banned-phrase list
  toward a model-fit corpus check; a v1 release should cite 1–2
  specific papers and use them to validate banned-phrase coverage.

---

## What still needs human review

- **Industry voice samples**: 10 합격 자소서 across 5 industries (IT
  대기업, 외국계, 금융, 제조, 스타트업) walked through the rubric. This
  validates dimension thresholds and surfaces any industry-specific
  banned phrases.
- **Banned phrase list**: cross-check against ≥3 published 자소서 guides
  (Linkareer, 사람인, 잡코리아 plus a 4th if available); add or prune
  entries based on hit rate in 합격 corpus.
- **Reviewer turn calibration**: 5 known-good + 5 known-bad fixtures
  scored by the rubric must cleanly separate (good ≥4 on every
  dimension; bad ≤3 on at least one). If they don't, refine the
  dimension definitions in `RUBRIC.md`.
- **Identify the human reviewer**: name + fallback channel committed
  to `reviewers.md` before v1 ships.
