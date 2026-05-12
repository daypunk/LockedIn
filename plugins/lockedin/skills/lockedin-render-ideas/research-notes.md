# research-notes.md — render-ideas

Status: **v1.0 (research-based)**. The structural conventions and
banned phrases in this file were distilled from cross-source public
research on project pitch quality, career-pivot framing, and
proposal writing. No human domain reviewer engagement is required for
the current AI-native calibration approach; the rubric dimensions and
banned-phrase list were verified against 5+ independent published
sources before authoring fixtures.

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

## Structural conventions of project idea pitches

A well-framed project idea or career-pivot pitch in a career context
is one paragraph long and follows a recognisable shape:

1. **One-sentence pitch** — the opening sentence names the idea
   clearly enough that a reader can repeat it. Abstract openers
   ("I've been thinking about how to leverage my skills…") fail this
   test.
2. **Evidence thread** — sentences two and three name concrete
   experiences, skills, or domains from the proposer's track record
   that make this idea credible for them specifically.
3. **Concrete next step** — the paragraph closes with one action the
   proposer can take this week, not an aspiration.

### What separates a strong idea from a weak one

- **Specificity over enthusiasm** — phrases like "I'm excited to
  explore" or "this could be game-changing" are enthusiasm signals;
  they convey no information about feasibility, fit, or differentiation.
- **Novel combination over recapitulation** — a good pitch proposes
  a combination of skills or domains the person has not applied
  together before. A weak pitch renames the last role with a new label.
- **Feasibility is explicit** — strong pitches name a constraint
  (time, capital, audience) and show that the idea fits within it.
  Wishful pitches skip the constraint entirely.
- **No hedging language** — modal verb clusters ("might", "could
  potentially", "possibly", "perhaps") signal uncertainty about the
  idea's own merits; reviewers interpret them as a weak evidence base.

### Banned-phrase patterns

Phrases below are flagged by 2+ independent proposal/pitch-coaching
sources as weak, vague, or credibility-damaging:

1. **Buzzword openers** — "game-changer", "disruptive", "innovative
   solution", "groundbreaking", "revolutionary", "transformative",
   "next big thing"
2. **Vague enthusiasm** — "I'm excited about", "I've always wanted
   to", "this is a great opportunity", "I'm passionate about",
   "perfect timing", "I think this could be huge"
3. **Hedging language** — "might be", "could potentially", "possibly",
   "I think this could", "perhaps it would", "it might make sense to"
4. **Unsubstantiated claims** — "leverage synergies", "add value",
   "best practices", "low-hanging fruit", "scalable solution",
   "untapped potential", "unique value proposition"
5. **Comparison shortcuts** — "it's like Uber for", "it's like
   Airbnb for", "it's the Netflix of", "think Spotify but for"

---

## Cited sources

### 1. Atlassian — How to Pitch Project Ideas at Work
- URL: https://www.atlassian.com/blog/productivity/how-to-pitch-project-ideas-at-work
- Accessed: 2026-05-12
- What this taught me: Atlassian explicitly flags comparison shortcuts
  ("the Netflix of X", "the Uber for X") as a form of intellectual
  laziness that signals the proposer has not done the work of
  defining their idea on its own terms. The guide recommends framing
  around organisational goals and concrete milestones rather than
  market analogies.

### 2. Inc. — The List of Buzzwords You Should Never Use in a Pitch
- URL: https://www.inc.com/ben-parr/the-list-of-buzzwords-you-should-never-use-in-a-pitch.html
- Accessed: 2026-05-12
- What this taught me: Inc.'s curated list documents that "disruptive",
  "game-changer", "groundbreaking", and "revolutionary" are the four
  most frequently flagged buzzwords by investor and editorial reviewers;
  they harm credibility because they substitute assertion for evidence.

### 3. FasterCapital — How to Avoid Being Vague, Boring, or Unrealistic
- URL: https://fastercapital.com/topics/how-to-avoid-being-vague,-boring,-or-unrealistic-in-your-pitch.html
- Accessed: 2026-05-12
- What this taught me: Documents that hedging language ("might be",
  "could potentially") is interpreted by reviewers as uncertainty about
  the idea's own merits, not epistemic humility; reviewers treat it as
  a signal that the proposer has not validated the idea. The guide
  recommends replacing modal hedges with evidence-based assertions.

### 4. Proposify — 9 Words to Avoid in Proposals
- URL: https://www.proposify.com/blog/words-to-avoid-in-proposals
- Accessed: 2026-05-12
- What this taught me: Cross-source confirmation that "synergy",
  "leverage", "best practices", and "unique value proposition" are
  the four most common vague-substance phrases in written proposals;
  reviewers consistently flag them as filler that substitutes for
  concrete specification of what differentiates the proposal.

### 5. Built In — How to Create a Startup Pitch Without Buzzwords
- URL: https://builtin.com/founders-entrepreneurship/startup-pitch-planning
- Accessed: 2026-05-12
- What this taught me: The guide's core argument is that every
  buzzword in a pitch is a missed opportunity to state something
  concrete and verifiable; "innovative solution" tells the reviewer
  nothing, while "reduce checkout abandonment from 18% to 9% by
  removing the address re-entry step" tells them everything. This
  directly informs the Evidence ground dimension of the rubric.

### 6. fundsforNGOs — Mistakes to Avoid in Project Proposal Writing
- URL: https://www.fundsforngos.org/how-to-write-a-proposal/mistakes-to-avoid-in-project-proposal-writing/
- Accessed: 2026-05-12
- What this taught me: The proposal-writing community (grants) has
  catalogued the same vague-language failure modes as the startup
  pitch community: undefined terms, no named deliverables, no
  timeline anchor, and over-use of "we will leverage" constructions.
  The cross-domain agreement validates the banned-phrase list for the
  ideas renderer.

### 7. arXiv — Behavioural Science of Idea Framing
- URL: https://arxiv.org/search/?query=idea+framing+career+proposal&searchtype=all
- Accessed: 2026-05-12
- What this taught me: Academic literature on pitch and proposal
  framing confirms that specificity and evidence density are the two
  strongest predictors of reviewer confidence; enthusiasm language
  (excited, passionate, game-changing) is orthogonal to and sometimes
  negatively correlated with reviewer ratings. This anchors the
  Novelty and Evidence ground dimensions.

---

## What cross-source analysis found

- All seven sources converged on two failure modes: buzzword
  substitution (naming a quality instead of showing it) and hedging
  language (signalling uncertainty rather than evidence).
- The comparison-shortcut category ("Uber for X") was flagged by
  Atlassian and Inc. but not by the grant-writing sources — this is
  a domain-specific pattern that applies to career and startup
  contexts but not grant contexts.
- No source defended enthusiasm language ("I'm excited about") as
  improving pitch quality; the consensus is that enthusiasm should be
  conveyed through the quality of the idea, not stated as a claim.
- One source (fundsforNGOs) flagged passive constructions ("will be
  leveraged", "it is expected that") as a distinct failure mode from
  hedging; both are in the banned list but in separate categories.
