#!/usr/bin/env python3
"""lockedin HUD — self-contained statusLine emitter.

Output (one line, exit 0):
    lockedin X.Y.Z │ 5h:NN% · wk:NN% │ experience: Nn · Me

Order, left to right:
    1. service name + version (cyan)
    2. Claude Code usage in the rolling 5-hour and 7-day windows (color
       grades green→yellow→red as % rises). Counted as user turns from
       Claude's session JSONL files at ~/.claude/projects/*/*.jsonl.
    3. experience state — node count, edge count, dangling references.

Defaults assume rough Pro-tier thresholds (50 user turns / 5h, 350 /
week). Override with LOCKEDIN_HUD_5H_LIMIT and LOCKEDIN_HUD_WK_LIMIT.

Color is on by default. Disable via NO_COLOR or LOCKEDIN_HUD_COLOR=0.

The script defers to the installed lockedin package if available so
the package and standalone stay in sync; otherwise the inline fallback
runs (vault walker + session-file scanner, stdlib only).

The HUD must NEVER crash the statusLine — runs every few hundred ms.
On any unexpected error, falls back to printing 'lockedin' and exit 0.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# --- defer to the package if available --------------------------------------

try:
    from lockedin.commands.hud import hud as _package_hud  # type: ignore[import-not-found]

    sys.exit(_package_hud([]))
except Exception:  # noqa: BLE001 — any import-time issue → use fallback
    pass


# --- self-contained fallback ------------------------------------------------

VERSION = "1.0.0"

DEFAULT_5H_LIMIT = 50
DEFAULT_WK_LIMIT = 350

# ANSI color codes
C_CYAN = "96"     # service name
C_DIM = "2"       # separators / labels
C_GREEN = "32"    # safe usage
C_YELLOW = "33"   # mid usage
C_RED = "31"      # high usage

_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def _wants_color() -> bool:
    if "NO_COLOR" in os.environ:
        return False
    return os.environ.get("LOCKEDIN_HUD_COLOR", "1") != "0"


def _ansi(text: str, code: str, on: bool) -> str:
    if not on or not code:
        return text
    return f"\x1b[{code}m{text}\x1b[0m"


def _usage_color(pct: int) -> str:
    if pct >= 80:
        return C_RED
    if pct >= 50:
        return C_YELLOW
    return C_GREEN


def _resolve_vault() -> Path:
    explicit = os.environ.get("LOCKEDIN_VAULT")
    if explicit:
        return Path(explicit).expanduser()
    return Path.home() / ".lockedin"


def _is_vault_note(path: Path) -> bool:
    if path.name.startswith("."):
        return False
    parts = path.parts
    return "outputs" not in parts and "templates" not in parts


def _read_frontmatter_value(header: str, key: str) -> str | None:
    for line in header.split("\n"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        if k.strip() == key:
            return v.strip()
    return None


def _parse_links(value: str) -> list[dict]:
    if not value or value[0] != "[":
        return []
    try:
        loaded = json.loads(value)
    except json.JSONDecodeError:
        return []
    return [item for item in loaded if isinstance(item, dict)]


def _walk_vault(vault: Path) -> tuple[int, int, set[str], set[str]]:
    nodes = 0
    edges = 0
    slugs: set[str] = set()
    targets: set[str] = set()
    for path in vault.rglob("*.md"):
        if not _is_vault_note(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        m = _FRONTMATTER_RE.match(text)
        if not m:
            continue
        header = m.group(1)
        slug = _read_frontmatter_value(header, "slug")
        if slug:
            slug = slug.strip("\"'")
            slugs.add(slug)
        nodes += 1
        for link in _parse_links(_read_frontmatter_value(header, "links") or ""):
            edges += 1
            target = link.get("object")
            if isinstance(target, str):
                targets.add(target)
    return nodes, edges, slugs, targets


def _claude_projects_dir() -> Path:
    explicit = os.environ.get("CLAUDE_CONFIG_DIR")
    if explicit:
        return Path(explicit).expanduser() / "projects"
    return Path.home() / ".claude" / "projects"


def _count_user_turns_within(now: datetime) -> tuple[int, int]:
    """Return (user-turns within 5h, user-turns within 7d) across all sessions."""
    proj_dir = _claude_projects_dir()
    if not proj_dir.exists():
        return 0, 0
    cut_5h = now - timedelta(hours=5)
    cut_wk = now - timedelta(days=7)
    five_h = 0
    week = 0
    for jsonl in proj_dir.rglob("*.jsonl"):
        try:
            with jsonl.open("r", encoding="utf-8") as fh:
                for line in fh:
                    if '"type":"user"' not in line and '"type": "user"' not in line:
                        continue
                    try:
                        d = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if d.get("type") != "user":
                        continue
                    ts_raw = d.get("timestamp")
                    if not isinstance(ts_raw, str):
                        continue
                    try:
                        ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
                    except ValueError:
                        continue
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=timezone.utc)
                    if ts >= cut_wk:
                        week += 1
                        if ts >= cut_5h:
                            five_h += 1
        except OSError:
            continue
    return five_h, week


def _render() -> str:
    color = _wants_color()
    parts: list[str] = []

    # 1. service + version (always present)
    parts.append(_ansi(f"lockedin {VERSION}", C_CYAN, color))

    # 2. Claude usage (best-effort)
    limit_5h = max(1, int(os.environ.get("LOCKEDIN_HUD_5H_LIMIT", DEFAULT_5H_LIMIT)))
    limit_wk = max(1, int(os.environ.get("LOCKEDIN_HUD_WK_LIMIT", DEFAULT_WK_LIMIT)))
    now = datetime.now(timezone.utc)
    used_5h, used_wk = _count_user_turns_within(now)
    if used_5h or used_wk:
        pct_5h = min(999, round(100 * used_5h / limit_5h))
        pct_wk = min(999, round(100 * used_wk / limit_wk))
        usage = (
            _ansi(f"5h:{pct_5h}%", _usage_color(pct_5h), color)
            + _ansi(" · ", C_DIM, color)
            + _ansi(f"wk:{pct_wk}%", _usage_color(pct_wk), color)
        )
        parts.append(usage)

    # 3. experience state
    vault = _resolve_vault()
    if vault.exists():
        nodes, edges, slugs, targets = _walk_vault(vault)
        if nodes == 0:
            parts.append(_ansi("experience empty", C_DIM, color))
        else:
            label = _ansi("experience:", C_DIM, color)
            counts = _ansi(f"{nodes}n · {edges}e", C_CYAN, color)
            dangling = len(targets - slugs)
            if dangling:
                counts = (
                    counts
                    + _ansi(" · ", C_DIM, color)
                    + _ansi(f"{dangling} dangling", C_RED, color)
                )
            parts.append(f"{label} {counts}")

    return _ansi(" │ ", C_DIM, color).join(parts)


def main() -> int:
    try:
        line = _render()
    except Exception:  # noqa: BLE001 — HUD must NEVER crash the statusLine
        line = "lockedin"
    sys.stdout.write(line + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
