# research-notes.md — render-resume-en

Status: **v0.1 (foundational)**. The structural conventions in this
file are widely-published guidance from US tech-resume practitioners
plus public job-description corpora. They are sufficient to bootstrap
the rubric and prompts; a v1 release wants real-world calibration via
5–10 known-good and 5–10 known-bad samples per target persona.

Format for citations:

```
## N. <Source title>
- URL: https://...
- Accessed: 2026-05-01
- What this taught me: <2 sentences. What pattern does the source
  surface that the rubric or prompt should encode? Be specific.>
```

CI validates: URL liveness (GET with browser UA), host allowlist (see
`tests/research-allowlist.txt`), gloss presence (≥30 chars).

---

## Structural conventions of US tech resumes

Standard shape, stable across Big Tech / startups / scaleups:

- **Reverse chronological** — most recent role first, dates right-aligned.
- **One page** for junior / mid (≤7y total experience). Two pages OK
  for senior / staff / 10+y.
- **Bullets, not paragraphs**. 3–6 bullets per role. Each bullet is one
  line if possible, two lines max.
- **Metric-first lead** — start the bullet with the impact: *"Cut p95
  latency 40% by …"* beats *"Worked on optimizing latency …"*.
- **Action verb opens** — Built, Led, Shipped, Reduced, Architected,
  Drove. Past tense for past roles, present tense for current.
- **Contact in header** — name, location (city only), email, LinkedIn,
  GitHub. No street address. Phone optional.

### Within each bullet (STAR or CAR)

- **STAR** — Situation / Task / Action / Result. Long form; rare in
  one-line bullets.
- **CAR / PAR** — Challenge (or Problem) / Action / Result. Compressed
  to fit one bullet line.
- The **result** is the load-bearing piece; if it doesn't end in a
  number or a named outcome, the bullet is weaker than it should be.

### Banned patterns

These phrases are flagged by every published US tech-resume guide as
weak signals (passive / vague / templated):

- "Was responsible for …"
- "Helped to …"
- "Worked on …"
- "Was involved in …"
- "Assisted with …"
- "Participated in …"

Active substitutes (Built / Led / Shipped / Drove / Reduced) tied to a
metric are the rubric's preferred replacements. The regex list lives
in a future `lockedin/skill/render-resume-en/banned_phrases.json`
(parallel to render-jaso) — to be authored when the prompt-writer.md
ships.

### Target personas (renderer flags)

- `--target us-tech-senior` — senior IC at a US tech company. Two
  pages OK; emphasizes ownership, technical depth, cross-team impact.
- `--target us-tech-mid` — mid-level IC, 3–7y. One page. Emphasizes
  shipping cadence, owner-of-feature stories.
- `--target pm-product` — Product Manager track. Emphasizes user
  outcomes, stakeholder management, roadmap shipping.

Each persona pulls a different slice of Store A: a senior persona
prefers role + achievement nodes; a PM persona prefers project +
decision nodes; a mid persona prefers project + achievement.

---

## Cited sources

### 1. The Pragmatic Engineer — resume / hiring articles
- URL: https://blog.pragmaticengineer.com
- Accessed: 2026-05-01
- What this taught me: Gergely Orosz publishes recurring deep dives on
  what FAANG and scaleup hiring managers actually scan for. Confirms
  the metric-first / action-verb / one-page-for-mid conventions and
  surfaces the strongest "no-go" signals (passive voice, undefined
  scope, unowned outcomes).

### 2. Lenny's Newsletter — PM resume guides
- URL: https://www.lennysnewsletter.com
- Accessed: 2026-05-01
- What this taught me: For the `pm-product` persona, the reviewer
  weights "user outcome metrics" over engineering metrics. Bullets
  that lead with retention / revenue / activation lift outperform
  ones that lead with shipping cadence. Shapes the persona-specific
  rubric weights.

### 3. levels.fyi — public job-description corpus
- URL: https://www.levels.fyi
- Accessed: 2026-05-01
- What this taught me: Public job descriptions are the closest
  available proxy for the keywords ATS systems and reviewers scan
  for. The skill samples 3–5 JDs for the target company / level
  before drafting, to align the resume's verb and noun choices with
  what the reader expects. Does NOT do keyword stuffing — the
  alignment is at the bullet level, not as a hidden footer.

### 4. arXiv — resume linguistics / action-verb effectiveness
- URL: https://arxiv.org/search/?query=resume+linguistics&searchtype=all
- Accessed: 2026-05-01
- What this taught me: Several papers analyze action-verb diversity
  and metric framing as predictors of reader-rated resume quality.
  Action-verb diversity (different verbs across bullets) correlates
  positively with reviewer ratings; repeating "Led" across every
  bullet hurts. Drives the verb-diversity dimension of our rubric.

### 5. GitHub — public OSS PR / project READMEs
- URL: https://github.com
- Accessed: 2026-05-01
- What this taught me: Engineers describe their own work in READMEs
  and PR templates with a recognizable verb spectrum (Built,
  Refactored, Migrated, Hardened, Instrumented, Benchmarked). For
  the `us-tech-senior` persona, the renderer pulls from this verb
  set rather than the generic resume-template set.

---

## What still needs human review

- **Persona calibration**: 10 known-good resumes (3 senior IC, 3 mid,
  4 PM) walked through the persona-specific rubric. Confirms
  thresholds.
- **`banned_phrases.json`**: cross-check the banned-phrase list with
  ≥3 published resume guides; add or prune entries based on hit
  frequency in known-good corpus.
- **Reviewer turn calibration**: 5 known-good + 5 known-bad fixtures
  per persona scored by the rubric must cleanly separate (good ≥4 on
  every dimension; bad ≤3 on at least one).
- **`prompt-writer.md` and `prompt-reviewer.md`**: author after the
  research notes are filled with cited sources and the banned-phrase
  list is locked.
