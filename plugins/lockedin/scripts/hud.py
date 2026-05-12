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

VERSION = "1.2.0"

DEFAULT_5H_LIMIT = 50
DEFAULT_WK_LIMIT = 350

# ANSI color codes
C_CYAN = "96"     # entity counts
C_DIM = "2"       # separators / labels / reset countdowns
C_GREEN = "32"    # safe usage
C_YELLOW = "33"   # mid usage
C_RED = "31"      # high usage
C_ORANGE = "38;5;208"  # 256-color orange for the brand version label


def _format_reset_delta(iso_string):
    """Turn an ISO-8601 reset timestamp into a compact countdown.

    Examples: "3h12m" for 3 hours 12 minutes from now; "2d4h" for 2
    days 4 hours; "<1m" for sub-minute. Returns empty string when the
    input is None or unparseable.
    """
    if not iso_string:
        return ""
    try:
        ts = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        delta = ts - datetime.now(timezone.utc)
        total_seconds = int(delta.total_seconds())
        if total_seconds <= 0:
            return "now"
        if total_seconds < 60:
            return "<1m"
        minutes = total_seconds // 60
        hours = minutes // 60
        days = hours // 24
        if days >= 1:
            return f"{days}d{hours - days * 24}h"
        if hours >= 1:
            return f"{hours}h{minutes - hours * 60}m"
        return f"{minutes}m"
    except (ValueError, TypeError):
        return ""

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


# --- inline Anthropic OAuth utilization (mirrors lockedin.hud.oauth_usage) ----
#
# The standalone script may run on a machine where the lockedin Python package
# is not on sys.path. The package import at the top of this file then fails
# silently and we fall through to this fallback section. To keep the HUD
# accurate even in that case, we duplicate the OAuth path here. The package
# version remains the source of truth and the test surface; this copy follows
# it.

_USAGE_URL = "https://api.anthropic.com/api/oauth/usage"
_KEYCHAIN_SERVICE = "Claude Code-credentials"
_OAUTH_CACHE_TTL_SECONDS = 60
_OAUTH_REQUEST_TIMEOUT_SECONDS = 5


def _claude_config_dir() -> Path:
    explicit = os.environ.get("CLAUDE_CONFIG_DIR")
    if explicit:
        return Path(explicit).expanduser()
    return Path.home() / ".claude"


def _credentials_path_filesystem() -> Path:
    return _claude_config_dir() / ".credentials.json"


def _oauth_cache_dir() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Caches" / "lockedin"
    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA")
        if local:
            return Path(local) / "lockedin" / "Cache"
        return Path.home() / "AppData" / "Local" / "lockedin" / "Cache"
    xdg = os.environ.get("XDG_CACHE_HOME")
    if xdg:
        return Path(xdg) / "lockedin"
    return Path.home() / ".cache" / "lockedin"


def _oauth_cache_path() -> Path:
    return _oauth_cache_dir() / "usage.json"


def _read_oauth_cache():
    import time
    try:
        path = _oauth_cache_path()
        if not path.exists():
            return None
        raw = json.loads(path.read_text(encoding="utf-8"))
        ts = raw.get("ts")
        payload = raw.get("payload")
        if not isinstance(ts, (int, float)) or not isinstance(payload, dict):  # noqa: UP038
            return None
        if time.time() - ts > _OAUTH_CACHE_TTL_SECONDS:
            return None
        return payload
    except (OSError, ValueError):
        return None


def _write_oauth_cache(payload: dict) -> None:
    import time
    try:
        path = _oauth_cache_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"ts": time.time(), "payload": payload}),
            encoding="utf-8",
        )
    except OSError:
        return


def _read_credentials_keychain_macos():
    import shutil
    import subprocess
    if shutil.which("security") is None:
        return None
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", _KEYCHAIN_SERVICE, "-w"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    blob = result.stdout.strip()
    if not blob:
        return None
    try:
        return json.loads(blob)
    except ValueError:
        return None


def _read_credentials_filesystem():
    path = _credentials_path_filesystem()
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _read_credentials():
    if sys.platform == "darwin":
        creds = _read_credentials_keychain_macos()
        if creds is not None:
            return creds
        return _read_credentials_filesystem()
    return _read_credentials_filesystem()


def _extract_access_token(creds):
    if not isinstance(creds, dict):
        return None
    candidates = []
    oauth = creds.get("claudeAiOauth")
    if isinstance(oauth, dict):
        candidates.append(oauth.get("accessToken"))
    candidates.append(creds.get("access_token"))
    candidates.append(creds.get("accessToken"))
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return None


def _fetch_oauth_usage(token: str):
    import urllib.error
    import urllib.request
    request = urllib.request.Request(
        _USAGE_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "User-Agent": "lockedin-hud/1.1",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=_OAUTH_REQUEST_TIMEOUT_SECONDS) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, ValueError, TimeoutError, OSError):
        return None


def _normalize_oauth_payload(raw):
    if not isinstance(raw, dict):
        return None

    def _pull(value):
        if isinstance(value, dict):
            value = value.get("utilization")
        if isinstance(value, (int, float)):  # noqa: UP038
            v = float(value)
            return v / 100 if v > 1.5 else v
        return None

    def _pull_reset(value):
        if isinstance(value, dict):
            r = value.get("resets_at") or value.get("reset_time")
            if isinstance(r, str) and r.strip():
                return r.strip()
        return None

    five_raw = raw.get("five_hour") if "five_hour" in raw else raw.get("fiveHour")
    seven_raw = raw.get("seven_day") if "seven_day" in raw else raw.get("sevenDay")
    five = _pull(five_raw)
    seven = _pull(seven_raw)
    if five is None and seven is None:
        return None
    return {
        "five_hour": five if five is not None else 0.0,
        "seven_day": seven if seven is not None else 0.0,
        "five_hour_resets_at": _pull_reset(five_raw),
        "seven_day_resets_at": _pull_reset(seven_raw),
    }


def _oauth_usage():
    """Return {'five_hour': 0.x, 'seven_day': 0.x} or None.

    None means OAuth path unavailable; the caller should fall back to the
    legacy turn-counting heuristic.
    """
    cached = _read_oauth_cache()
    if cached is not None:
        return cached
    try:
        creds = _read_credentials()
        if creds is None:
            return None
        token = _extract_access_token(creds)
        if token is None:
            return None
        raw = _fetch_oauth_usage(token)
        if raw is None:
            return None
        payload = _normalize_oauth_payload(raw)
        if payload is None:
            return None
        _write_oauth_cache(payload)
        return payload
    except Exception:  # noqa: BLE001 — HUD must NEVER crash
        return None


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

    # 1. service + version (brand display in user-facing HUD)
    parts.append(_ansi(f"LockedIn {VERSION}", C_ORANGE, color))

    # 2. Claude usage. Prefer Anthropic OAuth utilization when available;
    # fall back to the legacy heuristic counting session JSONL user turns.
    # When OAuth gives us a reset timestamp we render it next to the
    # percentage in dim grey so the user sees how long until the window
    # rolls over.
    pct_5h = None
    pct_wk = None
    reset_5h = ""
    reset_wk = ""
    oauth_payload = _oauth_usage()
    if oauth_payload is not None:
        pct_5h = min(999, round(100 * oauth_payload.get("five_hour", 0)))
        pct_wk = min(999, round(100 * oauth_payload.get("seven_day", 0)))
        reset_5h = _format_reset_delta(oauth_payload.get("five_hour_resets_at"))
        reset_wk = _format_reset_delta(oauth_payload.get("seven_day_resets_at"))
    else:
        limit_5h = max(1, int(os.environ.get("LOCKEDIN_HUD_5H_LIMIT", DEFAULT_5H_LIMIT)))
        limit_wk = max(1, int(os.environ.get("LOCKEDIN_HUD_WK_LIMIT", DEFAULT_WK_LIMIT)))
        now = datetime.now(timezone.utc)
        used_5h, used_wk = _count_user_turns_within(now)
        if used_5h or used_wk:
            pct_5h = min(999, round(100 * used_5h / limit_5h))
            pct_wk = min(999, round(100 * used_wk / limit_wk))
    if pct_5h is not None and pct_wk is not None:
        five_text = _ansi(f"5h:{pct_5h}%", _usage_color(pct_5h), color)
        if reset_5h:
            five_text += _ansi(f" ({reset_5h})", C_DIM, color)
        wk_text = _ansi(f"wk:{pct_wk}%", _usage_color(pct_wk), color)
        if reset_wk:
            wk_text += _ansi(f" ({reset_wk})", C_DIM, color)
        parts.append(five_text + _ansi(" · ", C_DIM, color) + wk_text)

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
