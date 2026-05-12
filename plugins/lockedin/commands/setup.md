---
description: |
  One-time setup wizard for lockedin. Walks the user through:
  (1) wiring the HUD into Claude Code's statusLine, (2) default Q&A
  interview language, (3) vault path. Every choice is reversible. Safe
  to re-run; idempotent.

  Use when the user says any of: "/lockedin:setup", "setup lockedin",
  "lockedin 설정", "lockedin 설정해줘", "configure lockedin", "wire
  lockedin HUD".
---

# /lockedin:setup — one-time setup wizard

Run this once right after `/plugin install lockedin@lockedin`. Each
step is independent; the user can skip any of them.

## Where state lives

- **LockedIn runtime config**: `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/lockedin/config.json`
- **HUD script**: `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/lockedin/hud.py`
- **Backup of any previous statusLine**: `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/lockedin/.previous-statusline.json`
- **Claude Code settings**: `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/settings.json`

If the `lockedin` Python CLI is on PATH, prefer it for file mutations
(it has the safe-write logic already); otherwise perform the equivalent
operations directly with `Read` / `Write` tools.

## Step 1 — HUD wiring (statusLine)

The HUD shows vault state on the line directly above your input box:
`lockedin: 12n · 15e`. Refreshes every few hundred milliseconds.

1. Read `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/settings.json`. If
   `statusLine.command` already contains both `hud.py` and `lockedin`
   substrings, HUD is already wired — say so and skip to Step 2.
2. If a different `statusLine` exists, mention it. Ask the user once:
   *"Wire lockedin HUD? It will replace the existing statusLine command,
   but the previous config is backed up and `lockedin install
   --remove-hud` restores it."*
3. If accepted, run `lockedin install --setup-hud` via Bash. If the CLI
   is not available, do the equivalent directly:
   - Copy `${CLAUDE_PLUGIN_ROOT}/scripts/hud.py` to
     `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/lockedin/hud.py` (chmod 0755).
   - If the existing `statusLine` is not lockedin's, write it to
     `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/lockedin/.previous-statusline.json`
     before replacing.
   - Set `settings.json` `statusLine` to:
     `{"type": "command", "command": "python3 ~/.claude/lockedin/hud.py"}`.
4. Tell the user the change won't visibly take effect until they restart
   Claude Code.

## Step 2 — Default Q&A interview language

When the interview engine asks questions, what language should the
default prompts be in?

1. Ask: *"Default Q&A interview language? English or Korean? (You can
   override per-session with `--lang`.)"*
2. Write to
   `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/lockedin/config.json`:
   `{ "interview_language": "en" | "ko" }` (merging with existing
   config).

## Step 3 — Vault path

The vault is the folder of markdown notes lockedin reads and writes.

1. Default: `~/Documents/LockedIn/`. Ask: *"Use the default vault path
   (`~/Documents/LockedIn/`) or a custom location?"*
2. If custom: prompt for the path, expand `~`, confirm it does not
   already contain unrelated files. Write to `lockedin/config.json`:
   `{ "vault_path": "<absolute path>" }`. The CLI also respects the
   `LOCKEDIN_VAULT` environment variable if set.

## Final — mark setup complete

Merge into `lockedin/config.json`:

```json
{
  "setup_completed": "<ISO-8601 timestamp>",
  "setup_version": "1.2.0"
}
```

Then summarize what was configured:

- HUD: wired / skipped (with restart-required note if wired)
- Interview language: en | ko
- Vault path: `<path>`

Close with a concrete next step. Three paths, ordered from lowest
friction to highest commitment — recommend the first.

> *"Three ways to start, fastest first:*
>
> *1. **Just audit a resume** (zero commitment). Drop any resume PDF or*
>    *DOCX in chat and say 'audit my resume'. Returns a 5-dimension*
>    *calibrated score in about 30 seconds. No vault, no merge.*
>
> *2. **Absorb a resume into the vault.** Drop the same file and say*
>    *'absorb my resume'. lockedin will parse it and propose entities*
>    *to add. After the merge you can refine, score, or render.*
>
> *3. **Sample-data preview.** Say 'load demo' if you'd rather see the*
>    *renderers running on fixture data first, before committing your*
>    *own experience.*
>
> *Re-run `/lockedin:setup` any time to change settings."*

### Demo vault loading (opt-in only)

If the user explicitly asks for "load demo" or "sample data" or
"preview" after setup, run the deterministic seed:

```
lockedin init --fixture examples/sample-vault.yaml --vault $VAULT
```

Demo vault loading is opt-in by design. A 12-entity demo vault is
sparse enough that renderers may produce uneven output (low
evidence_recall, generic phrasing); a user who sees that output as
their first lockedin experience can mis-learn the tool's quality.
PDF-first onboarding leaves the user's vault in a state where the
first render reflects real personal evidence rather than fixture
data.

## Reversibility

Each step is reversible:

- HUD: `lockedin install --remove-hud` (restores previous statusLine
  if any was backed up).
- Language / vault path: edit `lockedin/config.json` directly, or
  re-run `/lockedin:setup`.

## Skipping the wizard

The skill's main entry point detects when setup has not been run and
offers the wizard once per fresh session. The user may decline, in
which case `lockedin` still works with sensible defaults — only the
HUD line will not appear until they wire it.
