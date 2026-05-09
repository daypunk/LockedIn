"""Tests for slug-to-natural-language resolution in renderer outputs."""

from __future__ import annotations

from pathlib import Path

from lockedin.ontology import Entity
from lockedin.render.resolve_slugs import resolve, resolve_file
from lockedin.storage.notes import write_entity


def _seed(vault: Path) -> None:
    write_entity(
        vault,
        Entity(
            type="role",
            title="Lead PM, Payments",
            slug="lead-pm-payments-2024",
            fields={"title": "Lead PM, Payments", "start_date": "2024-01-01"},
            created="2026-01-01T00:00:00Z",
            updated="2026-01-01T00:00:00Z",
        ),
    )
    write_entity(
        vault,
        Entity(
            type="project",
            title="Checkout Migration",
            slug="checkout-migration-2024",
            fields={"name": "Checkout Migration"},
            created="2026-01-01T00:00:00Z",
            updated="2026-01-01T00:00:00Z",
        ),
    )


def test_resolve_replaces_known_slug(tmp_path: Path) -> None:
    _seed(tmp_path)
    text = "I led [[role/lead-pm-payments-2024]] for two years."
    out = resolve(text, vault=tmp_path)
    assert "[[" not in out
    assert "Lead PM, Payments" in out


def test_resolve_leaves_unknown_slug(tmp_path: Path) -> None:
    _seed(tmp_path)
    text = "Worked on [[project/missing-slug-xyz]]."
    out = resolve(text, vault=tmp_path)
    assert "[[project/missing-slug-xyz]]" in out


def test_resolve_handles_multiple_tokens(tmp_path: Path) -> None:
    _seed(tmp_path)
    text = "[[role/lead-pm-payments-2024]] shipped [[project/checkout-migration-2024]]."
    out = resolve(text, vault=tmp_path)
    assert "Lead PM, Payments" in out
    assert "Checkout Migration" in out


def test_resolve_file_in_place(tmp_path: Path) -> None:
    _seed(tmp_path)
    target = tmp_path / "outputs" / "resume.md"
    target.parent.mkdir(parents=True)
    target.write_text("Owned [[role/lead-pm-payments-2024]].\n", encoding="utf-8")
    replaced = resolve_file(target, vault=tmp_path)
    assert replaced >= 1
    out = target.read_text(encoding="utf-8")
    assert "[[" not in out
    assert "Lead PM, Payments" in out


def test_resolve_missing_vault_returns_text_unchanged(tmp_path: Path) -> None:
    text = "Pure text [[role/x]]"
    out = resolve(text, vault=tmp_path / "no-such")
    assert out == text


def test_resolve_file_nonexistent_path_is_noop(tmp_path: Path) -> None:
    replaced = resolve_file(tmp_path / "no-such.md", vault=tmp_path)
    assert replaced == 0
