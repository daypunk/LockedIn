# HUD integration

Claude Code's bottom **statusLine** is the only legitimate hook for
showing one line of lockedin state at a glance. The chat chrome above
it is closed; the line at the very bottom of your terminal (e.g. tmux's
status bar) is also unrelated. Only the line directly under your chat
input is what lockedin populates.

## Output shapes

```
lockedin                              # no vault yet
lockedin: vault empty                 # vault dir exists, no notes
lockedin: 12n · 15e                   # 12 nodes, 15 edges
lockedin: 12n · 15e · 3 dangling      # also flag dangling references
```

Why these signals:

- **node count** — the only number a casual user wants to see grow over
  time ("Am I building this?").
- **edge count** — surfaces whether the graph is actually connected or
  just a pile of disconnected notes.
- **dangling reference count** — fast feedback for vault-hygiene
  problems (a deleted note that was still linked from somewhere).

## How it gets wired

The recommended path is the one-time `/lockedin:setup` wizard inside
Claude Code (you'd run it right after installing the plugin). Step 1 of
that wizard handles the HUD: one "yes" is enough.

If you skipped the wizard and start using lockedin anyway, the skill
notices and offers the wizard once per session as a safety net.

For scripted or non-interactive setup, the equivalent CLI commands work
the same way:

```bash
lockedin install --setup-hud         # wire it
lockedin install --remove-hud        # undo (restores any previous statusLine)
```

Behind the scenes:

- The HUD script is copied to
  `${CLAUDE_CONFIG_DIR:-~/.claude}/lockedin/hud.py` (a stable path that
  doesn't change with plugin upgrades).
- `settings.json` gets `"statusLine": {"type": "command", "command":
  "python3 ~/.claude/lockedin/hud.py"}`.
- Any existing `statusLine` config is backed up to
  `~/.claude/lockedin/.previous-statusline.json` before being replaced;
  `--remove-hud` restores it.

## Color

Output is plain ASCII by default so it stays readable in any terminal.
Force ANSI color via `LOCKEDIN_HUD_COLOR=1`. `NO_COLOR` always wins.

## Failure mode

The HUD must **never** crash the statusLine — it runs every few hundred
milliseconds. On any unexpected error the script falls back to printing
the bare label `lockedin` and exits 0.

## What we deliberately don't show

- **Last activity timestamp** — would require additional state and may
  drift across multi-device vault syncs. Not worth the complexity for v1.
- **Active skill / current turn** — Claude Code does not expose this to
  external commands.
- **Token usage / model tier** — out of scope; if your Claude Code setup
  already shows it elsewhere, leave it there.
- **Type breakdown** (e.g. `5p · 7r · 3a`) — too noisy at glance, push
  to `lockedin validate` or a future `lockedin stats` command.
