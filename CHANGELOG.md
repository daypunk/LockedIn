# Changelog

## [1.1.0] — in progress

Rebrand to LockedIn plus targeted improvements based on first-user
testing of 1.0. Documentation, identifiers, and vault path all changed.
The render-graph artifact was retired. The HUD started showing real
Anthropic OAuth utilization instead of a heuristic. Renderer outputs
got slug resolution and a logical-flow guard.

### Rebrand

- Product name: selfgraph to LockedIn. The selfgraph identifier slot is
  reserved for a future v2 product targeting a wider experience domain.
- GitHub repo: daypunk/selfgraph renamed to daypunk/LockedIn (history
  and v1.0.0 tag follow).
- Naming convention: brand `LockedIn`, machine identifier `lockedin`,
  slash command `/lockedin:setup`.
- Vault default: `~/.selfgraph/` to `~/Documents/LockedIn/`. The
  dot-prefixed home directory was hidden from Finder and Explorer.
- Env vars: `SELFGRAPH_*` to `LOCKEDIN_*` (`LOCKEDIN_VAULT`,
  `LOCKEDIN_HUD_5H_LIMIT`, `LOCKEDIN_HUD_WK_LIMIT`,
  `LOCKEDIN_HUD_COLOR`, `LOCKEDIN_ALLOW_API_KEY`).
- Default template: `career` to `experience`. The umbrella covers
  meetings, decisions, learning, and side projects, not only career
  history. `lockedin migrate` auto-renames `<vault>/career/` to
  `<vault>/experience/` for users on the earlier layout.

### Removed

- **render-graph**: retired. First-user testing showed the auto-rendered
  force-graph HTML did not deliver clear value and risked anchoring the
  product's perceived quality on a weak surface. See ADR-0001 for the
  full disposition. Files removed:
  `lockedin/commands/render_graph.py`,
  `lockedin/render/graph_html.py`,
  `plugins/lockedin/scripts/vendor/force-graph.min.js` (~178 KB).

### Renderer quality

- `[[type/slug]]` references in renderer output are now resolved to
  natural-language labels before the artifact is shown to the user.
  See `prompt-writer.md` and the new resolver helper.
- Logical-flow guard added to both `prompt-writer.md` files. One
  experience per paragraph and explicit transition between
  experiences. Prevents reader cognitive load when more than one
  experience is implied per slot.

### HUD

- Anthropic OAuth `api.anthropic.com/api/oauth/usage` integration. HUD
  now shows real `five_hour.utilization` and `seven_day.utilization`
  instead of a heuristic counted from session JSONL. macOS reads
  credentials from Keychain. Linux reads
  `~/.claude/.credentials.json`. Windows reads
  `%USERPROFILE%\.claude\.credentials.json`.
- HUD label: `vault: Nn · Me` to `experience: Nn · Me` to match the
  renamed default template.
- Falls back to vault-only display when OAuth is unavailable.

### Documentation

- README.md and README.ko.md rewritten with LockedIn brand display.
- CLAUDE.md, CHANGELOG.md, docs/, CONTRIBUTING.md, plugin and
  marketplace manifests, ISSUE_TEMPLATE all updated.

## [1.0.0] — 2026-05-01

Initial release. Distribution via the Claude Code plugin marketplace
as `daypunk/selfgraph` (later renamed to `daypunk/LockedIn` in 1.1).
Renderers ship with research-based calibration. Named human reviewer
engagement and fixture buildout are explicit follow-up targets.

### Plugin distribution

- Marketplace catalog at `.claude-plugin/marketplace.json`.
- Plugin manifest at `plugins/<plugin>/.claude-plugin/plugin.json`.
- One-time setup wizard.

### Ontology v0.2

- 15 entity types: person, company, role, project, achievement,
  skill, education, certificate, publication, volunteer, language,
  document, meeting, decision, topic.
- 15 edge predicates with domain, range, and inverse.
- Per-entity-type field contracts (required and optional, 9 field
  types).
- Edge domain and range constraints. Validate command rejects
  type-mismatched edges.
- External vocabulary aliases (schema.org, FOAF, JSON Resume) per
  `docs/ontology-mapping.md`.
- Schema versioning. `SCHEMA_VERSION = 2`.

### Renderers

- **render-jaso**: Korean cover letter renderer with calibrated
  rubric.
  - Five dimensions (두괄식, 구조화, 구체성, 표현, 적합성) with 0 to
    5 score bands and pass criterion.
  - `prompt-writer.md` and `prompt-reviewer.md`: two-turn writer and
    reviewer split.
  - `banned_phrases.json`: 28 cross-source confirmed entries.
    HR-survey-anchored frequency data (성실 49.2%, 노력 36.3%,
    책임감 28.5%, 솔선수범 21.8%, 창의적 21.8%, 도전적 13.4%).
  - `research-notes.md`: citations across 워크넷, 잡코리아, 사람인,
    링커리어, 캐치, 하이잡, arXiv, Google Scholar.
  - 5 pass and 5 fail golden fixtures across IT 대기업, 외국계, 금융,
    제조, 스타트업 industries.
- **render-resume-en**: English resume renderer with calibrated
  rubric.
  - Five dimensions: metric_density, action_verb_quality,
    structural_adherence, banned_phrase_cleanliness, persona_fit.
  - Two-turn writer and reviewer split.
  - 44 cross-source confirmed banned phrases plus 5 soft-overuse
    entries. Sources include The Pragmatic Engineer, Lenny's
    Newsletter, MIT CAPD, Harvard FAS Mignone Center, Yale OCS,
    Workology, Tealhq, ResumeWorded, IGotAnOffer, Toptal.
  - 3 personas: us-tech-senior, us-tech-mid, pm-product.

### CLI utilities (deterministic, no LLM)

- `lockedin install`: `--auto-register`, `--check`, `--upgrade`
  (hash-aware refusal of user-modified files), `--uninstall`,
  `--setup-hud`, `--remove-hud`.
- `lockedin init --non-interactive --fixture <yaml>`: deterministic
  vault seed from a YAML fixture.
- `lockedin ingest <path> --dry-run`: parses `.pdf`, `.docx`, `.md`,
  `.txt` and emits a diff report.
- `lockedin validate`: three-layer check.
- `lockedin template list / add / remove`.
- `lockedin doctor`: runtime, skill install, and API key state check.
- `lockedin hud`: one-line statusLine snippet.

### HUD (statusLine)

- Heuristic three-segment output (replaced in 1.1 with OAuth).
- Color graded green, yellow, red as percentage rises.

### OSS infrastructure

- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` (Contributor Covenant v2.1),
  `.github/ISSUE_TEMPLATE/`.

### Tests

52 tests across import, ontology, storage round-trip, command
lifecycle, plus the non-LLM portion of jaso fixture validation
against the 5 pass and 5 fail golden set.

## Future work

- **Q&A interview buildout**: 1.1 ships a 3-section, 6-question
  skeleton. The next target is 9 sections (identity, companies and
  roles, projects, education, skills, decisions, learning,
  certificates, publications) with 5 or more questions each,
  branching, follow-up probing on weak answers, and ontology
  completeness checks.
- **render-jaso human reviewer**: `reviewers.md` is open for
  calibration. Onboard via the Korean reviewer issue template.
- **render-resume-en fixture set**: 5 pass and 5 fail per persona to
  match render-jaso coverage.
- **render-resume-en human reviewer**: senior US tech recruiter or
  hiring manager walks through the fixture set.
- **Quick-start path**: PDF-first onboarding so a fresh user reaches
  a first artifact in under two minutes.
- **Automatic LOCKEDIN_REPORT.md and master EXPERIENCE.md**: a single
  file at the vault root that lists all experiences in human-readable
  form, regenerated as the vault changes.
- **v1.2 orchestration**: explicit 5-step render pipeline plus
  parallel bulk-ingest dispatcher.
- **v1.3 vault curator**: quarterly duplicate-merge agent.
