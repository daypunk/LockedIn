"""Tests for init --fixture, template add/list/remove, ingest --dry-run."""

from __future__ import annotations

from pathlib import Path

import pytest

from lockedin.cli import main as cli_main
from lockedin.commands.ingest_dry import ingest_dry_run
from lockedin.commands.init import init_from_fixture
from lockedin.commands.template import template
from lockedin.storage.notes import read_entity

# ----- init --fixture --------------------------------------------------------


SAMPLE_FIXTURE = """\
schema_version: 1
template: experience
entities:
  - type: person
    title: Sample User
    slug: sample-user
    fields:
      current_role: PM
    links:
      - {predicate: works_on, object: project-a}
  - type: project
    title: Project A
    slug: project-a
"""


def test_init_from_fixture_writes_entities(tmp_path: Path, monkeypatch, capsys) -> None:
    pytest.importorskip("yaml")
    monkeypatch.setenv("LOCKEDIN_VAULT", str(tmp_path))
    fixture = tmp_path / "seed.yaml"
    fixture.write_text(SAMPLE_FIXTURE, encoding="utf-8")

    rc = init_from_fixture(str(fixture))
    assert rc == 0
    out = capsys.readouterr().out
    assert "wrote 2 entities" in out
    person = read_entity(tmp_path / "experience" / "person" / "sample-user.md")
    assert person.title == "Sample User"
    assert person.fields["current_role"] == "PM"
    assert person.links[0]["object"] == "project-a"
    assert (tmp_path / "experience" / "project" / "project-a.md").exists()


def test_interview_alias_dispatches_to_init(tmp_path: Path, monkeypatch, capsys) -> None:
    """The `interview` alias should route through the same dispatch as `init`."""
    pytest.importorskip("yaml")
    monkeypatch.setenv("LOCKEDIN_VAULT", str(tmp_path))
    fixture = tmp_path / "seed.yaml"
    fixture.write_text(SAMPLE_FIXTURE, encoding="utf-8")

    rc = cli_main(["interview", "--fixture", str(fixture)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "wrote 2 entities" in out
    assert (tmp_path / "experience" / "person" / "sample-user.md").exists()


def test_init_from_fixture_missing_file(tmp_path: Path, capsys) -> None:
    pytest.importorskip("yaml")
    rc = init_from_fixture(str(tmp_path / "no-such-fixture.yaml"))
    assert rc == 1
    assert "fixture not found" in capsys.readouterr().err


def test_init_from_fixture_skips_malformed_entries(tmp_path: Path, monkeypatch, capsys) -> None:
    pytest.importorskip("yaml")
    monkeypatch.setenv("LOCKEDIN_VAULT", str(tmp_path))
    fixture = tmp_path / "seed.yaml"
    fixture.write_text(
        "template: experience\n"
        "entities:\n"
        "  - type: person\n"
        "    title: OK\n"
        "    slug: ok\n"
        "  - title: Missing-type-and-slug\n",
        encoding="utf-8",
    )
    rc = init_from_fixture(str(fixture))
    assert rc == 0  # at least one entity written
    err = capsys.readouterr().err
    assert "skipped" in err
    assert (tmp_path / "experience" / "person" / "ok.md").exists()


def test_example_fixture_loads(tmp_path: Path, monkeypatch) -> None:
    """Sanity check the bundled examples/sample-vault.yaml round-trips."""
    pytest.importorskip("yaml")
    monkeypatch.setenv("LOCKEDIN_VAULT", str(tmp_path))
    repo_root = Path(__file__).resolve().parent.parent
    fixture = repo_root / "examples" / "sample-vault.yaml"
    if not fixture.exists():
        pytest.skip("examples/sample-vault.yaml not present")
    rc = init_from_fixture(str(fixture))
    assert rc == 0
    # at least the canonical entities should exist
    assert (tmp_path / "experience" / "person" / "sample-user.md").exists()
    assert (tmp_path / "experience" / "achievement" / "achievement-payments-uplift.md").exists()


# ----- template list/add/remove ----------------------------------------------


def test_template_list_on_empty_vault(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("LOCKEDIN_VAULT", str(tmp_path))
    tmp_path.mkdir(exist_ok=True)
    rc = template("list")
    assert rc == 0
    out = capsys.readouterr().out
    assert "no templates yet" in out


def test_template_add_then_list_then_remove(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("LOCKEDIN_VAULT", str(tmp_path))
    rc = template("add", "research")
    assert rc == 0
    assert (tmp_path / "research").is_dir()
    assert (tmp_path / "research" / ".README.md").exists()

    rc = template("list")
    assert rc == 0
    assert "research" in capsys.readouterr().out

    # add again should refuse
    rc = template("add", "research")
    assert rc == 1

    # remove succeeds (only .README.md inside)
    rc = template("remove", "research")
    assert rc == 0
    assert not (tmp_path / "research").exists()


def test_template_remove_refuses_non_empty(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("LOCKEDIN_VAULT", str(tmp_path))
    template("add", "ops")
    (tmp_path / "ops" / "user-note.md").write_text("hi", encoding="utf-8")
    rc = template("remove", "ops")
    assert rc == 1
    assert (tmp_path / "ops" / "user-note.md").exists()


def test_template_rejects_invalid_names(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("LOCKEDIN_VAULT", str(tmp_path))
    assert template("add", "with/slash") == 1
    assert template("add", ".dotted") == 1
    assert template("add", "outputs") == 1  # reserved


# ----- ingest --dry-run ------------------------------------------------------


def test_ingest_dry_run_reports_md_and_txt(tmp_path: Path, capsys) -> None:
    (tmp_path / "doc.md").write_text("# Title\n\nbody.", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("plain\nlines", encoding="utf-8")
    rc = ingest_dry_run(str(tmp_path))
    assert rc == 0
    out = capsys.readouterr().out
    assert "parsed: 2" in out
    assert "doc.md" in out and "notes.txt" in out
    # next-step pointer present
    assert "/lockedin ingest" in out


def test_ingest_dry_run_path_missing(tmp_path: Path, capsys) -> None:
    rc = ingest_dry_run(str(tmp_path / "no-such"))
    assert rc == 1
    assert "path not found" in capsys.readouterr().out


def test_ingest_dry_run_empty_directory(tmp_path: Path, capsys) -> None:
    rc = ingest_dry_run(str(tmp_path))
    assert rc == 0
    out = capsys.readouterr().out
    assert "no supported files" in out


def test_ingest_dry_run_single_file(tmp_path: Path, capsys) -> None:
    f = tmp_path / "single.md"
    f.write_text("hello", encoding="utf-8")
    rc = ingest_dry_run(str(f))
    assert rc == 0
    out = capsys.readouterr().out
    assert "parsed: 1" in out
