# TOOLS.md — lockedin-audit tool requirements

Lists the tools and CLI commands this skill requires for each mode.

## Bash (required for drive-by entry point)

```bash
lockedin ingest <path> --dry-run
```

Used in drive-by mode to extract source text without mutating the
vault. The `--dry-run` flag ensures no vault writes. The skill reads
stdout (the extracted text) and passes it to the scorer.

Exit code 0 = success. Non-zero = surface error to user and abort.

## File system reads (required)

The skill reads the following files during execution. All reads are
read-only. No file writes by this skill (except through the explicit
vault-update confirmation flow in Mode 2 / Mode 3 post-ingest).

| File | Purpose |
| --- | --- |
| `plugins/lockedin/skills/lockedin-audit/RUBRIC.md` | Document type routing |
| `plugins/lockedin/skills/lockedin-render-resume-en/RUBRIC.md` | English resume dimension definitions |
| `plugins/lockedin/skills/lockedin-render-jaso/RUBRIC.md` | Korean cover letter (jaso) dimension definitions |
| `plugins/lockedin/skills/lockedin-render-resume-en/banned_phrases.json` | English banned phrases |
| `plugins/lockedin/skills/lockedin-render-jaso/banned_phrases.json` | Korean banned phrases |
| `<vault>/experience/**/*.md` | Vault entities (post-ingest mode only) |

## Vault writes (Mode 2 / Mode 3, post-ingest only)

Vault entity updates go through the `lockedin` CLI, not direct file
writes:

```bash
lockedin ingest --patch <entity_slug> --field <field> --value <value>
```

Or if no patch subcommand exists, the skill outputs the changes for
the user to apply manually via `lockedin ingest` with a revised
source file. Direct markdown file writes are permissible only with
explicit user confirmation and only to files under `LOCKEDIN_VAULT`.

## JSON parsing

The reviewer turn emits a single JSON object. The orchestrator uses
`json.loads()` to parse it. If parsing fails, the orchestrator asks
the reviewer to retry with clean JSON output (no prose prefix/suffix).

## No Python API calls

This skill does not call the Anthropic API directly. All reasoning
runs through Claude Code skills on the user's existing subscription.
The `lockedin doctor` command confirms subscription path is intact.

## Optional: PDF / DOCX extraction

For drive-by audits where `lockedin ingest --dry-run` returns an
empty result (unsupported format or extraction failure), the skill
falls back to:

```bash
python3 -c "
from lockedin.ingest.pdf import extract_text
print(extract_text('<path>'))
" 2>/dev/null
```

Or for DOCX:

```bash
python3 -c "
from lockedin.ingest.docx import extract_text
print(extract_text('<path>'))
" 2>/dev/null
```

If both fail, surface the error to the user and ask them to paste
the resume text directly.
