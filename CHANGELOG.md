# Changelog

## [1.0.0] — 2026-05-01

Initial release. Distribution via the Claude Code plugin marketplace
as `daypunk/selfgraph`. Renderers ship with research-based
calibration. Named human reviewer engagement and fixture buildout are
explicit v1.1 targets, listed in Future work below.

### Plugin distribution

- Marketplace catalog at `.claude-plugin/marketplace.json`.
- Plugin manifest at `plugins/selfgraph/.claude-plugin/plugin.json`.
- Skills under `plugins/selfgraph/skills/{selfgraph,
  selfgraph-render-jaso, selfgraph-render-resume-en}/`.
- One-time setup wizard at `plugins/selfgraph/commands/setup.md`
  (`/selfgraph:setup`). It wires the HUD, picks a default Q&A
  language, and picks a vault path.

### Ontology v0.2

- 15 entity types: person, company, role, project, achievement,
  skill, education, certificate, publication, volunteer, language,
  document, meeting, decision, topic.
- 15 edge predicates with domain, range, and inverse: works_on,
  held_role_at, has_role, produced, uses_skill, studied_at, earned,
  attended, made, covers, mentions, derived_from, volunteered_at,
  speaks, authored.
- Per-entity-type field contracts (required and optional, 9 field
  types).
- Edge domain and range constraints. `selfgraph validate` rejects
  type-mismatched edges.
- External vocabulary aliases (`schema:Person`, `foaf:Organization`,
  `jsonresume:work`, …) per `docs/ontology-mapping.md`.
- Schema versioning. `SCHEMA_VERSION = 2`.

### Renderers

- **render-graph**: interactive single-file `graph.html` using
  vendored force-graph 1.51.4 (~178 KB, MIT). See
  `docs/adr/0001-viz-library.md`.
- **render-jaso**: Korean cover letter renderer with calibrated
  rubric.
  - `RUBRIC.md`: five dimensions (두괄식, 구조화, 구체성, 표현,
    적합성) with 0 to 5 score bands and pass criterion.
  - `prompt-writer.md` and `prompt-reviewer.md`: two-turn writer and
    reviewer split.
  - `banned_phrases.json`: 28 cross-source confirmed entries.
    HR-survey-anchored frequency data (성실 49.2%, 노력 36.3%,
    책임감 28.5%, 솔선수범 21.8%, 창의적 21.8%, 도전적 13.4%).
  - `research-notes.md`: citations across 워크넷, 잡코리아, 사람인,
    링커리어, 캐치, 하이잡, arXiv, Google Scholar.
  - `reviewers.md`: research-based calibration documented. Named
    human reviewer awaited via
    `.github/ISSUE_TEMPLATE/korean_reviewer_onboarding.yml`.
  - 5 pass and 5 fail golden fixtures across IT 대기업, 외국계, 금융,
    제조, 스타트업 industries plus the five canonical failure modes
    (templated phrasing, passive voice, generic content, missing
    structure, missing metrics).
- **render-resume-en**: English resume renderer with calibrated
  rubric.
  - `RUBRIC.md`: five dimensions (metric_density,
    action_verb_quality, structural_adherence,
    banned_phrase_cleanliness, persona_fit) with 0 to 5 score bands.
  - `prompt-writer.md` and `prompt-reviewer.md`: two-turn split.
  - `banned_phrases.json`: 44 cross-source confirmed phrases plus 5
    soft-overuse entries. Sources include The Pragmatic Engineer,
    Lenny's Newsletter, MIT CAPD, Harvard FAS Mignone Center, Yale
    OCS, Workology, Tealhq, ResumeWorded, IGotAnOffer, Toptal, plus
    academic resume linguistics literature.
  - 3 personas: us-tech-senior, us-tech-mid, pm-product. Each carries
    its own emphasis. Senior surfaces ownership, scope, and
    influence. Mid surfaces shipping cadence. PM surfaces
    user-outcome metrics (activation, retention, revenue, NPS).

### CLI utilities (deterministic, no LLM)

- `selfgraph install`: `--auto-register`, `--check`, `--upgrade`
  (hash-aware refusal of user-modified files), `--uninstall`,
  `--setup-hud`, `--remove-hud`.
- `selfgraph init --non-interactive --fixture <yaml>`: deterministic
  vault seed from a YAML fixture. PyYAML date and datetime values are
  auto-coerced to ISO strings.
- `selfgraph ingest <path> --dry-run`: parses `.pdf`, `.docx`, `.md`,
  `.txt` and emits a diff report. No vault writes.
- `selfgraph validate`: three-layer check (frontmatter shape, field
  contracts, edge constraints).
- `selfgraph render graph`: graph.json plus interactive graph.html.
- `selfgraph template list / add / remove`.
- `selfgraph doctor`: runtime, skill install, and API key state
  check.
- `selfgraph hud`: one-line statusLine snippet.

### HUD (statusLine)

- Three-segment output: `selfgraph X.Y.Z │ 5h:NN% · wk:NN% │ vault:
  Nn · Me`.
- Claude Code usage counted from `~/.claude/projects/*/*.jsonl` user
  turns within the rolling 5-hour and 7-day windows. Default
  thresholds tuned for the Pro tier. Override with
  `SELFGRAPH_HUD_5H_LIMIT` and `SELFGRAPH_HUD_WK_LIMIT`.
- Color graded green, yellow, red as percentage rises. On by default.
  Disable via `NO_COLOR` or `SELFGRAPH_HUD_COLOR=0`.
- Wired automatically by `/selfgraph:setup` (or `selfgraph install
  --setup-hud`). Reversible via `selfgraph install --remove-hud`.

### OSS infrastructure

- `CONTRIBUTING.md`: dev setup, accepted contribution paths, Korean
  fixture authoring rules, domain reviewer onboarding, language
  policy, CI gates, commit style.
- `CODE_OF_CONDUCT.md`: adopts Contributor Covenant v2.1 by
  reference. Maintainer contact at
  [daehee216@naver.com](mailto:daehee216@naver.com).
- `.github/ISSUE_TEMPLATE/`: structured YAML forms for `bug_report`,
  `feature_request`, `korean_reviewer_onboarding`, plus `config.yml`
  linking to Discussions and disabling blank issues.

### Documentation

- `README.md` and `README.ko.md`: install, use, why, how it works,
  skills, license. Language switcher at top of both.
- `CLAUDE.md`: fresh-session bootstrap (project state, working
  agreements, repo layout, what to never do, verification quick
  reference, resume protocol).
- `docs/architecture.md`: execution model and skill plus CLI split.
- `docs/ontology-spec.md`: frontmatter contract.
- `docs/ontology-mapping.md`: cross-walk to JSON Resume, Schema.org,
  FOAF.
- `docs/orchestration.md`: pipeline plan for render, bulk ingest, and
  graph curator.
- `docs/hud.md`: statusLine integration.
- `docs/cli.md`: optional CLI surface.
- `docs/adr/0001-viz-library.md`: ACCEPTED, vendored force-graph.

### Tests

52+ tests across import, ontology, storage round-trip, command
lifecycle (install, doctor, validate v0.2 contracts, render graph,
init from fixture, template, ingest dry-run, hud), plus the non-LLM
portion of jaso fixture validation against the 5 pass and 5 fail
golden set.

## Removed in this release

- **render-portfolio**: removed from scope. Portfolio sites belong to
  dedicated design and web-publishing tooling (Figma, dedicated
  static-site generators, hand-curated PDF) where the quality bar
  exceeds what a markdown-vault render can deliver. selfgraph stays
  focused on text artifacts (resume, 자소서) and the graph
  visualization.

## Future work

- **Q&A interview buildout**: v1.0 ships
  `plugins/selfgraph/skills/selfgraph/templates/career/questions.yaml`
  as a 3-section, 6-question skeleton. v1.1 target is 9 sections
  (identity, companies and roles, projects, education, skills,
  decisions, learning, certificates, publications) with 5 or more
  questions each, branching, follow-up probing on weak answers, and
  ontology completeness checks. Vault quality depends on interview
  depth, which makes this the highest-leverage v1.1 work.
- **render-jaso human reviewer**: `reviewers.md` placeholder is open
  for v1.1 calibration. Onboard via
  `.github/ISSUE_TEMPLATE/korean_reviewer_onboarding.yml`.
- **render-resume-en fixture set**: 5 pass and 5 fail per persona to
  match render-jaso coverage.
- **render-resume-en human reviewer**: senior US tech recruiter or
  hiring manager walks through the fixture set.
- **Quick-start path**: PDF-first onboarding and demo vault loading
  so a fresh user reaches a first artifact in under two minutes.
- **Automatic SELFGRAPH_REPORT.md**: single file at
  `~/.selfgraph/outputs/SELFGRAPH_REPORT.md` regenerated when the
  vault changes. Surfaces god nodes, coverage gaps, evidence recall
  trend, recent ingest summary.
- **Provenance tags**: `provenance` field on every vault entry
  (interview, pdf_ingest, docx_ingest, user_edit, inferred). Enables
  the user to trace where each fact came from.
- **Evidence recall instrumentation**: reviewer JSON gains an
  `evidence_recall` field (range 0.0 to 1.0). See `RUBRIC.md`
  "Evidence recall (informational)" in each renderer.
- **`selfgraph migrate`**: schema migration command for users on
  earlier vaults.
- **v1.2 orchestration**: explicit 5-step render pipeline plus
  parallel bulk-ingest dispatcher (designed in
  `docs/orchestration.md`).
- **v1.3 graph curator**: quarterly duplicate-merge agent.
