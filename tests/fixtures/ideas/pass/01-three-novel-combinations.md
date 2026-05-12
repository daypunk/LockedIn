---
expected_score: 4.5
expected_dimensions:
  feasibility: 5
  novelty: 5
  evidence_ground: 5
  scope_match: 5
  motivation_alignment: 4
expected_revisions_required: false
constraint: "evenings and weekends, 8 weeks, no funding"
notes: |
  Synthetic composite — three ideas each in a distinct skill × domain
  quadrant, each grounded in named vault entities (slugs preserved),
  each with a concrete next step. Placeholder identifiers only
  (SOME_COMPANY, SAMPLE_USER, GLOBAL_TECH, ACME). No real persons or
  companies. Pass fixture: all five dimensions ≥ 4. All ideas respect
  the 8-week evenings constraint and cite at least two vault entities.
  No banned phrases present.
---
1. Build a CLI linter for internal SQL queries that flags patterns your team's retrospectives have flagged as costly. Your work on [[project/data-pipeline-2024]] gave you a precise map of which query shapes caused the most production incidents at ACME; that pattern corpus is the training set. The linter runs as a pre-commit hook, adding zero pipeline overhead. Estimated scope: two weekends to build the rule engine, four evenings to write the first 15 rules from the incident log. Next step: export the incident-tagged query log from [[project/data-pipeline-2024]] and count recurring anti-patterns to confirm the rule count is realistic.

2. Write a short guide series on [[skill/distributed-tracing]] targeted at engineers at companies the size of SOME_COMPANY (50–200 engineers) who are adding tracing for the first time. Your work at [[role/senior-swe-infra-2023]] is the primary source material — you solved the cold-start problem on two separate occasions, which most guides skip entirely. The guide series is six posts, each under 1,000 words, publishable on a personal site with no editorial gate. Estimated scope: three evenings per post. Next step: draft the outline for post one ("Why your first trace is never representative") using notes from [[project/infra-observability-2023]].

3. Prototype a weekend scheduler tool that combines your [[skill/calendar-api-integration]] work with the constraint-satisfaction logic you wrote for [[project/team-scheduling-2024]] at GLOBAL_TECH. The tool would let a team of 8–12 people declare availability windows and hard constraints, then propose a meeting grid for the week — a problem your team solved manually each Monday. Estimated scope: one weekend to wire the API, one weekend to build the constraint solver, two evenings to add a simple export. Next step: confirm the Google Calendar API still supports the batch-read scope you used in [[project/team-scheduling-2024]].
