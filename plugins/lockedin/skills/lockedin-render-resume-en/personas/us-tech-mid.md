# us-tech-mid

## Snapshot

Mid-level software engineer (IC2 / SWE II / Software Engineer II) at a US
tech company, startup, or scaleup with 3-7 years of experience. Owns
features end-to-end within a team: takes a spec from planning to production,
including testing, deployment, and monitoring. Scope is typically a single
service or a feature area within a larger system. Distinct from junior in
that shipping cadence and feature ownership are visible; distinct from senior
in that cross-team influence is not yet the primary expectation. Resume should
demonstrate growth across roles and increasing scope. One-page format.
Targets Software Engineer II / III roles, or equivalent, at Big Tech,
scaleups, or Series A-C startups.

## Skill cluster

Hard skills (8-12 items):
- Primary language at production depth (TypeScript, Python, Go, Java, or
  equivalent)
- Full-stack awareness: frontend framework (React, Vue) or backend API
  design, depending on focus
- Database basics: SQL at query-authoring depth; one NoSQL system at
  operational familiarity
- REST API design and contract versioning
- Testing: unit, integration, and at least one E2E test framework
- Docker at development and deployment usage depth
- Cloud fundamentals: AWS, GCP, or Azure services at feature-usage level
  (not infra ownership)
- CI/CD: pipeline authorship, test gating, deployment automation
- Code review practices: writing constructive review comments, reviewing
  for correctness and maintainability
- Observability basics: reading dashboards, adding log statements, creating
  a basic alert

Soft / cross-functional skills (4-6 items):
- Feature ownership: taking a ticket from design spec through production
  without hand-holding
- Cross-squad communication: participating in planning, raising blockers
  early, updating stakeholders
- Debugging methodology: systematic isolation of production issues
- Growth trajectory: demonstrable increase in scope, complexity, or
  responsibility across roles

## Responsibility patterns

- Builds and ships features end-to-end within a product squad, owning
  implementation from design review through production deploy and monitoring.
- Improves code quality and system reliability within a service boundary:
  refactoring hot paths, adding tests, reducing error rates.
- Contributes to the team's sprint cadence by estimating accurately, raising
  blockers promptly, and completing defined scope without scope creep.
- Participates in on-call rotation, learning the production surface and
  documenting runbook improvements based on incident learnings.
- Migrates or updates components within a service, following established
  patterns, with minimal rework requested in code review.
- Writes or improves documentation for the features they build, reducing
  future onboarding friction.
- Grows scope across roles: measurable increase in ownership, complexity,
  or team influence between the first and most recent roles on the resume.

## Tone guidance

Vocabulary register: shipping-cadence-forward, outcome-focused, honest about
scope. Bullets should foreground what you built and what measurably improved
as a result. Do not over-inflate scope to senior level — authenticity reads
better to mid-level hiring managers than inflated language.

Lean on: Built, Shipped, Reduced, Implemented, Migrated, Improved, Launched,
Automated, Refactored, Added.

Avoid: "owned the entire platform" (scope inflation), "architected"
(unless a junior-to-mid scope architecture decision is genuine), weak verbs
("worked on", "helped with"), buzzwords that imply seniority you don't yet
have.

## Action verb cluster

Built, Shipped, Reduced, Implemented, Migrated, Improved, Launched,
Automated, Refactored, Added, Contributed, Delivered, Deployed, Designed,
Tested, Optimized, Replaced, Maintained

## Banned phrases (persona-specific additions to global banned_phrases.json)

- "full ownership" without scope qualification — mid-level engineers own
  features, not platforms; qualify the scope
- "led the team" without a formal lead role — use "drove" or "proposed"
  if informal influence is what you mean
- "architected" without a clear design decision — reserve for cases where
  a genuine architectural choice (trade-off documented) was made

## Persona fit scoring guidance

- `us-tech-mid` persona_fit >= 4 requires a visible shipping cadence (feature
  count, sprint cadence, or release frequency) AND at least 1 metric per
  role showing a quantified improvement.
- Scope inflation (staff-level language for feature-level work) caps
  persona_fit at 3.0.
- Clear scope growth between roles (from BLUE_LABS feature work to
  SOME_COMPANY multi-squad impact) is the strongest persona_fit elevator.
- One-page length compliance is a gate for structural_adherence, not
  persona_fit, but matters for overall pass.

## Quality bar examples

Before: "Worked on frontend features for the product."
After: "Built the onboarding A/B testing framework from scratch, enabling
3 simultaneous experiments per sprint; onboarding completion rate rose from
54% to 71% within two months of adoption."

Before: "Helped improve API performance."
After: "Reduced API error rate from 1.4% to 0.2% by migrating the Express.js
authentication middleware to a dedicated auth service with retry logic and
circuit-breaking."

Before: "Maintained the CI/CD pipeline."
After: "Automated the staging deploy pipeline with GitHub Actions, cutting
deploy-to-staging cycle time from 40 minutes to 8 minutes and eliminating
the manual approval step for non-production environments."
