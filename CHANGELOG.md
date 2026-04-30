# Changelog

## [Unreleased] — 0.0.1

Initial pre-alpha. Targeted at the first GitHub push and the first
plugin-marketplace install path.

### Plugin distribution

- Marketplace catalog at `.claude-plugin/marketplace.json`.
- Plugin manifest at `plugins/selfgraph/.claude-plugin/plugin.json`.
- Skills under `plugins/selfgraph/skills/{selfgraph,
  selfgraph-render-jaso, selfgraph-render-resume-en,
  selfgraph-render-portfolio}/`.
- One-time setup wizard at `plugins/selfgraph/commands/setup.md`
  (`/selfgraph:setup`) — wires the HUD, picks a default Q&A language,
  picks a vault path.

### Ontology — v0.2

- 15 entity types (was 11 in v0.1) — added `certificate`,
  `publication`, `volunteer`, `language`.
- 15 edge predicates (was 12) — added `volunteered_at`, `speaks`,
  `authored`.
- Per-entity-type field contracts (required + optional + 9 field
  types) replace the old `fields: dict[str, Any]`.
- Edge domain/range constraints — `selfgraph validate` rejects
  type-mismatched edges.
- External vocabulary aliases (`schema:Person`, `foaf:Organization`,
  `jsonresume:work`, …) per `docs/ontology-mapping.md`.
- Schema versioning — `SCHEMA_VERSION = 2`.

### Renderers

- `render-graph` — interactive single-file `graph.html` using vendored
  force-graph 1.51.4 (~178 KB, MIT). See `docs/adr/0001-viz-library.md`.
- `render-jaso` — Korean cover-letter renderer scaffold:
  `research-notes.md` v0.1 (5 cited Korean job-market sources +
  structural conventions), `RUBRIC.md` (5-dim scoring contract with
  bands), `prompt-writer.md` + `prompt-reviewer.md` (two-turn split),
  `banned_phrases.json`. Cultural calibration (`reviewers.md`) is a
  named TBD before v1.
- `render-resume-en` — English resume renderer scaffold:
  `research-notes.md` v0.1 (US tech / PM resume conventions, 3
  personas: us-tech-senior / us-tech-mid / pm-product). Prompts and
  rubric to follow.
- `render-portfolio` — single-file static HTML scaffold.

### CLI utilities (deterministic, no LLM)

- `selfgraph install` — `--auto-register`, `--check`, `--upgrade`
  (hash-aware refusal of user-modified files), `--uninstall`,
  `--setup-hud`, `--remove-hud`.
- `selfgraph init --non-interactive --fixture <yaml>` — deterministic
  vault seed from a YAML fixture. PyYAML date / datetime auto-coerced
  to ISO strings.
- `selfgraph ingest <path> --dry-run` — parses `.pdf` / `.docx` /
  `.md` / `.txt` and emits a diff report (no vault writes).
- `selfgraph validate` — three-layer check (frontmatter shape, field
  contracts, edge constraints).
- `selfgraph render graph` — graph.json + interactive graph.html.
- `selfgraph template list / add / remove`.
- `selfgraph doctor` — runtime / skill-install / API-key state check.
- `selfgraph hud` — one-line statusLine snippet.

### HUD (statusLine)

- Three-segment output: `selfgraph X.Y.Z │ 5h:NN% · wk:NN% │ vault:
  Nn · Me`.
- Claude Code usage counted from `~/.claude/projects/*/*.jsonl` user
  turns within the rolling 5-hour and 7-day windows. Default
  thresholds tuned for Pro tier; override with `SELFGRAPH_HUD_5H_LIMIT`
  / `SELFGRAPH_HUD_WK_LIMIT`.
- Color graded green / yellow / red as % rises; on by default.
  Disable via `NO_COLOR` or `SELFGRAPH_HUD_COLOR=0`.
- Wired automatically by `/selfgraph:setup` (or `selfgraph install
  --setup-hud`); reversible via `selfgraph install --remove-hud`.

### Documentation

- `README.md` / `README.ko.md` — install, use, why, two-store model
  (image placeholder), features, advanced links, license.
- `docs/architecture.md` — execution model and skill / CLI split.
- `docs/ontology-spec.md` — frontmatter contract.
- `docs/ontology-mapping.md` — selfgraph ↔ JSON Resume / Schema.org /
  FOAF cross-walk.
- `docs/orchestration.md` — pipeline plan for render / bulk ingest /
  graph curator.
- `docs/hud.md` — statusLine integration.
- `docs/cli.md` — optional CLI surface.
- `docs/adr/0001-viz-library.md` — ACCEPTED: vendored force-graph.

### Tests

52 tests across import / ontology / storage round-trip / commands
(install lifecycle, doctor, validate v0.2 contracts, render graph,
init from fixture, template, ingest dry-run, hud).

## Known gaps before v1

- `tests/fixtures/jaso/{pass,fail}/` — golden fixtures (5 + 5) need
  domain reviewer authoring; the directory ships with TEMPLATE.md.
- `selfgraph/skill/render-jaso/reviewers.md` — named human reviewer
  TBD before v1 release.
- `selfgraph/skill/render-resume-en/{RUBRIC,prompt-writer,prompt-reviewer}.md`
  — to author after research-notes.md is locked.
- v0.3 orchestration: explicit 5-step render pipeline + parallel
  bulk-ingest dispatcher.
