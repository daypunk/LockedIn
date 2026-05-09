# Changelog

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
