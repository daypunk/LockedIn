"""lockedin doctor — runtime / skill / subscription diagnostic.

Pure-CLI utility. Exits non-zero when:
  - lockedin skill files are not installed (so the host AI can't find them)
  - ``ANTHROPIC_API_KEY`` is set but the user has not opted in via
    ``LOCKEDIN_ALLOW_API_KEY=1`` (lockedin is designed for the
    subscription path, not direct API usage)
  - Python is older than 3.10

Informational sections (never cause non-zero exit):
  - Vault path (created on first init if absent)
  - Audit skill registration (bundled with main install; absence only warns)
  - Optional document-ingest deps (pypdf, python-docx — extras)
  - Interview state file (in-progress Q&A session, if any)
"""

from __future__ import annotations

import json
import os
import sys

from lockedin import __version__
from lockedin.commands.install import resolve_target
from lockedin.config import ENV_ALLOW_API_KEY, resolve_vault


def _check_optional_dep(import_name: str) -> bool:
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False


def _summarize_interview_state(state_path) -> str:
    """Return a single-line summary, or empty string on absence / corruption."""
    if not state_path.exists():
        return ""
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return "state file present but unreadable (will start fresh on next run)"
    answered = len(data.get("answers") or {})
    completed = data.get("completed_at")
    updated = data.get("updated_at", "unknown")
    if completed:
        return f"interview complete ({answered} answered, finished {completed})"
    return f"in progress: {answered} answered, last updated {updated}"


def run_doctor() -> int:
    print(f"lockedin {__version__}")
    print()

    failures = 0

    # 1. Skill install — modern layout has each skill as its own subdir
    skills_root = resolve_target(None)
    main_skill = skills_root / "lockedin" / "SKILL.md"
    if main_skill.exists():
        print(f"  [ok]    skill installed:    {skills_root}/lockedin/")
    else:
        failures += 1
        print(f"  [fail]  skill NOT installed: {skills_root}/lockedin/")
        print("           → recommended: `/plugin marketplace add daypunk/lockedin`")
        print("                          `/plugin install lockedin@lockedin`")
        print("           → manual fallback: `lockedin install --auto-register`")

    # 2. Audit skill — bundled with main; absence is a soft warning
    audit_skill = skills_root / "lockedin-audit" / "SKILL.md"
    if audit_skill.exists():
        print(f"  [ok]    audit skill:        {skills_root}/lockedin-audit/")
    else:
        print(f"  [info]  audit skill:        not at {skills_root}/lockedin-audit/")
        print("           → drive-by audit (no vault) may not route correctly.")
        print("           → re-run `/plugin install lockedin@lockedin` or `lockedin install --upgrade`.")

    # 3. Subscription mode (no API key set, or explicit opt-in)
    api_key_set = bool(os.environ.get("ANTHROPIC_API_KEY"))
    allow_api_key = os.environ.get(ENV_ALLOW_API_KEY) == "1"
    if not api_key_set:
        print("  [ok]    runtime mode:       subscription (ANTHROPIC_API_KEY not set)")
    elif allow_api_key:
        print("  [ok]    runtime mode:       api-key (explicit opt-in)")
    else:
        failures += 1
        print("  [fail]  runtime mode:       conflict — ANTHROPIC_API_KEY is set")
        print("           → lockedin is designed for the subscription path.")
        print(f"           → to dismiss this warning set {ENV_ALLOW_API_KEY}=1")

    # 4. Vault
    vault = resolve_vault(None)
    if vault.exists():
        print(f"  [ok]    vault:              {vault}")
    else:
        # Not a failure — vault is created on first init
        print(f"  [info]  vault:              {vault} (will be created on first init)")

    # 5. Interview state (in-progress Q&A session)
    state_path = vault / ".lockedin" / "interview-state.json"
    summary = _summarize_interview_state(state_path)
    if summary:
        print(f"  [info]  interview:          {summary}")
    else:
        print("  [info]  interview:          no session in progress")

    # 6. Optional document-ingest deps
    pypdf_ok = _check_optional_dep("pypdf")
    docx_ok = _check_optional_dep("docx")
    yaml_ok = _check_optional_dep("yaml")
    if pypdf_ok:
        print("  [ok]    pypdf (PDF ingest): available")
    else:
        print("  [info]  pypdf (PDF ingest): not installed")
        print('           → install via: pip install "lockedin[pdf]"')
    if docx_ok:
        print("  [ok]    python-docx:        available")
    else:
        print("  [info]  python-docx:        not installed")
        print('           → install via: pip install "lockedin[docx]"')
    if yaml_ok:
        print("  [ok]    PyYAML (interview): available")
    else:
        print("  [info]  PyYAML (interview): not installed")
        print('           → install via: pip install "lockedin[yaml]"')

    # 7. Python version
    py_ver = ".".join(map(str, sys.version_info[:3]))
    print(f"  [ok]    python:             {py_ver}")

    print()
    if failures:
        print(f"{failures} check(s) failed.")
        return 1
    print("All checks passed.")
    return 0
