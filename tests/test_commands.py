"""Tests for the deterministic CLI commands."""

from __future__ import annotations

from pathlib import Path

from selfgraph.commands.doctor import run_doctor
from selfgraph.commands.install import (
    install_auto_register,
    install_check,
    install_remove_hud,
    install_setup_hud,
    install_uninstall,
    install_upgrade,
)
from selfgraph.commands.render_graph import run_render_graph
from selfgraph.commands.validate import validate
from selfgraph.ontology import Entity
from selfgraph.storage.notes import write_entity


def test_install_check_missing(tmp_path: Path, capsys) -> None:
    target = tmp_path / "missing"
    rc = install_check(str(target))
    assert rc == 1
    out = capsys.readouterr().out
    assert "NOT installed" in out


def test_install_register_then_check_then_uninstall(tmp_path: Path) -> None:
    target = tmp_path / "skills"
    assert install_auto_register(str(target)) == 0
    # Main skill directory now lives at <target>/selfgraph/
    assert (target / "selfgraph" / "SKILL.md").exists()
    assert (target / "selfgraph" / ".selfgraph-manifest.json").exists()
    # Sub-skills install as their own top-level directories
    assert (target / "selfgraph-render-jaso" / "SKILL.md").exists()
    assert install_check(str(target)) == 0
    # second register without --force refuses
    assert install_auto_register(str(target)) == 1
    # but with --force overwrites
    assert install_auto_register(str(target), force=True) == 0
    assert install_uninstall(str(target)) == 0
    # all selfgraph* skill subdirs gone
    assert not (target / "selfgraph").exists()
    assert not (target / "selfgraph-render-jaso").exists()


def test_install_upgrade_refuses_when_user_modified(tmp_path: Path) -> None:
    target = tmp_path / "skills"
    install_auto_register(str(target))
    # User edits the main skill file
    skill_md = target / "selfgraph" / "SKILL.md"
    skill_md.write_text(skill_md.read_text() + "\n# user edit\n", encoding="utf-8")
    rc = install_upgrade(str(target))
    assert rc == 1
    # but --force succeeds
    rc2 = install_upgrade(str(target), force=True)
    assert rc2 == 0


def test_doctor_runs(monkeypatch, tmp_path: Path, capsys) -> None:
    # Steer skill check at a known empty path so it reports missing
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "claude"))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("SELFGRAPH_ALLOW_API_KEY", raising=False)
    rc = run_doctor()
    out = capsys.readouterr().out
    assert "selfgraph" in out
    assert rc == 1  # skill not installed at the steered location


def test_doctor_warns_on_api_key_without_optin(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "claude"))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake")
    monkeypatch.delenv("SELFGRAPH_ALLOW_API_KEY", raising=False)
    rc = run_doctor()
    out = capsys.readouterr().out
    assert rc == 1
    assert "ANTHROPIC_API_KEY is set" in out


def test_validate_passes_on_clean_vault(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("SELFGRAPH_VAULT", str(tmp_path))
    person = Entity(
        type="person",
        title="Sample",
        slug="sample",
        fields={"name": "Sample"},
        links=[{"predicate": "works_on", "object": "project-a", "weight": 1.0}],
        created="2026-04-30T10:00:00Z",
        updated="2026-04-30T10:00:00Z",
    )
    project = Entity(
        type="project",
        title="Project A",
        slug="project-a",
        fields={"name": "Project A"},
        created="2026-04-30T10:00:00Z",
        updated="2026-04-30T10:00:00Z",
    )
    write_entity(tmp_path, person)
    write_entity(tmp_path, project)
    rc = validate(None)
    assert rc == 0
    assert "OK" in capsys.readouterr().out


def test_validate_catches_missing_required_field(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("SELFGRAPH_VAULT", str(tmp_path))
    # Person without 'name' (required)
    person = Entity(
        type="person",
        title="Sample",
        slug="sample",
        fields={"current_role": "PM"},
        created="2026-04-30T10:00:00Z",
        updated="2026-04-30T10:00:00Z",
    )
    write_entity(tmp_path, person)
    rc = validate(None)
    assert rc == 1
    assert "required field 'name'" in capsys.readouterr().out


def test_validate_catches_edge_domain_violation(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("SELFGRAPH_VAULT", str(tmp_path))
    # company --works_on--> project: works_on requires source=person
    bad = Entity(
        type="company",
        title="Bad Co.",
        slug="bad-co",
        fields={"name": "Bad Co."},
        links=[{"predicate": "works_on", "object": "p", "weight": 1.0}],
        created="2026-04-30T10:00:00Z",
        updated="2026-04-30T10:00:00Z",
    )
    project = Entity(
        type="project",
        title="P",
        slug="p",
        fields={"name": "P"},
        created="2026-04-30T10:00:00Z",
        updated="2026-04-30T10:00:00Z",
    )
    write_entity(tmp_path, bad)
    write_entity(tmp_path, project)
    rc = validate(None)
    assert rc == 1
    assert "not allowed from source type" in capsys.readouterr().out


def test_validate_catches_edge_range_violation(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("SELFGRAPH_VAULT", str(tmp_path))
    # person --works_on--> company: works_on requires target=project
    person = Entity(
        type="person",
        title="P",
        slug="p",
        fields={"name": "P"},
        links=[{"predicate": "works_on", "object": "c", "weight": 1.0}],
        created="2026-04-30T10:00:00Z",
        updated="2026-04-30T10:00:00Z",
    )
    company = Entity(
        type="company",
        title="C",
        slug="c",
        fields={"name": "C"},
        created="2026-04-30T10:00:00Z",
        updated="2026-04-30T10:00:00Z",
    )
    write_entity(tmp_path, person)
    write_entity(tmp_path, company)
    rc = validate(None)
    assert rc == 1
    assert "not in allowed range" in capsys.readouterr().out


def test_validate_catches_dangling_reference(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("SELFGRAPH_VAULT", str(tmp_path))
    person = Entity(
        type="person",
        title="Sample",
        slug="sample",
        links=[{"predicate": "works_on", "object": "missing-project", "weight": 1.0}],
        created="2026-04-30T10:00:00Z",
        updated="2026-04-30T10:00:00Z",
    )
    write_entity(tmp_path, person)
    rc = validate(None)
    assert rc == 1
    out = capsys.readouterr().out
    assert "dangling reference" in out


def test_render_graph_emits_json_and_html(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("SELFGRAPH_VAULT", str(tmp_path))
    write_entity(
        tmp_path,
        Entity(
            type="person",
            title="Sample",
            slug="sample",
            created="2026-04-30T10:00:00Z",
            updated="2026-04-30T10:00:00Z",
        ),
    )
    rc = run_render_graph(None)
    assert rc == 0
    json_path = tmp_path / "outputs" / "graph.json"
    html_path = tmp_path / "outputs" / "graph.html"
    assert json_path.exists()
    assert html_path.exists()
    html = html_path.read_text(encoding="utf-8")
    assert "<!doctype html>" in html
    assert "sample" in html
    # Force-graph bundle is embedded inline (interactive HTML).
    assert "ForceGraph" in html
    # Bundle is real (not the placeholder fallback).
    assert "force-graph" in html
    # Total size stays under the AC ceiling (600 KB).
    assert html_path.stat().st_size < 600_000


def test_render_graph_html_handles_empty_vault_gracefully(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("SELFGRAPH_VAULT", str(tmp_path))
    rc = run_render_graph(None)
    assert rc == 0
    html = (tmp_path / "outputs" / "graph.html").read_text(encoding="utf-8")
    # Empty vault renders a friendly notice, not the force-graph init script.
    assert "vault is empty" in html
    # The bundle still ships (so the page loads cleanly).
    assert "ForceGraph" in html


def test_render_graph_fails_when_vault_missing(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("SELFGRAPH_VAULT", str(tmp_path / "no-such"))
    rc = run_render_graph(None)
    assert rc == 1
    assert "does not exist" in capsys.readouterr().out


# ----- install --setup-hud / --remove-hud ----------------------------------


def _read_settings(claude_dir: Path) -> dict:
    f = claude_dir / "settings.json"
    if not f.exists():
        return {}
    import json
    return json.loads(f.read_text(encoding="utf-8"))


def test_setup_hud_wires_statusline_when_absent(tmp_path: Path, monkeypatch, capsys) -> None:
    claude_dir = tmp_path / "claude"
    claude_dir.mkdir()
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(claude_dir))

    rc = install_setup_hud()
    assert rc == 0

    # Script installed at stable path
    assert (claude_dir / "selfgraph" / "hud.py").exists()
    # settings.json populated
    settings = _read_settings(claude_dir)
    sl = settings.get("statusLine")
    assert isinstance(sl, dict)
    assert sl.get("type") == "command"
    assert "hud.py" in sl.get("command", "")
    assert "selfgraph" in sl.get("command", "")
    # User-friendly output
    assert "selfgraph HUD wired" in capsys.readouterr().out


def test_setup_hud_backs_up_existing_statusline(tmp_path: Path, monkeypatch) -> None:
    claude_dir = tmp_path / "claude"
    claude_dir.mkdir()
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(claude_dir))

    # Pre-existing statusLine from some other tool
    pre = {"statusLine": {"type": "command", "command": "node /path/to/other-hud.mjs"}}
    (claude_dir / "settings.json").write_text(
        '{\n  "statusLine": {"type": "command", "command": "node /path/to/other-hud.mjs"}\n}\n',
        encoding="utf-8",
    )

    rc = install_setup_hud()
    assert rc == 0

    backup = claude_dir / "selfgraph" / ".previous-statusline.json"
    assert backup.exists()
    import json
    restored = json.loads(backup.read_text(encoding="utf-8"))
    assert restored == pre["statusLine"]

    settings = _read_settings(claude_dir)
    assert "selfgraph" in settings["statusLine"]["command"]


def test_remove_hud_restores_previous_statusline(tmp_path: Path, monkeypatch) -> None:
    claude_dir = tmp_path / "claude"
    claude_dir.mkdir()
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(claude_dir))

    # First, set up an existing statusLine + wire selfgraph (which backs it up)
    (claude_dir / "settings.json").write_text(
        '{\n  "statusLine": {"type": "command", "command": "echo previous"}\n}\n',
        encoding="utf-8",
    )
    install_setup_hud()
    assert "selfgraph" in _read_settings(claude_dir)["statusLine"]["command"]

    # Now remove — backup should be restored
    rc = install_remove_hud()
    assert rc == 0
    assert _read_settings(claude_dir)["statusLine"]["command"] == "echo previous"
    assert not (claude_dir / "selfgraph" / "hud.py").exists()


def test_setup_hud_idempotent(tmp_path: Path, monkeypatch) -> None:
    claude_dir = tmp_path / "claude"
    claude_dir.mkdir()
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(claude_dir))

    install_setup_hud()
    first = _read_settings(claude_dir)["statusLine"]
    install_setup_hud()  # second call must not bork the config
    second = _read_settings(claude_dir)["statusLine"]
    assert first == second


def test_remove_hud_when_not_ours(tmp_path: Path, monkeypatch, capsys) -> None:
    claude_dir = tmp_path / "claude"
    claude_dir.mkdir()
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(claude_dir))
    (claude_dir / "settings.json").write_text(
        '{\n  "statusLine": {"type": "command", "command": "node /not-ours.mjs"}\n}\n',
        encoding="utf-8",
    )
    rc = install_remove_hud()
    assert rc == 0
    out = capsys.readouterr().out
    assert "not selfgraph" in out
    # statusLine left intact
    assert _read_settings(claude_dir)["statusLine"]["command"] == "node /not-ours.mjs"
