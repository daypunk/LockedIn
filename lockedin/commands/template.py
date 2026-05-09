"""lockedin template list|add|remove — manage ontology templates.

Pure-CLI utility. A "template" here is just a vault sub-folder with a
domain name. Built-in templates are recognized by name; user-added ones
work the same way structurally.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from lockedin.config import resolve_vault

BUILTIN_TEMPLATES = ("career", "meeting", "project", "learning")
RESERVED_DIRS = {"outputs"}


def _list(vault: Path) -> int:
    if not vault.exists():
        print(f"vault does not exist: {vault}")
        return 1
    found = sorted(
        p.name
        for p in vault.iterdir()
        if p.is_dir() and not p.name.startswith(".") and p.name not in RESERVED_DIRS
    )
    print(f"vault: {vault}")
    if not found:
        print("(no templates yet)")
        return 0
    print("templates:")
    for t in found:
        marker = "*" if t in BUILTIN_TEMPLATES else " "
        print(f"  {marker} {t}")
    print(f"\n* = built-in ({', '.join(BUILTIN_TEMPLATES)})")
    return 0


def _add(vault: Path, name: str) -> int:
    if not name or "/" in name or name.startswith("."):
        print(f"invalid template name: {name!r}")
        return 1
    if name in RESERVED_DIRS:
        print(f"reserved name: {name!r}")
        return 1
    target = vault / name
    if target.exists():
        print(f"template already exists: {target}")
        return 1
    target.mkdir(parents=True, exist_ok=True)
    readme = target / ".README.md"
    readme.write_text(
        f"# {name} template\n\n"
        f"Notes in this folder use the `{name}` template. See "
        f"`docs/ontology-spec.md` for the entity types and predicates.\n",
        encoding="utf-8",
    )
    print(f"created template: {target}")
    return 0


def _remove(vault: Path, name: str) -> int:
    if not name or "/" in name or name.startswith("."):
        print(f"invalid template name: {name!r}")
        return 1
    target = vault / name
    if not target.exists():
        print(f"template does not exist: {target}")
        return 1
    contents = [c for c in target.iterdir() if c.name != ".README.md"]
    if contents:
        print(f"refusing to remove non-empty template: {target}")
        print(f"  contains: {[c.name for c in contents]}")
        return 1
    shutil.rmtree(target)
    print(f"removed template: {target}")
    return 0


def template(action: str, name: str | None = None, *, vault_arg: str | None = None) -> int:
    vault = resolve_vault(vault_arg)
    if action == "list":
        return _list(vault)
    if action in ("add", "remove"):
        if not name:
            print(f"lockedin template {action} <name> requires a name")
            return 1
        return (_add if action == "add" else _remove)(vault, name)
    print(f"unknown action: {action!r}")
    return 1
