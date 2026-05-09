"""lockedin install — fallback for users who prefer not to use plugin marketplace.

The recommended install path is via Claude Code's plugin marketplace:

    /plugin marketplace add daypunk/lockedin
    /plugin install lockedin@lockedin

This module exists for users who want a manual file-copy install (or for
CI smoke tests that exercise the same artifact layout).

Source tree shape (plugin format):

    plugins/lockedin/skills/
        lockedin/                    main skill (SKILL.md, AGENTS.md, TOOLS.md)
        lockedin-render-jaso/
        lockedin-render-resume-en/

Target tree shape (Claude Code skills directory):

    <target>/                          (default: ~/.claude/skills/)
        lockedin/
        lockedin-render-jaso/
        lockedin-render-resume-en/
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path

from lockedin import __version__

MANIFEST_NAME = ".lockedin-manifest.json"

# Stable, version-independent location for the HUD script that statusLine
# points at. Kept under ~/.claude/lockedin/ so a plugin upgrade (which
# changes the cache path) doesn't break the user's statusLine config.
HUD_SCRIPT_BASENAME = "hud.py"
HUD_PREVIOUS_BACKUP = ".previous-statusline.json"


def resolve_target(target: str | None) -> Path:
    """Return the skills directory where each individual skill lives as a subdir."""
    if target:
        return Path(target).expanduser()
    config_dir = os.environ.get("CLAUDE_CONFIG_DIR")
    if config_dir:
        return Path(config_dir).expanduser() / "skills"
    return Path.home() / ".claude" / "skills"


def _skill_source() -> Path:
    """Locate the bundled skill tree (the parent of each skill subdir)."""
    here = Path(__file__).resolve()
    repo_root = here.parent.parent.parent
    candidates = [
        repo_root / "plugins" / "lockedin" / "skills",
        repo_root / "lockedin" / "skill",  # legacy fallback
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return candidates[0]


def _list_skills(src: Path) -> list[Path]:
    """Each direct subdirectory of `src` that has a SKILL.md is a skill."""
    return sorted(p for p in src.iterdir() if p.is_dir() and (p / "SKILL.md").exists())


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _build_manifest(skills_dir: Path, skill_dirs: list[Path]) -> dict:
    files: dict[str, str] = {}
    for skill in skill_dirs:
        skill_name = skill.name
        for path in sorted(skill.rglob("*")):
            if path.is_dir() or path.name == MANIFEST_NAME:
                continue
            rel = f"{skill_name}/{path.relative_to(skill).as_posix()}"
            files[rel] = _hash_file(path)
    return {"version": __version__, "files": dict(sorted(files.items()))}


def _copy_skill(src_skill: Path, dest_root: Path) -> None:
    target = dest_root / src_skill.name
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    for item in src_skill.rglob("*"):
        rel = item.relative_to(src_skill)
        out = target / rel
        if item.is_dir():
            out.mkdir(parents=True, exist_ok=True)
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, out)


def install_check(target: str | None = None) -> int:
    dest_root = resolve_target(target)
    main = dest_root / "lockedin" / "SKILL.md"
    if not main.exists():
        print(f"lockedin skill NOT installed under: {dest_root}")
        print(
            "Recommended: install via Claude Code plugin marketplace:\n"
            "  /plugin marketplace add daypunk/lockedin\n"
            "  /plugin install lockedin@lockedin\n"
            "Manual fallback:\n"
            "  lockedin install --auto-register"
        )
        return 1

    manifest_path = dest_root / "lockedin" / MANIFEST_NAME
    version = "?"
    files_count = 0
    if manifest_path.exists():
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            version = data.get("version", "?")
            files_count = len(data.get("files", {}))
        except json.JSONDecodeError:
            pass

    skills = sorted(
        p.name for p in dest_root.iterdir()
        if p.is_dir() and p.name.startswith("lockedin") and (p / "SKILL.md").exists()
    )
    print(f"lockedin installed at: {dest_root}")
    print(f"manifest version: {version}, files tracked: {files_count}")
    print(f"skills present: {', '.join(skills)}")
    return 0


def install_auto_register(target: str | None = None, *, force: bool = False) -> int:
    dest_root = resolve_target(target)
    src = _skill_source()
    if not src.exists():
        print(f"skill source not found: {src}")
        return 1
    skill_dirs = _list_skills(src)
    if not skill_dirs:
        print(f"no skills under: {src}")
        return 1

    main_skill = dest_root / "lockedin" / "SKILL.md"
    if main_skill.exists() and not force:
        print(f"already installed under {dest_root}.")
        print("use `lockedin install --upgrade` (hash-aware) or `--force` to overwrite.")
        return 1

    dest_root.mkdir(parents=True, exist_ok=True)
    for skill in skill_dirs:
        _copy_skill(skill, dest_root)

    manifest = _build_manifest(src, skill_dirs)
    (dest_root / "lockedin" / MANIFEST_NAME).write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    names = ", ".join(s.name for s in skill_dirs)
    print(f"installed lockedin v{__version__} ({len(skill_dirs)} skills: {names}) to {dest_root}.")
    return 0


def install_upgrade(target: str | None = None, *, force: bool = False) -> int:
    dest_root = resolve_target(target)
    src = _skill_source()
    if not src.exists():
        print(f"skill source not found: {src}")
        return 1
    main_skill = dest_root / "lockedin" / "SKILL.md"
    if not main_skill.exists():
        print(f"nothing installed at {dest_root} — running fresh install.")
        return install_auto_register(target, force=False)

    manifest_path = dest_root / "lockedin" / MANIFEST_NAME
    prev_files: dict[str, str] = {}
    if manifest_path.exists():
        try:
            prev_files = json.loads(manifest_path.read_text(encoding="utf-8")).get("files", {}) or {}
        except json.JSONDecodeError:
            prev_files = {}

    modified: list[str] = []
    if not force:
        for rel, prev_hash in prev_files.items():
            on_disk = dest_root / rel
            if not on_disk.exists():
                continue
            if _hash_file(on_disk) != prev_hash:
                modified.append(rel)
    if modified and not force:
        print(f"refusing to upgrade: {len(modified)} skill file(s) modified locally:")
        for m in modified:
            print(f"  - {m}")
        print("re-run with --force to overwrite, or back them up first.")
        return 1

    skill_dirs = _list_skills(src)
    for skill in skill_dirs:
        _copy_skill(skill, dest_root)
    manifest = _build_manifest(src, skill_dirs)
    (dest_root / "lockedin" / MANIFEST_NAME).write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"upgraded lockedin at {dest_root} to v{__version__}.")
    return 0


def _claude_config_dir() -> Path:
    explicit = os.environ.get("CLAUDE_CONFIG_DIR")
    if explicit:
        return Path(explicit).expanduser()
    return Path.home() / ".claude"


def _hud_install_dir() -> Path:
    return _claude_config_dir() / "lockedin"


def _settings_file() -> Path:
    return _claude_config_dir() / "settings.json"


def _read_settings() -> dict:
    f = _settings_file()
    if not f.exists():
        return {}
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _write_settings(data: dict) -> None:
    f = _settings_file()
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _hud_source_script() -> Path:
    """Locate the bundled HUD script in the plugin tree."""
    here = Path(__file__).resolve()
    repo_root = here.parent.parent.parent
    return repo_root / "plugins" / "lockedin" / "scripts" / "hud.py"


def install_setup_hud(target: str | None = None, *, force: bool = False) -> int:
    """Wire lockedin HUD into Claude Code's statusLine.

    Idempotent. Writes a self-contained HUD script to a stable location
    (``~/.claude/lockedin/hud.py``) and updates ``settings.json`` so
    Claude Code calls it. Existing non-lockedin statusLine configs are
    backed up next to the script and replaced (use ``--force`` to skip
    the user-confirmation prompt; here we treat ``force`` as "go ahead
    and overwrite").
    """
    src = _hud_source_script()
    if not src.exists():
        print(f"HUD source script not found: {src}")
        return 1

    install_dir = _hud_install_dir()
    install_dir.mkdir(parents=True, exist_ok=True)
    dest_script = install_dir / HUD_SCRIPT_BASENAME
    shutil.copy2(src, dest_script)
    dest_script.chmod(0o755)

    settings = _read_settings()
    new_command = f"python3 {dest_script}"
    new_status_line = {"type": "command", "command": new_command}

    existing = settings.get("statusLine")
    already_ours = (
        isinstance(existing, dict)
        and existing.get("type") == "command"
        and isinstance(existing.get("command"), str)
        and HUD_SCRIPT_BASENAME in existing["command"]
        and "lockedin" in existing["command"]
    )

    if existing and not already_ours and not force:
        backup_path = install_dir / HUD_PREVIOUS_BACKUP
        backup_path.write_text(
            json.dumps(existing, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(
            f"lockedin HUD: existing statusLine backed up to {backup_path}"
        )

    settings["statusLine"] = new_status_line
    _write_settings(settings)

    print(f"lockedin HUD wired into {_settings_file()}.")
    print(f"  script:    {dest_script}")
    print(f"  command:   {new_command}")
    print("Restart Claude Code to see the HUD.")
    return 0


def install_remove_hud(target: str | None = None) -> int:
    """Reverse ``install_setup_hud``: restore the previous statusLine if any,
    and remove the installed HUD script."""
    install_dir = _hud_install_dir()
    backup_path = install_dir / HUD_PREVIOUS_BACKUP
    settings = _read_settings()

    existing = settings.get("statusLine")
    is_ours = (
        isinstance(existing, dict)
        and isinstance(existing.get("command"), str)
        and HUD_SCRIPT_BASENAME in existing.get("command", "")
        and "lockedin" in existing.get("command", "")
    )

    if is_ours:
        if backup_path.exists():
            try:
                restored = json.loads(backup_path.read_text(encoding="utf-8"))
                settings["statusLine"] = restored
                print(f"lockedin HUD: restored previous statusLine from {backup_path}.")
            except json.JSONDecodeError:
                settings.pop("statusLine", None)
                print("lockedin HUD: backup unreadable; removed statusLine.")
        else:
            settings.pop("statusLine", None)
            print("lockedin HUD: removed statusLine entry.")
        _write_settings(settings)
    else:
        print("lockedin HUD: statusLine is not lockedin's; nothing to undo.")

    script_path = install_dir / HUD_SCRIPT_BASENAME
    if script_path.exists():
        script_path.unlink()
        print(f"lockedin HUD: removed {script_path}.")
    if backup_path.exists():
        backup_path.unlink()
    if install_dir.exists() and not any(install_dir.iterdir()):
        install_dir.rmdir()
    return 0


def install_uninstall(target: str | None = None) -> int:
    dest_root = resolve_target(target)
    removed: list[str] = []
    for child in dest_root.iterdir() if dest_root.exists() else []:
        if child.is_dir() and child.name.startswith("lockedin") and (child / "SKILL.md").exists():
            shutil.rmtree(child)
            removed.append(child.name)
    if not removed:
        print(f"nothing to uninstall under {dest_root}.")
        return 0
    print(f"uninstalled lockedin skills from {dest_root}: {', '.join(sorted(removed))}.")
    return 0
