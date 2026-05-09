"""lockedin hud — emit a one-line statusLine snippet for Claude Code.

Order, left to right (separated by `│`):
  1. service name + version (cyan)
  2. Claude Code usage in rolling 5-hour and 7-day windows (color-graded)
  3. experience state — node count, edge count, dangling references

Usage values are pulled from Anthropic's OAuth usage endpoint when
the user's Claude Code OAuth credentials are available. macOS reads
the credential from Keychain; Linux and Windows from
``~/.claude/.credentials.json``. If the OAuth path is unavailable,
the legacy heuristic that counted user turns from session JSONL
files is used as a fallback. The legacy heuristic uses
``LOCKEDIN_HUD_5H_LIMIT`` and ``LOCKEDIN_HUD_WK_LIMIT`` as turn
thresholds.

Color is on by default. Disable via ``NO_COLOR`` or
``LOCKEDIN_HUD_COLOR=0``.

The HUD must NEVER crash the statusLine — runs every few hundred ms.
On any unexpected error, falls back to ``lockedin`` and exits 0.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from lockedin import __version__
from lockedin.config import resolve_vault
from lockedin.hud import get_usage
from lockedin.storage.notes import read_entity

DEFAULT_5H_LIMIT = 50
DEFAULT_WK_LIMIT = 350

# ANSI color codes
C_CYAN = "96"
C_DIM = "2"
C_GREEN = "32"
C_YELLOW = "33"
C_RED = "31"


def _is_vault_note(path: Path) -> bool:
    if path.name.startswith("."):
        return False
    parts = path.parts
    return "outputs" not in parts and "templates" not in parts


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


def _wants_color(flag: bool) -> bool:
    if "NO_COLOR" in os.environ:
        return False
    if flag:
        return True
    return os.environ.get("LOCKEDIN_HUD_COLOR", "1") != "0"


def _claude_projects_dir() -> Path:
    explicit = os.environ.get("CLAUDE_CONFIG_DIR")
    if explicit:
        return Path(explicit).expanduser() / "projects"
    return Path.home() / ".claude" / "projects"


def _count_user_turns(now: datetime) -> tuple[int, int]:
    """Return (user turns in last 5h, user turns in last 7d)."""
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


def _walk_vault(vault: Path) -> tuple[int, int, set[str], set[str]]:
    nodes = 0
    edges = 0
    slugs: set[str] = set()
    targets: set[str] = set()
    for path in vault.rglob("*.md"):
        if not _is_vault_note(path):
            continue
        try:
            entity = read_entity(path)
        except Exception:  # noqa: BLE001
            continue
        nodes += 1
        slugs.add(entity.slug)
        for link in entity.links:
            if not isinstance(link, dict):
                continue
            edges += 1
            tgt = link.get("object")
            if isinstance(tgt, str):
                targets.add(tgt)
    return nodes, edges, slugs, targets


def _render(vault: Path, color: bool) -> str:
    parts: list[str] = []

    # 1. service + version (brand display in user-facing HUD)
    parts.append(_ansi(f"LockedIn {__version__}", C_CYAN, color))

    # 2. Claude usage. Prefer Anthropic OAuth utilization when
    # available; fall back to the legacy heuristic counting session
    # JSONL user turns.
    pct_5h: int | None = None
    pct_wk: int | None = None
    oauth_payload = get_usage()
    if oauth_payload is not None:
        pct_5h = min(999, round(100 * oauth_payload.get("five_hour", 0)))
        pct_wk = min(999, round(100 * oauth_payload.get("seven_day", 0)))
    else:
        limit_5h = max(1, int(os.environ.get("LOCKEDIN_HUD_5H_LIMIT", DEFAULT_5H_LIMIT)))
        limit_wk = max(1, int(os.environ.get("LOCKEDIN_HUD_WK_LIMIT", DEFAULT_WK_LIMIT)))
        now = datetime.now(timezone.utc)
        used_5h, used_wk = _count_user_turns(now)
        if used_5h or used_wk:
            pct_5h = min(999, round(100 * used_5h / limit_5h))
            pct_wk = min(999, round(100 * used_wk / limit_wk))
    if pct_5h is not None and pct_wk is not None:
        usage = (
            _ansi(f"5h:{pct_5h}%", _usage_color(pct_5h), color)
            + _ansi(" · ", C_DIM, color)
            + _ansi(f"wk:{pct_wk}%", _usage_color(pct_wk), color)
        )
        parts.append(usage)

    # 3. experience state
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


def hud(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lockedin hud")
    parser.add_argument("--color", action="store_true", help="force ANSI color")
    parser.add_argument("--no-color", action="store_true", help="disable color")
    parser.add_argument("--vault", help="vault path (default ~/Documents/LockedIn/)")
    args = parser.parse_args(argv)

    color = False if args.no_color else _wants_color(args.color)
    vault = resolve_vault(args.vault)
    try:
        line = _render(vault, color)
    except Exception:  # noqa: BLE001 — HUD must NEVER crash the statusLine
        line = "lockedin"
    sys.stdout.write(line + "\n")
    return 0
