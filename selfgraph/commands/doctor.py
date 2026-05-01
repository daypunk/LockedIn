"""selfgraph doctor — runtime / skill / subscription diagnostic.

Pure-CLI utility. Exits non-zero when:
  - selfgraph skill files are not installed (so the host AI can't find them)
  - ``ANTHROPIC_API_KEY`` is set but the user has not opted in via
    ``SELFGRAPH_ALLOW_API_KEY=1`` (selfgraph is designed for the
    subscription path, not direct API usage)
  - Python is older than 3.10
"""

from __future__ import annotations

import os
import sys

from selfgraph import __version__
from selfgraph.commands.install import resolve_target
from selfgraph.config import ENV_ALLOW_API_KEY, resolve_vault


def run_doctor() -> int:
    print(f"selfgraph {__version__}")
    print()

    failures = 0

    # 1. Skill install — modern layout has each skill as its own subdir
    skills_root = resolve_target(None)
    main_skill = skills_root / "selfgraph" / "SKILL.md"
    if main_skill.exists():
        print(f"  [ok]    skill installed:    {skills_root}/selfgraph/")
    else:
        failures += 1
        print(f"  [fail]  skill NOT installed: {skills_root}/selfgraph/")
        print("           → recommended: `/plugin marketplace add daypunk/selfgraph`")
        print("                          `/plugin install selfgraph@selfgraph`")
        print("           → manual fallback: `selfgraph install --auto-register`")

    # 2. Subscription mode (no API key set, or explicit opt-in)
    api_key_set = bool(os.environ.get("ANTHROPIC_API_KEY"))
    allow_api_key = os.environ.get(ENV_ALLOW_API_KEY) == "1"
    if not api_key_set:
        print("  [ok]    runtime mode:       subscription (ANTHROPIC_API_KEY not set)")
    elif allow_api_key:
        print("  [ok]    runtime mode:       api-key (explicit opt-in)")
    else:
        failures += 1
        print("  [fail]  runtime mode:       conflict — ANTHROPIC_API_KEY is set")
        print("           → selfgraph is designed for the subscription path.")
        print(f"           → to dismiss this warning set {ENV_ALLOW_API_KEY}=1")

    # 3. Vault
    vault = resolve_vault(None)
    if vault.exists():
        print(f"  [ok]    vault:              {vault}")
    else:
        # Not a failure — vault is created on first init
        print(f"  [info]  vault:              {vault} (will be created on first init)")

    # 4. Python version
    py_ver = ".".join(map(str, sys.version_info[:3]))
    print(f"  [ok]    python:             {py_ver}")

    print()
    if failures:
        print(f"{failures} check(s) failed.")
        return 1
    print("All checks passed.")
    return 0
