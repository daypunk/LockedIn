"""Anthropic OAuth utilization reader for the LockedIn HUD.

Claude Code stores an OAuth credential bundle locally. The HUD asks
Anthropic's `api.anthropic.com/api/oauth/usage` endpoint for the same
five-hour and seven-day utilization that Claude Code itself reports.
This replaces the heuristic that counted user turns from session JSONL
files; that heuristic produced misleading percentages for users with
many sessions or long-token sessions.

Credential location per OS:

- **macOS**: macOS Keychain item ``Claude Code-credentials``. Read via
  ``security find-generic-password``. The Keychain entry stores the
  same JSON blob that Linux keeps in plain text.
- **Linux**: ``~/.claude/.credentials.json``.
- **Windows**: ``%USERPROFILE%\\.claude\\.credentials.json``.

Failure semantics: every failure path returns ``None``. The HUD then
falls back to vault-only display. The HUD must NEVER crash the
statusLine, so this module catches everything outside its own
boundary.

The OAuth endpoint and credential format are not officially documented
by Anthropic. This implementation matches what Claude Code itself
uses at the time of writing. If the endpoint moves, the HUD will
silently fall back. A new release will be needed to update the path.

Caching: a successful response is cached for 60 seconds in an
OS-appropriate cache directory to avoid hammering the API on every
HUD refresh (statusLine updates several times per second).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

_USAGE_URL = "https://api.anthropic.com/api/oauth/usage"
_KEYCHAIN_SERVICE = "Claude Code-credentials"
_CACHE_TTL_SECONDS = 60
_REQUEST_TIMEOUT_SECONDS = 5


def _claude_config_dir() -> Path:
    explicit = os.environ.get("CLAUDE_CONFIG_DIR")
    if explicit:
        return Path(explicit).expanduser()
    return Path.home() / ".claude"


def _credentials_path_filesystem() -> Path:
    return _claude_config_dir() / ".credentials.json"


def _cache_dir() -> Path:
    """OS-appropriate cache dir for the usage payload."""
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Caches" / "lockedin"
    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA")
        if local:
            return Path(local) / "lockedin" / "Cache"
        return Path.home() / "AppData" / "Local" / "lockedin" / "Cache"
    # Linux / *BSD / others
    xdg = os.environ.get("XDG_CACHE_HOME")
    if xdg:
        return Path(xdg) / "lockedin"
    return Path.home() / ".cache" / "lockedin"


def _cache_path() -> Path:
    return _cache_dir() / "usage.json"


def _read_cache() -> dict[str, Any] | None:
    """Return cached payload if fresh, else None."""
    try:
        path = _cache_path()
        if not path.exists():
            return None
        raw = json.loads(path.read_text(encoding="utf-8"))
        ts = raw.get("ts")
        payload = raw.get("payload")
        if not isinstance(ts, (int, float)) or not isinstance(payload, dict):  # noqa: UP038
            return None
        if time.time() - ts > _CACHE_TTL_SECONDS:
            return None
        return payload
    except (OSError, ValueError):
        return None


def _write_cache(payload: dict[str, Any]) -> None:
    try:
        path = _cache_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"ts": time.time(), "payload": payload}),
            encoding="utf-8",
        )
    except OSError:
        # Cache is best-effort. Silently drop write failures.
        return


def _read_credentials_keychain_macos() -> dict[str, Any] | None:
    """Read the Claude Code credentials JSON from macOS Keychain.

    Uses ``security find-generic-password -s <service> -w`` which prints
    the password (the credentials JSON blob) to stdout.
    """
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


def _read_credentials_filesystem() -> dict[str, Any] | None:
    """Read the credentials JSON from the filesystem path used on Linux
    and Windows."""
    path = _credentials_path_filesystem()
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _read_credentials() -> dict[str, Any] | None:
    """Dispatch to the OS-specific credential reader.

    macOS prefers Keychain; falls back to filesystem if the Keychain
    read fails (some installs vary). Linux and Windows go straight to
    filesystem.
    """
    if sys.platform == "darwin":
        creds = _read_credentials_keychain_macos()
        if creds is not None:
            return creds
        return _read_credentials_filesystem()
    return _read_credentials_filesystem()


def _extract_access_token(creds: dict[str, Any]) -> str | None:
    """Pull an access_token out of the credentials blob.

    The Claude Code credential JSON wraps the token under
    ``claudeAiOauth.accessToken`` (observed shape). We tolerate a few
    plausible variations.
    """
    if not isinstance(creds, dict):
        return None
    candidates: list[Any] = []
    oauth = creds.get("claudeAiOauth")
    if isinstance(oauth, dict):
        candidates.append(oauth.get("accessToken"))
    candidates.append(creds.get("access_token"))
    candidates.append(creds.get("accessToken"))
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return None


def _fetch_usage(token: str) -> dict[str, Any] | None:
    """Call the Anthropic OAuth usage endpoint. Returns parsed JSON or None."""
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
        with urllib.request.urlopen(request, timeout=_REQUEST_TIMEOUT_SECONDS) as resp:
            data = resp.read().decode("utf-8")
            return json.loads(data)
    except (urllib.error.URLError, ValueError, TimeoutError, OSError):
        return None


def _normalize_payload(raw: dict[str, Any]) -> dict[str, Any] | None:
    """Pick out the two utilization values and their reset timestamps.

    The API returns ``utilization`` as a percentage (8.0 == 8%, 1.0 == 1%).
    We coerce to a 0-1 float so the HUD's color thresholds work
    consistently. The reset timestamp comes through as an ISO-8601
    string in the ``resets_at`` field; we keep it as a string and let
    the renderer format it. If neither window is present, return None.
    """
    if not isinstance(raw, dict):
        return None

    def _pull_util(value: Any) -> float | None:
        if isinstance(value, dict):
            value = value.get("utilization")
        if isinstance(value, (int, float)):  # noqa: UP038 — Python 3.8 fallback
            return float(value) / 100
        return None

    def _pull_reset(value: Any) -> str | None:
        if isinstance(value, dict):
            r = value.get("resets_at") or value.get("reset_time")
            if isinstance(r, str) and r.strip():
                return r.strip()
        return None

    five_raw = raw.get("five_hour") if "five_hour" in raw else raw.get("fiveHour")
    seven_raw = raw.get("seven_day") if "seven_day" in raw else raw.get("sevenDay")
    five = _pull_util(five_raw)
    seven = _pull_util(seven_raw)
    if five is None and seven is None:
        return None
    return {
        "five_hour": five if five is not None else 0.0,
        "seven_day": seven if seven is not None else 0.0,
        "five_hour_resets_at": _pull_reset(five_raw),
        "seven_day_resets_at": _pull_reset(seven_raw),
    }


def get_usage() -> dict[str, Any] | None:
    """Return the parsed usage payload or ``None``.

    Shape::

        {
            "five_hour": 0.45,
            "seven_day": 0.33,
            "five_hour_resets_at": "2026-05-09T18:30:00Z",
            "seven_day_resets_at": "2026-05-13T13:59:59Z",
        }

    Reset fields are optional and may be ``None``. ``None`` for the
    whole return value means OAuth path is unavailable; the HUD then
    falls back to its vault-only display. The function never raises
    and never crashes the statusLine.
    """
    cached = _read_cache()
    if cached is not None:
        return cached

    try:
        creds = _read_credentials()
        if creds is None:
            return None
        token = _extract_access_token(creds)
        if token is None:
            return None
        raw = _fetch_usage(token)
        if raw is None:
            return None
        payload = _normalize_payload(raw)
        if payload is None:
            return None
        _write_cache(payload)
        return payload
    except Exception:  # noqa: BLE001 — HUD must NEVER crash
        return None
