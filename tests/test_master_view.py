"""Tests for the master EXPERIENCE.md auto-refresh."""

from __future__ import annotations

from pathlib import Path

from lockedin.ontology import Entity
from lockedin.render.master_view import MASTER_FILENAME, refresh_master_view
from lockedin.storage.notes import write_entity


def test_refresh_returns_none_for_missing_vault(tmp_path: Path) -> None:
    target = refresh_master_view(tmp_path / "no-such")
    assert target is None


def test_refresh_writes_empty_message_for_empty_vault(tmp_path: Path) -> None:
    target = refresh_master_view(tmp_path)
    assert target is not None
    assert target.name == MASTER_FILENAME
    text = target.read_text(encoding="utf-8")
    assert "Vault is empty" in text


def test_write_entity_auto_refreshes_master_view(tmp_path: Path) -> None:
    write_entity(
        tmp_path,
        Entity(
            type="person",
            title="Jane Doe",
            slug="jane-doe",
            fields={"name": "Jane Doe", "summary": "PM and writer."},
            created="2026-01-01T00:00:00Z",
            updated="2026-01-01T00:00:00Z",
        ),
    )
    master = tmp_path / MASTER_FILENAME
    assert master.exists(), "master view should be auto-refreshed"
    text = master.read_text(encoding="utf-8")
    assert "Jane Doe" in text
    assert "## Person" in text
    assert "PM and writer." in text


def test_master_view_groups_by_type_and_orders_preferred(tmp_path: Path) -> None:
    # Mix types deliberately out of preferred order.
    for ent in (
        Entity(
            type="skill",
            title="Discovery",
            slug="discovery",
            fields={"name": "Discovery"},
            created="2026-01-01T00:00:00Z",
            updated="2026-01-01T00:00:00Z",
        ),
        Entity(
            type="person",
            title="A",
            slug="a",
            fields={"name": "A"},
            created="2026-01-01T00:00:00Z",
            updated="2026-01-01T00:00:00Z",
        ),
        Entity(
            type="project",
            title="X",
            slug="x",
            fields={"name": "X"},
            created="2026-01-01T00:00:00Z",
            updated="2026-01-01T00:00:00Z",
        ),
    ):
        write_entity(tmp_path, ent)

    master = (tmp_path / MASTER_FILENAME).read_text(encoding="utf-8")
    person_idx = master.index("## Person")
    project_idx = master.index("## Project")
    skill_idx = master.index("## Skill")
    # Preferred order: person < project < skill.
    assert person_idx < project_idx < skill_idx


def test_master_view_excludes_outputs_and_templates(tmp_path: Path) -> None:
    write_entity(
        tmp_path,
        Entity(
            type="person",
            title="Real",
            slug="real",
            fields={"name": "Real"},
            created="2026-01-01T00:00:00Z",
            updated="2026-01-01T00:00:00Z",
        ),
    )
    # Drop a stray markdown file under outputs/. It must not appear in
    # the master view.
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    (outputs / "stray.md").write_text(
        "---\ntype: person\ntitle: Stray\nslug: stray\n---\n",
        encoding="utf-8",
    )
    master = refresh_master_view(tmp_path)
    text = master.read_text(encoding="utf-8")
    assert "Real" in text
    assert "Stray" not in text
