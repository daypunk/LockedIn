# pm-product

## Snapshot

Product Manager with 4-10 years of experience owning a product area or
feature domain at a tech company. Ships roadmap items from discovery through
launch, defines success metrics, and drives cross-functional alignment across
engineering, design, data, and marketing. Distinct from a TPM (who manages
delivery schedules and dependencies) or a growth PM (who focuses narrowly on
funnel metrics) in that this persona covers the full PM spectrum: strategy,
discovery, scoping, launch, and post-launch iteration. User-outcome metrics
are the primary evidence of impact. Targets Product Manager, Senior PM, or
Group PM roles at B2B SaaS, consumer apps, or platform companies.

## Skill cluster

Hard skills (8-12 items):
- Product analytics: Amplitude, Mixpanel, or Looker for funnel analysis,
  cohort retention, and activation metric tracking
- SQL at self-serve analytical depth (cohort queries, funnel queries, A/B
  test result interpretation)
- A/B experiment design: hypothesis framing, MDE calculation, significance
  thresholds, holdout groups
- Roadmap tools: Linear, Jira, Productboard, or equivalent; prioritization
  frameworks (RICE, ICE, opportunity scoring)
- User research facilitation: moderated usability interviews, Jobs-to-be-Done
  framing, user survey design
- PRD / spec authorship at a level that engineers and designers can build from
  without repeated clarification
- Launch coordination: GTM planning, in-app messaging, release notes,
  changelog management
- OKR/metric definition: setting leading and lagging indicators, writing
  measurable KRs that the team can influence
- Stakeholder management: executive reporting, cross-team dependency
  alignment, escalation judgment

Soft / cross-functional skills (4-6 items):
- Engineering partnership: translating user problems into scoped technical
  requirements, respecting feasibility constraints
- Design collaboration: grounding design decisions in user research evidence
  and measurable success criteria
- Data team partnership: defining event taxonomies, working with analysts on
  experiment design, interpreting cohort data
- Executive storytelling: connecting product metrics to business outcomes in
  a format leadership can act on

## Responsibility patterns

- Defines and owns the success metrics for a product area or feature set,
  aligning the engineering squad and design partner on what a successful
  launch looks like before work begins.
- Conducts discovery research (user interviews, competitive analysis, support
  ticket triage) and synthesizes findings into a product brief that scopes
  the problem, not just the solution.
- Ships the roadmap on a quarterly cadence: manages scope, negotiates
  dependencies, and communicates launch risks to leadership before they
  become misses.
- Runs post-launch metric reviews and drives the iteration cycle based on
  activation, retention, or revenue signal — not gut feel.
- Aligns cross-functional stakeholders (engineering, design, marketing, sales)
  through shared product artifacts: PRDs, one-pagers, roadmap reviews.
- Defines and monitors leading indicators that predict downstream business
  metrics, escalating early when a metric diverges from target.
- Represents the user perspective in technical trade-off discussions,
  ensuring that scope cuts do not silently degrade the core user outcome.

## Tone guidance

Vocabulary register: outcome-led, user-focused, narrative-friendly. Bullets
must foreground user-outcome metrics (activation, retention, NPS, revenue,
error rate reduction) over engineering metrics. A PM resume that reads like
an engineering resume has the wrong emphasis for this persona. Stakeholder
alignment and discovery work are visible, not just launch outcomes.

Lean on: Drove, Defined, Launched, Increased, Reduced, Owned, Shipped,
Partnered, Designed, Led, Grew, Established.

Avoid: "managed the backlog" without an outcome, "wrote PRDs" as a
standalone claim (describe the decision or feature and its metric impact),
"cross-functional collaboration" without specifying what the collaboration
produced, engineering metrics as the primary headline on a PM resume.

## Action verb cluster

Drove, Defined, Launched, Increased, Reduced, Owned, Shipped, Partnered,
Designed, Led, Grew, Established, Coordinated, Synthesized, Aligned,
Validated, Introduced, Measured

## Banned phrases (persona-specific additions to global banned_phrases.json)

- "managed stakeholders" — vague; describe the alignment outcome or the
  decision the stakeholders reached
- "wrote PRDs" — table stakes; describe the feature shipped and the metric
  it moved
- "wore many hats" — startup-culture cliche; name the specific functions
  you covered and the outcome
- "customer obsessed" — self-evaluative; demonstrate it with a user research
  method and what it changed
- "moved fast" — describe the ship cadence with specifics (features per
  quarter, experiment velocity)

## Persona fit scoring guidance

- `pm-product` persona_fit >= 4 requires at least 2 user-outcome metrics
  (activation rate, retention rate, NPS, revenue lift, error rate for users)
  — engineering metrics alone are not sufficient for this persona.
- A resume that reads primarily as engineering ownership without user-outcome
  framing cannot score above 3.0 on persona_fit.
- Discovery work evidence (user interviews, research synthesis, A/B test
  design) is a strong signal for senior PM persona_fit.
- Roadmap and cross-functional alignment artifacts (PRD quality, GTM
  coordination) are expected signals; their complete absence caps
  persona_fit at 3.5.

## Quality bar examples

Before: "Launched new features for the mobile app."
After: "Defined and launched a bill-pay reminder feature with 3 engineering
squads; late-payment rate among enrolled users dropped by ~34% within the
first quarter of launch."

Before: "Improved the onboarding experience."
After: "Drove the onboarding flow redesign from 11 steps to 5 after
synthesizing findings from 14 user sessions; seller activation rate within
7 days of sign-up rose from 29% to 47%."

Before: "Worked with data team on analytics."
After: "Partnered with the data team to standardize the metric event
taxonomy, reducing experiment cycle time from 6 weeks to 3 weeks and
enabling the squad to double its A/B test throughput per half."
