# prompt-writer.md — render-resume-en writer turn

This is the writer-turn instruction for `render-resume-en`. The
reviewer turn lives in `prompt-reviewer.md` and runs in a SEPARATE
Claude turn with `RUBRIC.md` re-loaded fresh. Do not collapse the two
turns — same-context self-evaluation inflates scores by ~1 point.

## Inputs

- **persona** (required): `us-tech-senior`, `us-tech-mid`, or
  `pm-product`. Each has a tuned voice and emphasis (see RUBRIC.md
  dimension 5).
- **target_company** (optional): target company name. Used for
  keyword alignment with public job descriptions.
- **target_jd_text** (optional): pasted job description. Used for
  bullet-level keyword mirror; does NOT cause keyword-stuffing — the
  alignment is at the bullet level, not as a hidden footer.
- **page_limit** (optional): `1` or `2`. Default: 1 page for
  `us-tech-mid` and `pm-product` mid-level; 2 pages for
  `us-tech-senior` and `pm-product` senior-level.

## Vault query

Before drafting, query the user's vault for nodes that match the
persona slice:

- **us-tech-senior** → role + achievement + project nodes; surface
  ownership and scope signals (team size, traffic, revenue under
  management, on-call responsibility, multi-team influence).
- **us-tech-mid** → role + project + achievement; surface shipping
  cadence and feature-ownership stories. Recent 5–7 years prioritized.
- **pm-product** → project + decision + achievement; surface
  user-outcome metrics (activation, retention, revenue, NPS).

If the vault has no relevant nodes for the persona, ask the user one
question to fill the gap before drafting. Do not invent ontology data.

## Drafting rules

- **Reverse chronological.** Most recent role first. Dates
  right-aligned. Past tense for past roles, present tense for current.
- **Metric-first XYZ bullets.** Each bullet leads with a quantifiable
  result, then specifies the action that produced it. Canonical
  shape: "Reduced p95 latency 40% by replacing X with Y across N
  services."
- **Action verb start.** Built, Led, Shipped, Reduced, Architected,
  Drove, Owned, Migrated, Hardened, Instrumented, Benchmarked,
  Refactored, Influenced, Defined, Launched, Increased.
- **Verb diversity.** Across any 5 consecutive bullets, use ≥3
  distinct lead verbs. Repeating "Led" or "Built" is the most common
  failure mode.
- **One to two lines per bullet, 20–25 words max.** If a bullet
  exceeds, split or compress.
- **3–6 bullets per recent role.** 2–3 per older roles.
- **One experience per bullet (load-bearing).** A single bullet must
  describe one experience. If two distinct experiences want to share
  a slot, write each as its own bullet, in chronological order.
  Prose paragraphs in the Summary section follow the same rule:
  one experience per paragraph, with an explicit transition sentence
  between paragraphs that name the thread connecting them. Mixing
  experiences in one bullet or paragraph creates reader cognitive
  load and is a quality bug.
- **Quote ontology slugs while drafting.** Reference concrete entities
  by slug in square brackets, e.g. `[[role/staff-eng-stripe-2023]]`
  or `[[project/checkout-migration-2024]]`. The reviewer turn uses
  these to verify metric claims against the vault. **The user-facing
  artifact must NOT contain raw slug notation.** After your draft is
  complete, replace every `[[type/slug]]` with the entity's
  natural-language label. The skill orchestrator runs
  `lockedin.render.resolve_slugs.resolve_file()` after this turn.
- **No banned phrases.** Before returning the draft, scan against
  `banned_phrases.json`. If any match, replace with a stronger active
  alternative (Built / Led / Drove / Shipped + metric).
- **ATS-clean format.** Plain markdown. No tables, no columns, no
  graphics. Standard sections (Header / Summary / Experience /
  Skills / Education).
- **Mirror JD keywords (if `target_jd_text` provided).** Align verbs
  and nouns at the bullet level — do NOT keyword-stuff a hidden
  footer. Modern ATS (2025+) uses semantic intelligence and rewards
  context-embedded keywords over isolated skill lists. Aim for the
  most relevant 3–5 JD terms surfaced naturally in the bullets.
- **Persona-specific emphasis** — see RUBRIC.md dimension 5. PM
  bullets lead with user-outcome metrics; senior IC bullets lead with
  ownership and scope; mid IC bullets lead with shipping outcomes.
- **2025-2026 GenAI era awareness.** Resume credibility has eroded as
  AI-assisted resumes converged toward uniform wording. Lean into
  authentic, hard-to-fake details: specific named systems, specific
  date ranges, specific team sizes. Avoid generic phrasing that AI
  graders flag as low-signal.

## Output

Two output forms: draft (handed to reviewer with slug tokens
intact) and final (saved to `<vault>/outputs/`, slug tokens
resolved). The skill orchestrator runs the resolver between the
two. Do not emit raw slug notation in the final artifact.

A single English resume in plain markdown. Sections:

```
# {Name}
{location} · {email} · {linkedin url} · {github url}

## Summary
{one paragraph, ≤3 lines, persona-specific value prop. Senior:
ownership/scope. Mid: shipping outcomes. PM: user outcomes.}

## Experience

### {Role title} — {Company}     {Start} – {End}
{Optional one-line scope: "Owned <service>; team of N; traffic Q."}
- {XYZ bullet 1}
- {XYZ bullet 2}
- ...

### ...

## Skills
{skills section. For ML/Security/Designer/EM personas, group by
category (Languages / Frameworks / Cloud / etc.). For generic
us-tech-mid, flat list.}

## Education
{degree(s), reverse chronological, only most recent if space tight}
```

## What you do NOT do here

- Score yourself. That's the reviewer turn's job.
- Suggest revisions. The reviewer's JSON drives the revision cycle.
- Add headers, footers, or surrounding chat ("Here is your
  resume..."). Output the resume markdown alone.
- Inflate scope. If the vault entity says "team of 3", do not write
  "team of 30".
- Generate fictitious metrics. If a project has no `result_metric`
  field in the ontology, ask the user before assigning one. The
  user's truth is the boundary.
