---
expected_score: 4.5
expected_dimensions:
  feasibility: 5
  novelty: 4
  evidence_ground: 5
  scope_match: 4
  motivation_alignment: 5
expected_revisions_required: false
constraint: "single weekend, solo, no external APIs with rate limits"
notes: |
  Synthetic composite — three ideas scoped to a single weekend solo
  build with no external API rate-limit dependencies. Placeholder
  identifiers only. No real persons or companies. Pass fixture:
  feasibility is 5 (every idea is scoped to ≤2 days). Novelty is 4
  not 5 because idea 2 is adjacent to existing work (it extends a
  tool the vault already has). All ideas cite vault entities and
  include concrete this-weekend next steps.
---
1. Build a local Markdown graph viewer for your [[project/note-graph-2023]] vault that reads the link structure already in your notes and renders it as an interactive force-directed graph in the browser, served from localhost. You have all the data (the Markdown files), you know the link syntax, and you built a similar graph for [[project/data-viz-2024]] — the only new surface is the browser rendering layer. No external API calls, no auth, no rate limits. Next step: spend Friday evening mapping the link-extraction logic and Saturday building the graph renderer using a local SVG library.

2. Extend [[project/log-formatter-2024]] to support NDJSON (newline-delimited JSON) in addition to the single-object JSON it handles today. The NDJSON format is the output of every structured logger your team uses at SOME_COMPANY; adding NDJSON support makes the tool immediately useful for your most common debugging workflow. This is adjacent to existing work, not a novel combination — but the weekend scope makes it the right unit of work. Next step: add a `--format ndjson` flag to the existing CLI and write three test cases from real log samples in [[project/log-formatter-2024]].

3. Write a deterministic test data generator for [[skill/database-testing]] scenarios that takes a JSON schema and emits fixture rows with controlled distribution properties (no duplicates, no nulls in specified columns, skew toward edge-case boundary values). You built ad-hoc versions of this in three separate projects; a standalone generator would have been reusable across all three. The scope is one data type per column per afternoon session. Next step: enumerate the five column types you need most frequently from [[project/db-migration-2023]] and write the spec for each generator.
