"""Tests for the lockedin hud statusLine command."""

from __future__ import annotations

from pathlib import Path

from lockedin.commands.hud import hud
from lockedin.ontology import Entity
from lockedin.storage.notes import write_entity


def _isolated_env(monkeypatch, claude_dir: Path) -> None:
    """Point Claude usage detection at an empty config dir so usage stays 0."""
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(claude_dir))
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.delenv("LOCKEDIN_HUD_COLOR", raising=False)
    monkeypatch.delenv("LOCKEDIN_HUD_5H_LIMIT", raising=False)
    monkeypatch.delenv("LOCKEDIN_HUD_WK_LIMIT", raising=False)


def test_hud_no_vault_emits_service_label(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("LOCKEDIN_VAULT", str(tmp_path / "no-such-vault"))
    _isolated_env(monkeypatch, tmp_path / "claude")
    rc = hud(["--no-color"])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert out.startswith("LockedIn")
    assert "1.1.0" in out  # version surfaces


def test_hud_empty_vault_says_empty(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("LOCKEDIN_VAULT", str(tmp_path))
    _isolated_env(monkeypatch, tmp_path / "claude")
    rc = hud(["--no-color"])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert "experience empty" in out


def test_hud_reports_node_and_edge_counts(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("LOCKEDIN_VAULT", str(tmp_path))
    _isolated_env(monkeypatch, tmp_path / "claude")
    write_entity(
        tmp_path,
        Entity(
            type="person",
            title="A",
            slug="a",
            fields={"name": "A"},
            links=[{"predicate": "works_on", "object": "p"}],
            created="2026-04-30T10:00:00Z",
            updated="2026-04-30T10:00:00Z",
        ),
    )
    write_entity(
        tmp_path,
        Entity(
            type="project",
            title="P",
            slug="p",
            fields={"name": "P"},
            created="2026-04-30T10:00:00Z",
            updated="2026-04-30T10:00:00Z",
        ),
    )
    rc = hud(["--no-color"])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert "LockedIn 1.1.0" in out
    assert "2n" in out
    assert "1e" in out
    assert "dangling" not in out


def test_hud_flags_dangling_references(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("LOCKEDIN_VAULT", str(tmp_path))
    _isolated_env(monkeypatch, tmp_path / "claude")
    write_entity(
        tmp_path,
        Entity(
            type="person",
            title="A",
            slug="a",
            fields={"name": "A"},
            links=[{"predicate": "works_on", "object": "missing"}],
            created="2026-04-30T10:00:00Z",
            updated="2026-04-30T10:00:00Z",
        ),
    )
    rc = hud(["--no-color"])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert "1n" in out and "1e" in out
    assert "1 dangling" in out


def test_hud_respects_no_color(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("LOCKEDIN_VAULT", str(tmp_path))
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "claude"))
    monkeypatch.setenv("NO_COLOR", "1")
    rc = hud(["--color"])  # explicit flag, but NO_COLOR wins
    assert rc == 0
    out = capsys.readouterr().out
    assert "\x1b[" not in out


def test_hud_color_by_default(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("LOCKEDIN_VAULT", str(tmp_path))
    _isolated_env(monkeypatch, tmp_path / "claude")
    rc = hud([])  # color is default-on
    assert rc == 0
    out = capsys.readouterr().out
    assert "\x1b[" in out


def test_hud_usage_section_appears_when_session_has_user_turns(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    monkeypatch.setenv("LOCKEDIN_VAULT", str(tmp_path))
    claude_dir = tmp_path / "claude"
    proj_dir = claude_dir / "projects" / "fake-proj"
    proj_dir.mkdir(parents=True)
    # Write a tiny session JSONL with 3 user turns inside the last 5h.
    import datetime as _dt
    now = _dt.datetime.now(_dt.timezone.utc)
    lines = []
    for i in range(3):
        lines.append(
            f'{{"type":"user","timestamp":"{(now - _dt.timedelta(minutes=i*30)).isoformat()}"}}'
        )
    (proj_dir / "session.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(claude_dir))
    monkeypatch.delenv("NO_COLOR", raising=False)
    rc = hud(["--no-color"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "5h:" in out and "%" in out
    assert "wk:" in out
