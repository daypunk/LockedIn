---
description: |
  Setup wizard for lockedin. Walks the user through:
  (1) wiring the HUD into Claude Code's statusLine, (2) default Q&A
  interview language, (3) vault path. Every choice is reversible. Safe
  to re-run; idempotent.

  Use when the user says any of: "/lockedin:setup", "setup lockedin",
  "lockedin 설정", "lockedin 설정해줘", "configure lockedin", "wire
  lockedin HUD".
---

# /lockedin:setup — wizard

Run after `/plugin install lockedin@lockedin`, or any time you want to
reconfigure. Each step is independent and reversible.

## Where state lives

- **LockedIn runtime config**: `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/lockedin/config.json`
- **HUD script**: `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/lockedin/hud.py`
- **Backup of any previous statusLine**: `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/lockedin/.previous-statusline.json`
- **Claude Code settings**: `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/settings.json`

If the `lockedin` Python CLI is on PATH, prefer it for file mutations
(it has the safe-write logic already); otherwise perform the equivalent
operations directly with `Read` / `Write` tools.

---

## Boot check

Perform this section first, before anything else.

### 1. Read existing config

Run:

```bash
CONFIG_FILE="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/lockedin/config.json"
cat "$CONFIG_FILE" 2>/dev/null || echo "__MISSING__"
```

Parse the result:

- If the output is `__MISSING__` or the file does not contain a
  `setup_completed` key, set `already_configured=false`.
- Otherwise set `already_configured=true` and note the stored
  `setup_version` value (may be absent in older configs).

### 2. Detect installed plugin version

Run:

```bash
python3 -c "from lockedin import __version__; print(__version__)" 2>/dev/null \
  || cat "${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json" 2>/dev/null \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('version','unknown'))" 2>/dev/null \
  || echo "unknown"
```

Capture the first successful output as `current_version`. If all
commands fail, set `current_version="unknown"` and continue.

### 3. Fetch latest available version (best-effort, fail gracefully)

Try each fallback in order. Stop at the first success. If every
attempt fails, set `latest_version="unknown"` and continue silently —
**never crash or block on this step**.

```bash
# Attempt 1 — gh CLI
gh api repos/daypunk/LockedIn/releases/latest --jq .tag_name 2>/dev/null

# Attempt 2 — curl GitHub API
curl -sf https://api.github.com/repos/daypunk/LockedIn/releases/latest \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('tag_name',''))" 2>/dev/null
```

Strip any leading `v` prefix from the fetched string so it matches the
`x.y.z` form from `current_version`.

### 4. Branch

Evaluate the following conditions in order:

**Condition A** — `already_configured=false`
→ Go to **Path A — first-time setup**.

**Condition B** — `already_configured=true` AND `latest_version` is
known AND `latest_version` is newer than `current_version` (simple
string comparison: `latest_version != current_version` is sufficient
when you know the values are both semver and latest was fetched from
GitHub releases)
→ Go to **Path B — plugin update available**.

**Condition C** — `already_configured=true` AND (version is current OR
version is unknown)
→ Go to **Path C — partial update menu**.

---

## Path A — first-time setup

Run Step 1, Step 2, and Step 3 in sequence. Then run the **Final —
write setup_completed** section. This is the same flow as the original
wizard.

---

## Path B — plugin update available

Use AskUserQuestion to present:

> Plugin update available: **`<current_version>`** → **`<latest_version>`**.
> Updating first is recommended so the wizard configures the latest
> feature set.
>
> What would you like to do?

Options:
- `Update now (recommended)`
- `Skip and continue with current version`
- `Cancel`

**If user picks "Update now":**
Print the exact command they need to run:

```
/plugin update lockedin@lockedin
```

Tell them: "Run the command above, then re-run `/lockedin:setup` once
the update finishes." Exit cleanly.

**If user picks "Skip and continue with current version":**
Go to **Path C — partial update menu**.

**If user picks "Cancel":**
Print: "No changes made. Re-run `/lockedin:setup` any time." Exit
cleanly.

---

## Path C — partial update menu

Use AskUserQuestion to present:

> LockedIn is already configured (version `<current_version>`). What
> would you like to update?

Options:
- `HUD reconfigure`
- `Interview language change`
- `Vault path change`
- `Run full wizard again`
- `Cancel`

**HUD reconfigure** → run Step 1 only, then run **Final — write
setup_completed**.

**Interview language change** → run Step 2 only, then run **Final —
write setup_completed**.

**Vault path change** → run Step 3 only, then run **Final — write
setup_completed**.

**Run full wizard again** → run Step 1, Step 2, and Step 3 in
sequence, then run **Final — write setup_completed**.

**Cancel** → print: "No changes made. Re-run `/lockedin:setup` any
time." Exit cleanly.

---

## Step 1 — HUD wiring (statusLine)

The HUD shows vault state on the line directly above your input box:
`lockedin: 12n · 15e`. Refreshes every few hundred milliseconds.

1. Read `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/settings.json`. If
   `statusLine.command` already contains both `hud.py` and `lockedin`
   substrings, HUD is already wired — say so and skip to the next step.
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

---

## Step 2 — Default interview language

When the interview engine asks questions, what language should the
default prompts be in?

1. Ask: *"Default Q&A interview language? English or Korean? (You can
   override per-session with `--lang`.)"*
2. Write to
   `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/lockedin/config.json`:
   `{ "interview_language": "en" | "ko" }` (merging with existing
   config).

---

## Step 3 — Vault path

The vault is the folder of markdown notes lockedin reads and writes.

1. Default: `~/Documents/LockedIn/`. Ask: *"Use the default vault path
   (`~/Documents/LockedIn/`) or a custom location?"*
2. If custom: prompt for the path, expand `~`, confirm it does not
   already contain unrelated files. Write to `lockedin/config.json`:
   `{ "vault_path": "<absolute path>" }`. The CLI also respects the
   `LOCKEDIN_VAULT` environment variable if set.

---

## Final — write setup_completed

Merge the following fields into
`${CLAUDE_CONFIG_DIR:-$HOME/.claude}/lockedin/config.json`, preserving
all existing keys:

```json
{
  "setup_completed": "<ISO-8601 timestamp>",
  "setup_version": "<current_version>"
}
```

Use `python3` to do a safe read-modify-write:

```bash
python3 - <<'EOF'
import json, os, datetime, pathlib

cfg_dir = pathlib.Path(os.environ.get("CLAUDE_CONFIG_DIR", pathlib.Path.home() / ".claude")) / "lockedin"
cfg_dir.mkdir(parents=True, exist_ok=True)
cfg_file = cfg_dir / "config.json"

existing = {}
if cfg_file.exists():
    try:
        existing = json.loads(cfg_file.read_text())
    except Exception:
        pass

existing["setup_completed"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
# setup_version is filled in by the wizard using current_version detected in Boot check
# Replace SETUP_VERSION_PLACEHOLDER with the actual version string before running
existing["setup_version"] = "SETUP_VERSION_PLACEHOLDER"

cfg_file.write_text(json.dumps(existing, indent=2) + "\n")
print("Config written to", cfg_file)
EOF
```

Replace `SETUP_VERSION_PLACEHOLDER` with the `current_version` value
captured during the Boot check before executing the script.

### Summary output — first-time setup (Path A and "Run full wizard again")

After the final write, summarize what was configured:

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

### Summary output — partial update (Path C single-step selections)

After the final write, print the one setting that changed and close with:

> "All set. Re-run `/lockedin:setup` any time."

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

---

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
