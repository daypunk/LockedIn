---
description: |
  One-time setup wizard for selfgraph. Walks the user through:
  (1) wiring the HUD into Claude Code's statusLine, (2) default Q&A
  interview language, (3) vault path. Every choice is reversible. Safe
  to re-run; idempotent.

  Use when the user says any of: "/selfgraph:setup", "setup selfgraph",
  "selfgraph 설정", "selfgraph 설정해줘", "configure selfgraph", "wire
  selfgraph HUD".
---

# /selfgraph:setup — one-time setup wizard

Run this once right after `/plugin install selfgraph@selfgraph`. Each
step is independent; the user can skip any of them.

## Where state lives

- **Selfgraph runtime config**: `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/selfgraph/config.json`
- **HUD script**: `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/selfgraph/hud.py`
- **Backup of any previous statusLine**: `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/selfgraph/.previous-statusline.json`
- **Claude Code settings**: `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/settings.json`

If the `selfgraph` Python CLI is on PATH, prefer it for file mutations
(it has the safe-write logic already); otherwise perform the equivalent
operations directly with `Read` / `Write` tools.

## Step 1 — HUD wiring (statusLine)

The HUD shows vault state on the line directly above your input box:
`selfgraph: 12n · 15e`. Refreshes every few hundred milliseconds.

1. Read `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/settings.json`. If
   `statusLine.command` already contains both `hud.py` and `selfgraph`
   substrings, HUD is already wired — say so and skip to Step 2.
2. If a different `statusLine` exists, mention it. Ask the user once:
   *"Wire selfgraph HUD? It will replace the existing statusLine command,
   but the previous config is backed up and `selfgraph install
   --remove-hud` restores it."*
3. If accepted, run `selfgraph install --setup-hud` via Bash. If the CLI
   is not available, do the equivalent directly:
   - Copy `${CLAUDE_PLUGIN_ROOT}/scripts/hud.py` to
     `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/selfgraph/hud.py` (chmod 0755).
   - If the existing `statusLine` is not selfgraph's, write it to
     `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/selfgraph/.previous-statusline.json`
     before replacing.
   - Set `settings.json` `statusLine` to:
     `{"type": "command", "command": "python3 ~/.claude/selfgraph/hud.py"}`.
4. Tell the user the change won't visibly take effect until they restart
   Claude Code.

## Step 2 — Default Q&A interview language

When the interview engine asks questions, what language should the
default prompts be in?

1. Ask: *"Default Q&A interview language? English or Korean? (You can
   override per-session with `--lang`.)"*
2. Write to
   `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/selfgraph/config.json`:
   `{ "interview_language": "en" | "ko" }` (merging with existing
   config).

## Step 3 — Vault path

The vault is the folder of markdown notes selfgraph reads and writes.

1. Default: `~/.selfgraph/`. Ask: *"Use the default vault path
   (`~/.selfgraph/`) or a custom location?"*
2. If custom: prompt for the path, expand `~`, confirm it does not
   already contain unrelated files. Write to `selfgraph/config.json`:
   `{ "vault_path": "<absolute path>" }`. The CLI also respects the
   `SELFGRAPH_VAULT` environment variable if set.

## Final — mark setup complete

Merge into `selfgraph/config.json`:

```json
{
  "setup_completed": "<ISO-8601 timestamp>",
  "setup_version": "0.0.1"
}
```

Then summarize what was configured:

- HUD: wired / skipped (with restart-required note if wired)
- Interview language: en | ko
- Vault path: `<path>`

Close with a concrete next step: *"Try saying 'log today's meeting' or
'absorb a resume.pdf' to start. Re-run `/selfgraph:setup` any time to
change settings."*

## Reversibility

Each step is reversible:

- HUD: `selfgraph install --remove-hud` (restores previous statusLine
  if any was backed up).
- Language / vault path: edit `selfgraph/config.json` directly, or
  re-run `/selfgraph:setup`.

## Skipping the wizard

The skill's main entry point detects when setup has not been run and
offers the wizard once per fresh session. The user may decline, in
which case `selfgraph` still works with sensible defaults — only the
HUD line will not appear until they wire it.
