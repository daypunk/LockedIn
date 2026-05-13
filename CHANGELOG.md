# Changelog

## [1.2.0] — 2026-05-12

### Added

- `lockedin-audit` skill: drive-by (no vault) and post-ingest 3-mode scorer (`score` / `refine` / `refine-score`). Router-only `RUBRIC.md` that reuses `render-resume-en` and `render-jaso` rubrics; no dimension duplication.
- `audit` CLI subcommand (`/lockedin audit <path>`) and `interview` alias for `init`.
- Real document ingest: PDF (`pypdf`), DOCX (`python-docx`), markdown, and plain text now expose `extract_text()` and regex-based `parse()` returning grounding dicts (dates, urls, emails, candidate orgs). Previously `NotImplementedError` stubs.
- Interview resumability: state persistence at `<vault>/.lockedin/interview-state.json`, atomic write, pause/skip/resume keywords, progress banner `[Section M/N · Q N/N]`, `sections=[…]` filter, `fresh=True` restart.
- Automatic edge inference: the interview engine now populates `entity.links` at session completion, inferring all valid edges from entity co-presence using domain/range rules in `lockedin/ontology/schema.py` (e.g. person + company → `held_role_at`, project + skill → `uses_skill`, project + achievement → `produced`). Document-ingest-only predicates (`mentions`, `derived_from`) are excluded. Inference is idempotent — edges are recomputed from scratch each run.
- Interview question bank expanded from 6 to 49 questions across 9 sections (identity, companies and roles, projects, education, certificates, publications, volunteer experience, languages, decisions and learning).
- Korean cover letter and English resume calibration parity: `banned_phrases.json` schema v2 (object array with category/severity/sources), 3 pass + 3 fail fixtures per skill, `test_jaso_calibration.py` and `test_resume_en_calibration.py`.
- AI-native cross-source calibration shipped for `lockedin-render-interview` (7 sources, 25 banned phrases) and `lockedin-render-ideas` (7 sources, 27 banned phrases) with 3 pass + 3 fail fixtures each.
- `lockedin doctor` now reports: audit skill installation, `pypdf` / `python-docx` / `PyYAML` availability, interview-state progress summary.
- New `README.ja.md` (Japanese); language switcher across all four READMEs links every locale.
- CI lint additions: `tests/test_research_allowlist.py` (citation host enforcement), `tests/test_readme_promises.py` (README ↔ code drift guard).
- `lockedin-render-resume-en` expanded from 3 to **10 built-in personas**. New persona spec files at `plugins/lockedin/skills/lockedin-render-resume-en/personas/`: `backend-senior`, `frontend-senior`, `mobile-senior`, `data-engineer-mid`, `ml-engineer-mid`, `designer-senior`, `marketing-mid`. Each spec carries skill cluster, responsibility patterns, tone guidance, action verb cluster, persona-specific banned phrases, and persona-fit scoring hints. The 3 existing personas (`us-tech-senior`, `us-tech-mid`, `pm-product`) also gained dedicated spec files in the same directory. Fixtures expanded with 1 pass + 1 fail per new persona, and `test_resume_en_calibration.py` gained per-persona spec-coverage invariants.

### Changed

- Ingest layer refactor: per-format modules at `lockedin/ingest/{pdf,docx,markdown,text}.py` now own `extract_text` and `parse`; `lockedin/commands/ingest_dry.py` slimmed to a thin orchestrator. Shared regex helpers extracted into `_parse_helpers.py` and `_section_heuristics.py`.
- Schema looseness for gentler capture: `role.start_date` and `meeting.date` no longer required. `meeting` description widened to include 1:1s, code reviews, and mentoring sessions. The vault accepts thin entities; renderer turns ask for missing precision when needed.
- Main skill `SKILL.md`: `audit` flagged as the lowest-friction first try (Step 0 in Core flow); activation triggers include audit-related natural language.
- `/lockedin:setup` wizard final guidance restructured to a 3-path menu (audit → absorb → demo).
- Render CLI choices expanded from `{jaso, resume}` to `{jaso, resume, interview, ideas}` to match shipped skills.
- AI-native posture made explicit in `CLAUDE.md`: rubric calibration goes through cross-source AI research, not human reviewer engagements.
- Interview completes with a next-steps footer and an explicit `EXPERIENCE.md` refresh.
- Test count: 73 → 231.

### Removed

- `.github/ISSUE_TEMPLATE/korean_reviewer_onboarding.yml` (AI-native posture).

### Fixed

- `lockedin/ontology/schema.py` module docstring corrected from "v0.2" to "v3" (matches `SCHEMA_VERSION = 3`).
- `docs/ontology-spec.md` and `docs/ontology-mapping.md`: version labels synced to v3; `aliases` (person/company) and `provenance` system field documented.
- `docs/architecture.md`: install paths updated from the legacy `uv tool install` flow to the current plugin marketplace + optional Python CLI accelerator.
- `tests/research-allowlist.txt`: added `linkareer.com` (was only `linkareer.co.kr`); both are the same service.

## [1.1.0] — 2026-05-09

### Breaking

- Vault default path moved to `~/Documents/LockedIn/` (was hidden under `~/.selfgraph/`).
- Default template directory renamed `career/` → `experience/`. `lockedin migrate` renames it in place.
- Env vars renamed `SELFGRAPH_*` → `LOCKEDIN_*`.
- Slash command renamed `/selfgraph:setup` → `/lockedin:setup`.
- `lockedin render graph` command and the bundled `force-graph` viz removed.

### Added

- Two new renderer skills: `lockedin-render-interview` and `lockedin-render-ideas`.
- `lockedin migrate` upgrades the vault to schema v3 (adds `provenance` and, for person/company, `aliases`) and renames `career/` → `experience/`.
- `lockedin experience <slug>` synthesises a denormalized view across role, project, achievement, and skill nodes.
- `lockedin refresh` rebuilds the master `EXPERIENCE.md` at the vault root.
- HUD pulls real Anthropic OAuth utilization with reset countdowns; falls back to a heuristic when OAuth is unavailable.
- `[[type/slug]]` references in renderer output are resolved to natural-language labels.

### Changed

- Renamed to **LockedIn** (was selfgraph). GitHub repo renamed; v1.0.0 tag follows.
- HUD label moved from cyan to brand orange and from `vault:` to `experience:`.
- Renderer prompts enforce one experience per paragraph with explicit transitions.
- Schema bumped to v3.

## [1.0.0] — 2026-05-01

### Added

- Initial release as a Claude Code plugin.
- Markdown vault with 15 entity types and 15 typed edge predicates (schema v2).
- Two calibrated renderer skills: `render-jaso` (Korean cover letter, 5 dimensions, 28-entry banned phrase list, 5 pass / 5 fail fixtures across 5 industries) and `render-resume-en` (English resume, 5 dimensions, 44 banned phrases + 8 soft-overuse, 3 personas).
- Two-turn writer/reviewer pattern with cross-context rubric reload.
- Deterministic CLI: `install`, `init --fixture`, `ingest --dry-run`, `validate`, `template`, `doctor`, `hud`.
- HUD status line, one-time setup wizard, and OSS infrastructure (CONTRIBUTING, CODE_OF_CONDUCT, ISSUE_TEMPLATE).
