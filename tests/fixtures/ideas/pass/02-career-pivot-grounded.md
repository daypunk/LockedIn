---
expected_score: 4.5
expected_dimensions:
  feasibility: 4
  novelty: 5
  evidence_ground: 5
  scope_match: 4
  motivation_alignment: 5
expected_revisions_required: false
constraint: "career pivot toward developer tooling, 12 weeks part-time"
notes: |
  Synthetic composite — three ideas for a career pivot from backend
  engineering toward developer tooling, each grounded in specific vault
  entities. Placeholder identifiers only. No real persons or companies.
  Pass fixture: motivation_alignment is 5 (every idea draws directly on
  stated developer-tooling interest). Feasibility is 4 because idea 3
  is a stretch for 12 weeks part-time (would likely need a 16-week
  horizon). All ideas cite at least two vault entities.
---
1. Port the static-analysis rules you wrote for [[project/security-lint-2023]] at ACME from Python to a language-server plugin that works inside VS Code. The rules caught 14 high-severity security patterns in your codebase; making them available as live in-editor diagnostics would surface the same patterns for any engineer writing Python, not just those who remember to run the CLI. The domain shift is small (you know the rules and you know Python); the novelty is the language-server protocol surface you have not used before. Estimated scope: 4 weekends to learn LSP basics and port the top 5 rules. Next step: read the VS Code language-server extension API docs and estimate how many of your 14 rules have direct diagnostic analogs.

2. Build a debug-log formatter that takes structured JSON logs from [[skill/structured-logging]] and renders them as a readable diff-style timeline in the terminal. Your work on [[project/infra-observability-2023]] involved reading thousands of raw JSON log lines manually — the formatter would have saved 2–3 hours per incident. The tool has a clear user (you and every engineer who does structured-log debugging) and a clear scope (terminal output only, no server, no auth). Estimated scope: 3 evenings for the parser, 2 evenings for the diff renderer, 1 weekend for the CLI wrapper. Next step: write the input specification from the most common log shapes in [[project/infra-observability-2023]].

3. Contribute a plugin to an open-source developer tooling project in the CI/CD space that adds the anomaly-detection heuristics you developed in [[project/ci-anomaly-2024]] at GLOBAL_TECH. The heuristics flag flaky tests with 89% precision in your test suite; packaging them as a plugin rather than a standalone tool gives you distribution and feedback from a live user base. This is the stretchiest of the three because it requires understanding the host project's plugin API before scoping. Next step: identify two OSS CI projects with active plugin ecosystems and read their contribution guides this week.
