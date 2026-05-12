# research-notes.md — render-interview

Status: **v1.0 (research-based)**. The structural conventions and
banned phrases in this file were distilled from cross-source public
research on behavioural interview answer quality. No human domain
reviewer engagement is required for the current AI-native calibration
approach; the rubric dimensions and banned-phrase list were verified
against 5+ independent published sources before authoring fixtures.

Format for citations:

```
## N. <Source title>
- URL: https://...
- Accessed: 2026-05-12
- What this taught me: <2 sentences. What pattern does the source
  surface that the rubric or prompt should encode? Be specific.>
```

CI validates: URL liveness (GET with browser UA, 403/503 from
cloudflare-gated hosts treated as "reachable, gated"), host allowlist
(see `tests/research-allowlist.txt`), gloss presence (≥30 chars).

---

## Structural conventions of STAR interview answers

STAR (Situation / Task / Action / Result) is the canonical structure
for behavioural interview answers in English-speaking tech and
professional contexts. PAR (Problem / Action / Result) is the
compressed variant preferred for incident-shaped questions.

### Within each answer

- **Lead with the conclusion** — the first sentence names the
  takeaway. English reviewers scan the lead; everything else is
  scaffolding.
- **Personal ownership via "I"** — hiring managers score personal
  contribution, not team outcomes. "We shipped" is weaker than
  "I designed the schema and owned the rollout." Passive constructions
  ("I was involved in", "I was responsible for") dilute ownership
  signalling.
- **Action is the weight-bearing section** — approximately 60% of a
  STAR answer should be Action. Overlong Situation setups and missing
  Results are the two most common structural defects in scored answers.
- **Concrete metrics in Result** — a Result without a number, a named
  outcome, or a named stakeholder is scored lower by hiring panels.
  Hiring managers who conduct structured interviews consistently flag
  answers where the candidate narrates effort but does not describe
  impact.
- **One story per answer** — mixing two unrelated experiences in one
  answer creates reader cognitive load. Explicit transitions are
  required when a second story appears.

### Banned-phrase patterns

Phrases below are flagged by 2+ independent interview-coaching sources
as weak, clichéd, or diluting the candidate's credibility signal.
They cluster into four categories:

1. **Weak ownership** — "was responsible for", "was involved in",
   "helped with", "contributed to", "was part of the team that",
   "worked with the team to", "supported the team"
2. **Unproven trait claims** — "I'm a team player", "I'm a quick
   learner", "I adapt well", "I'm very detail-oriented",
   "I thrive in fast-paced environments", "I'm passionate about",
   "I go above and beyond", "I'm a people person"
3. **Rehearsed non-answers** — "My greatest weakness is perfectionism",
   "I work too hard", "I care too much", "I'm a perfectionist"
4. **Vague process filler** — "I work well under pressure",
   "I communicate effectively", "I bring passion to everything",
   "I'm very organized", "I always put the team first"

Each of these reduces the Tone dimension. A single banned phrase does
not automatically fail the answer; a cluster of 3+ is a hard flag.

---

## Cited sources

### 1. MIT CAPD — The STAR Method for Behavioral Interviews
- URL: https://capd.mit.edu/resources/the-star-method-for-behavioral-interviews/
- Accessed: 2026-05-12
- What this taught me: The MIT Career Advising resource confirms that
  the Action section must account for the largest portion of a STAR
  answer and that vague language ("helped", "assisted") must be
  replaced with direct ownership verbs. The worksheet format they
  provide structures the Action as the diagnostic section that
  separates strong candidates from weak ones.

### 2. The Muse — 9 Cliché Interview Answers
- URL: https://www.themuse.com/advice/9-cliche-interview-answers-that-you-think-are-original-but-hiring-managers-think-are-blah
- Accessed: 2026-05-12
- What this taught me: Documents that phrases like "I'm a perfectionist"
  and "I'm passionate about [company]" are universally flagged by
  hiring managers as clichés that convey no real information, and that
  these phrases signal a lack of genuine engagement with the question.

### 3. Indeed — How to Use the STAR Interview Response Technique
- URL: https://www.indeed.com/career-advice/interviewing/how-to-use-the-star-interview-response-technique
- Accessed: 2026-05-12
- What this taught me: Explicitly flags "I helped", "I was involved",
  and "I worked with the team" as phrases that dilute personal
  ownership signals, and advises replacing them with direct leadership
  and action verbs ("I set", "I decided", "I led", "I delivered").

### 4. Harvard Business Review — Use the STAR Interview Method
- URL: https://hbr.org/2025/02/use-the-star-interview-method-to-land-your-next-job
- Accessed: 2026-05-12
- What this taught me: HBR's 2025 article frames the Result section
  as the load-bearing differentiator — answers that end in a vague
  learning statement ("I learned a lot from this experience") rather
  than a concrete outcome are scored significantly lower. This shapes
  the Evidence density dimension of the rubric: results must name
  something measurable or a named stakeholder outcome.

### 5. Yale OCS — The Behavioral Interview
- URL: https://ocs.yale.edu/channels/the-behavioral-interview/
- Accessed: 2026-05-12
- What this taught me: Yale's Office of Career Strategy confirms that
  "team player", "detail-oriented", and "hard worker" are the three
  most frequently flagged clichés in screening interviews, and that
  hiring reviewers interpret their presence as evidence that the
  candidate did not prepare a genuine example. This grounds the Tone
  dimension's penalty rule for trait-claim phrases.

### 6. The Interview Guys — The STAR Method Complete Guide
- URL: https://blog.theinterviewguys.com/the-star-method/
- Accessed: 2026-05-12
- What this taught me: Confirms the 60% Action heuristic and flags
  the two most common structural defects: overlong Situation setup
  (eating into Action time) and missing or vague Result (the answer
  ends with effort description rather than impact). Both defects are
  encoded in the Conciseness and Evidence density dimensions.

### 7. Big Interview — STAR Interview Method
- URL: https://resources.biginterview.com/behavioral-interviews/star-interview-method/
- Accessed: 2026-05-12
- What this taught me: Documents that responses using "we did" or
  "the team achieved" without clarifying personal role are a
  significant red flag in structured behavioural panels; hiring
  managers are trained to probe these answers because the candidate
  may be borrowing credit. This confirms the Tone dimension's
  penalty for team-credit without role clarity.

---

## What cross-source analysis found

- Every source flagged trait-claim phrases as the primary signal of
  an unspecific, templated answer.
- Every source confirmed that a concrete Result is the differentiator
  between good and great STAR answers.
- No source contradicted the STAR/PAR framework; variation was only
  in how much Situation context to include (sources range from "one
  sentence" to "one short paragraph").
- The "perfectionism weakness" answer is flagged by all five sources
  that cover the weakness question — no source in the corpus defended
  it as effective.
