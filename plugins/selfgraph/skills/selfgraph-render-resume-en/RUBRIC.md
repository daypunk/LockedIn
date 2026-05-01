# RUBRIC.md — render-resume-en scoring contract

The reviewer turn (`prompt-reviewer.md`) loads this file fresh and
scores the writer's draft against the five dimensions below. Output
schema is defined in `prompt-reviewer.md`; this file is the score
bands and the fixture authoring guide.

The dimensions are derived from cross-source consensus across the US
tech-resume corpus (see `research-notes.md` for citations). Every
dimension definition was confirmed by 3+ independent guides; single-
source signals were rejected.

## Dimensions

### 1. Metric Density (impact-first bullets)

Every meaningful bullet leads with — or is anchored by — a
quantifiable outcome (%, $, count, duration, ratio, or a named outcome
that is verifiable). The XYZ formula ("Accomplished X as measured by
Y, by doing Z") is the canonical shape.

| Score | Band |
| --- | --- |
| 5.0 | ≥90% of bullets metric-anchored. Every metric is specific (no "improved performance"). |
| 4.0 | ≥80% metric-anchored. Remaining bullets are summary or tools-list. |
| 3.0 | 60–80% metric-anchored. Some bullets describe activity without outcome. |
| 2.0 | 40–60% metric-anchored. Many bullets read as responsibility lists. |
| 1.0 | <40% metric-anchored. Resume reads as duties, not impact. |
| 0.0 | No metrics anywhere. |

### 2. Action Verb Quality (active voice + diversity)

Each bullet starts with a strong action verb (Built, Led, Shipped,
Reduced, Architected, Drove, Owned, Migrated, Hardened, Instrumented).
Past tense for past roles, present tense for current. Verb repetition
is penalized: ≥3 different lead verbs across any 5 consecutive bullets.

| Score | Band |
| --- | --- |
| 5.0 | Every bullet starts with an active verb. ≥6 distinct verbs across the document. |
| 4.0 | Every bullet starts with an active verb. 4–5 distinct verbs (mild repetition). |
| 3.0 | One or two bullets passive or weak-verb led; verbs otherwise active. |
| 2.0 | 3+ bullets passive / "responsible for" / "helped" led. |
| 1.0 | Half or more of bullets passive or weak-verb led. |
| 0.0 | Predominantly passive / responsibility-list voice. |

### 3. Structural Adherence (XYZ, length, format)

- Bullets follow XYZ or CAR (Challenge / Action / Result).
- Length: ≤1 page for ≤8y total experience; ≤2 pages for 8y+ /
  staff / principal / EM.
- 3–6 bullets per recent role / 2–3 per older roles.
- Reverse chronological. ATS-clean format (no graphics, no columns,
  no tables).

| Score | Band |
| --- | --- |
| 5.0 | All bullets XYZ or CAR; length matches persona; ATS-clean. |
| 4.0 | Most bullets XYZ; 1–2 transitions implicit but recoverable; length matches. |
| 3.0 | About half XYZ; some bullets read as continuous prose; length acceptable. |
| 2.0 | Structure is implied but reviewer must look for it; length is a stretch. |
| 1.0 | Continuous prose; length wrong for persona; format ATS-hostile. |
| 0.0 | No structure (paragraph format) or critically wrong length / format. |

### 4. Banned Phrase Cleanliness

Banned-phrase regex check (`banned_phrases.json`) is the gate. Each
hit reduces this dimension's score by 1.0 (floor 0). The phrases were
confirmed by 3+ cross-source US tech-resume guides as weak / vague /
templated.

| Score | Band |
| --- | --- |
| 5.0 | Zero banned-phrase hits. |
| 4.0 | Zero hits, but one or two soft-overuse verbs (leveraged / spearheaded) flagged for awareness. |
| 3.0 | One banned-phrase hit. |
| 2.0 | Two banned-phrase hits. |
| 1.0 | Three+ banned-phrase hits. |
| 0.0 | Templated buzzword language throughout. |

### 5. Persona Fit

The resume voice and emphasis match the target persona flag.

**`us-tech-senior`** — senior IC / staff / principal. Emphasizes
ownership ("Owned X service"), scope (team count, traffic, revenue
under management, on-call responsibility), influence (multi-team /
org-wide impact), technical judgment. Per the staff/principal
literature: Staff = 2–4 teams influence; Principal = 10–30+ teams.
Two pages acceptable. Verbs lean: Owned, Architected, Migrated, Drove,
Influenced.

**`us-tech-mid`** — mid-level IC, 3–7y. Emphasizes shipping cadence,
owner-of-feature stories, growth in scope across roles. One page.
Verbs lean: Built, Shipped, Reduced, Implemented, Led (limited scope).

**`pm-product`** — Product Manager track. Emphasizes user-outcome
metrics (activation, retention, revenue, NPS), stakeholder management,
roadmap shipping. Per Lenny's Newsletter + Exponent + Leland: the
reviewer weights user-outcome metrics over engineering metrics for
this persona. Verbs lean: Drove, Defined, Launched, Increased,
Reduced (user-side).

| Score | Band |
| --- | --- |
| 5.0 | Voice and entity selection cleanly match the persona; reviewer can't tell it isn't hand-written for that persona. |
| 4.0 | Persona match strong; one or two bullets drift into adjacent persona. |
| 3.0 | Persona match recognizable but generic; could pass for two personas. |
| 2.0 | Wrong emphasis for persona (e.g., engineering metrics on PM resume; intern-level metrics on staff resume). |
| 1.0 | Persona ignored; resume reads as one-size-fits-all. |
| 0.0 | Fundamentally mismatched (PM resume produces SQL bullets; senior resume produces homework-project bullets). |

## Pass criterion

`revisions_required` is **false** only when ALL of:

- Every dimension ≥ 4.0.
- `banned_phrase_hits` is empty.
- `missing_slugs` is empty (every quoted ontology slug resolves).

Otherwise the writer turn gets one revision cycle (max).

## Persona-specific weighting notes

For `pm-product`, treat the metric in dimension 1 as user-outcome
metric primarily. A resume with strong shipping-cadence metrics but no
user-outcome metrics scores ≤3.0 on dimension 1 even if numerical
density is high. The user-outcome bias is per Lenny's Newsletter
guidance and confirmed by Exponent + Leland PM resume guides.

For `us-tech-senior`, dimension 5 (persona fit) takes co-equal weight
with dimension 1; a resume with strong metrics but no ownership or
scope signal cannot score 5/5 on persona fit. Multi-team scope (Staff
= 2–4 teams; Principal = 10–30+ teams) per the staff/principal
literature should be visible.

## ATS sanity check (non-LLM portion)

CI runs the deterministic portion of this rubric:

- `banned_phrases.json` regex sweep — gates dimension 4.
- Bullet count per role (3–6 / 2–3 by recency).
- Length: page count via word count proxy (≈400–500 words per page).
- Reverse-chronological order check.
- No table / column / graphic markers in source.

The LLM-scored portion (dimensions 1, 2, 3, 5) runs in the reviewer
turn and is non-blocking in CI but tracked for drift across model
versions.

## Fixture authoring guide

Place pass and fail golden fixtures under
`tests/fixtures/resume-en/{pass,fail}/`:

```
tests/fixtures/resume-en/
  pass/
    01-us-tech-senior-infra.md      (senior IC, infra ownership)
    02-us-tech-mid-startup.md       (mid IC, startup, shipping cadence)
    03-pm-product-saas.md           (PM, B2B SaaS, retention metrics)
    04-us-tech-senior-em.md         (EM track, multi-team)
    05-pm-product-consumer.md       (PM, consumer, activation focus)
  fail/
    01-passive-voice-throughout.md  (banned-phrase cluster + passive)
    02-no-metrics.md                (responsibility-list bullets)
    03-buzzword-overload.md         (synergy / team-player / proven)
    04-wrong-persona-fit.md         (PM resume with infra metrics)
    05-keyword-stuffed-ats.md       (ATS keyword stuffing footer)
```

Each fixture is plain markdown with frontmatter:

```
---
expected_dimensions:
  metric_density: 4
  action_verb_quality: 4
  structural_adherence: 4
  banned_phrase_cleanliness: 4
  persona_fit: 4
expected_revisions_required: false
persona: us-tech-senior        # or us-tech-mid, pm-product
target_company: <company>      # optional
notes: |
  Why this is a known good/bad sample. One paragraph.
  Cite the failure mode it isolates if any.
---
{the resume markdown}
```

## Refinement protocol

When the reviewer turn lands non-cleanly on a fixture (good fixture
scores < 4 on some dimension, or bad fixture scores ≥ 4 across the
board), refine THIS file's band definitions until separation is clean.
Do not retroactively change fixture labels — fixtures are the ground
truth, the rubric chases them.

## Calibration status (v1.0)

This rubric ships with **research-based calibration** — dimension
definitions and bands were derived from cross-source consensus across
20+ US tech-resume guides (see `research-notes.md`). A named human
domain reviewer (e.g., a senior tech recruiter or hiring manager) is
recommended for v1.1 calibration; their walkthrough of the golden
fixtures may shift band thresholds. Until then, the LLM reviewer turn
is self-consistent against this rubric, and the fixture set provides
ground truth.
