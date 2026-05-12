"""Tests for interview engine resumability (state persistence, resume, pause, skip).

All tests that exercise the interview engine must:
- Set LOCKEDIN_VAULT via monkeypatch to a tmp_path so no real vault is touched.
- Monkeypatch lockedin.ingest.interview._ask to control user input.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("yaml")

import lockedin.ingest.interview as interview_mod
from lockedin.ingest.interview import (
    _atomic_write,
    _load_state,
    _vault_path,
    run,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_minimal_config() -> dict:
    """A tiny 2-section / 3-question config for fast unit tests.

    Section 1 (identity): q_name (required), q_email (optional)
    Section 2 (work): q_company (required)
    Total: 3 questions, 2 sections
    """
    return {
        "version": 1,
        "template": "test",
        "sections": [
            {
                "name": "identity",
                "questions": [
                    {
                        "id": "q_name",
                        "text": "What is your name?",
                        "writes": {"entity": "person", "field": "name"},
                        "validate": "non_empty",
                    },
                    {
                        "id": "q_email",
                        "text": "What is your email?",
                        "writes": {"entity": "person", "field": "email"},
                        # no validate → optional
                    },
                ],
            },
            {
                "name": "work",
                "questions": [
                    {
                        "id": "q_company",
                        "text": "Where do you work?",
                        "writes": {"entity": "company", "field": "name"},
                        "validate": "non_empty",
                        "requires": ["q_name"],
                    },
                ],
            },
        ],
    }


def _patch_run(
    tmp_path: Path,
    monkeypatch,
    answers: list[str],
    config: dict | None = None,
    *,
    sections: list[str] | None = None,
    fresh: bool = False,
) -> list:
    """Run the interview with controlled input and return entities.

    Monkeypatches:
    - LOCKEDIN_VAULT to tmp_path
    - _ask to pop from answers list
    - _yaml_load / _resolve_template to use in-memory config
    """
    monkeypatch.setenv("LOCKEDIN_VAULT", str(tmp_path))

    if config is None:
        config = _make_minimal_config()

    answer_iter = iter(answers)

    def fake_ask(prompt: str) -> str:
        try:
            return next(answer_iter)
        except StopIteration:
            return "[pause]"

    monkeypatch.setattr(interview_mod, "_ask", fake_ask)
    monkeypatch.setattr(interview_mod, "_yaml_load", lambda _path: config)
    monkeypatch.setattr(
        interview_mod,
        "_resolve_template",
        lambda _template: Path("/fake/questions.yaml"),
    )

    kwargs: dict = {}
    if sections is not None:
        kwargs["sections"] = sections

    return run("test", lang="en", fresh=fresh, **kwargs)


# ---------------------------------------------------------------------------
# 1. Fresh run — no existing state file
# ---------------------------------------------------------------------------


class TestFreshRun:
    def test_state_file_created(self, tmp_path: Path, monkeypatch) -> None:
        _patch_run(tmp_path, monkeypatch, ["Alice", "alice@example.com", "Acme"])
        state_file = tmp_path / ".lockedin" / "interview-state.json"
        assert state_file.exists()

    def test_answers_in_state_file(self, tmp_path: Path, monkeypatch) -> None:
        _patch_run(tmp_path, monkeypatch, ["Alice", "alice@example.com", "Acme"])
        state_file = tmp_path / ".lockedin" / "interview-state.json"
        state = json.loads(state_file.read_text())
        assert state["answers"]["q_name"] == "Alice"
        assert state["answers"]["q_email"] == "alice@example.com"
        assert state["answers"]["q_company"] == "Acme"

    def test_completed_at_set(self, tmp_path: Path, monkeypatch) -> None:
        _patch_run(tmp_path, monkeypatch, ["Alice", "alice@example.com", "Acme"])
        state = json.loads(
            (tmp_path / ".lockedin" / "interview-state.json").read_text()
        )
        assert state["completed_at"] is not None

    def test_entities_returned(self, tmp_path: Path, monkeypatch) -> None:
        entities = _patch_run(
            tmp_path, monkeypatch, ["Alice", "alice@example.com", "Acme"]
        )
        types = {e.type for e in entities}
        assert "person" in types
        assert "company" in types

    def test_provenance_interview(self, tmp_path: Path, monkeypatch) -> None:
        entities = _patch_run(
            tmp_path, monkeypatch, ["Alice", "alice@example.com", "Acme"]
        )
        for ent in entities:
            assert ent.fields.get("provenance") == "interview"

    def test_state_schema_version(self, tmp_path: Path, monkeypatch) -> None:
        _patch_run(tmp_path, monkeypatch, ["Alice", "alice@example.com", "Acme"])
        state = json.loads(
            (tmp_path / ".lockedin" / "interview-state.json").read_text()
        )
        assert state["schema_version"] == 1
        assert state["template"] == "test"
        assert state["lang"] == "en"


# ---------------------------------------------------------------------------
# 2. Pause via [pause] keyword — mid-interview
# ---------------------------------------------------------------------------


class TestPause:
    def test_pause_returns_partial_entities(self, tmp_path: Path, monkeypatch) -> None:
        # Answer q_name then pause instead of email
        entities = _patch_run(tmp_path, monkeypatch, ["Alice", "[pause]"])
        types = {e.type for e in entities}
        assert "person" in types

    def test_pause_state_file_persists(self, tmp_path: Path, monkeypatch) -> None:
        _patch_run(tmp_path, monkeypatch, ["Alice", "[pause]"])
        state = json.loads(
            (tmp_path / ".lockedin" / "interview-state.json").read_text()
        )
        assert state["answers"]["q_name"] == "Alice"
        # q_email and q_company not yet answered
        assert "q_email" not in state["answers"]
        assert "q_company" not in state["answers"]

    def test_pause_completed_at_null(self, tmp_path: Path, monkeypatch) -> None:
        _patch_run(tmp_path, monkeypatch, ["Alice", "[pause]"])
        state = json.loads(
            (tmp_path / ".lockedin" / "interview-state.json").read_text()
        )
        assert state["completed_at"] is None

    @pytest.mark.parametrize("keyword", ["[pause]", "[stop]", "[exit]", ":pause", ":q"])
    def test_all_pause_keywords(
        self, keyword: str, tmp_path: Path, monkeypatch
    ) -> None:
        _patch_run(tmp_path, monkeypatch, ["Alice", keyword])
        state = json.loads(
            (tmp_path / ".lockedin" / "interview-state.json").read_text()
        )
        assert "q_name" in state["answers"]
        assert state["completed_at"] is None

    def test_pause_message_printed(
        self, tmp_path: Path, monkeypatch, capsys
    ) -> None:
        _patch_run(tmp_path, monkeypatch, ["Alice", "[pause]"])
        out = capsys.readouterr().out
        assert "Paused" in out


# ---------------------------------------------------------------------------
# 3. Resume — second call skips answered questions
# ---------------------------------------------------------------------------


class TestResume:
    def test_resume_skips_answered(self, tmp_path: Path, monkeypatch) -> None:
        # First run: answer q_name then pause
        _patch_run(tmp_path, monkeypatch, ["Alice", "[pause]"])
        state_before = json.loads(
            (tmp_path / ".lockedin" / "interview-state.json").read_text()
        )
        assert "q_name" in state_before["answers"]
        assert "q_company" not in state_before["answers"]

        # Second run: should not re-ask q_name, should ask q_email then q_company
        _patch_run(
            tmp_path, monkeypatch, ["alice@example.com", "Acme Corp"]
        )
        state_after = json.loads(
            (tmp_path / ".lockedin" / "interview-state.json").read_text()
        )
        # q_name still Alice (not overwritten)
        assert state_after["answers"]["q_name"] == "Alice"
        assert state_after["answers"]["q_email"] == "alice@example.com"
        assert state_after["answers"]["q_company"] == "Acme Corp"

    def test_resume_prints_notice(
        self, tmp_path: Path, monkeypatch, capsys
    ) -> None:
        # Seed state file directly
        state_dir = tmp_path / ".lockedin"
        state_dir.mkdir(parents=True)
        state_file = state_dir / "interview-state.json"
        state_file.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "template": "test",
                    "lang": "en",
                    "started_at": "2026-01-01T00:00:00Z",
                    "updated_at": "2026-01-01T00:00:00Z",
                    "answers": {"q_name": "Bob"},
                    "completed_at": None,
                }
            ),
            encoding="utf-8",
        )

        _patch_run(tmp_path, monkeypatch, ["bob@example.com", "Globex"])
        out = capsys.readouterr().out
        assert "Resuming interview" in out

    def test_resume_entities_include_prior(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        # Seed state with q_name already answered
        state_dir = tmp_path / ".lockedin"
        state_dir.mkdir(parents=True)
        (state_dir / "interview-state.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "template": "test",
                    "lang": "en",
                    "started_at": "2026-01-01T00:00:00Z",
                    "updated_at": "2026-01-01T00:00:00Z",
                    "answers": {"q_name": "Carol"},
                    "completed_at": None,
                }
            ),
            encoding="utf-8",
        )
        entities = _patch_run(
            tmp_path, monkeypatch, ["carol@example.com", "Initech"]
        )
        person_entities = [e for e in entities if e.type == "person"]
        assert person_entities
        person = person_entities[0]
        assert person.fields.get("name") == "Carol"


# ---------------------------------------------------------------------------
# 4. Skip optional question
# ---------------------------------------------------------------------------


class TestSkipOptional:
    @pytest.mark.parametrize("keyword", ["[skip]", ":skip"])
    def test_skip_optional_continues(
        self, keyword: str, tmp_path: Path, monkeypatch
    ) -> None:
        # q_email is optional, q_company is required
        _patch_run(
            tmp_path, monkeypatch, ["Alice", keyword, "Acme"]
        )
        state = json.loads(
            (tmp_path / ".lockedin" / "interview-state.json").read_text()
        )
        # q_email recorded as empty (skipped), q_company answered
        assert state["answers"].get("q_email") == ""
        assert state["answers"].get("q_company") == "Acme"
        # Interview still reaches completion
        assert state["completed_at"] is not None

    def test_skip_optional_entity_has_no_field(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        entities = _patch_run(tmp_path, monkeypatch, ["Alice", "[skip]", "Acme"])
        entities = _patch_run(tmp_path, monkeypatch, [])
        # After full completion the person entity shouldn't have email set
        # (it's either absent or empty from the skip)
        person = next((e for e in entities if e.type == "person"), None)
        if person:
            assert person.fields.get("email", "") == "" or "email" not in person.fields


# ---------------------------------------------------------------------------
# 5. Skip rejected on required question
# ---------------------------------------------------------------------------


class TestSkipRequired:
    def test_skip_required_rejected_message(
        self, tmp_path: Path, monkeypatch, capsys
    ) -> None:
        # q_name is required (non_empty). Attempt to skip → should print message
        # then ask again; second time provide valid answer
        _patch_run(tmp_path, monkeypatch, ["[skip]", "Alice", "alice@x.com", "Acme"])
        out = capsys.readouterr().out
        assert "required" in out.lower()

    def test_skip_required_then_answer(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        # Skip attempt then real answer
        entities = _patch_run(
            tmp_path, monkeypatch, ["[skip]", "Alice", "alice@x.com", "Acme"]
        )
        person = next((e for e in entities if e.type == "person"), None)
        assert person is not None
        assert person.fields.get("name") == "Alice"


# ---------------------------------------------------------------------------
# 6. Corrupt state file — warning, fresh start
# ---------------------------------------------------------------------------


class TestCorruptState:
    def test_corrupt_json_prints_warning(
        self, tmp_path: Path, monkeypatch, capsys
    ) -> None:
        state_dir = tmp_path / ".lockedin"
        state_dir.mkdir(parents=True)
        (state_dir / "interview-state.json").write_text(
            "{{ not valid json !!!", encoding="utf-8"
        )
        _patch_run(tmp_path, monkeypatch, ["Alice", "a@b.com", "Acme"])
        err = capsys.readouterr().err
        assert "corrupt" in err.lower() or "warning" in err.lower() or "fresh" in err.lower()

    def test_corrupt_json_still_completes(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        state_dir = tmp_path / ".lockedin"
        state_dir.mkdir(parents=True)
        (state_dir / "interview-state.json").write_text("{bad}", encoding="utf-8")
        entities = _patch_run(tmp_path, monkeypatch, ["Alice", "a@b.com", "Acme"])
        assert any(e.type == "person" for e in entities)


# ---------------------------------------------------------------------------
# 7. Completion — completed_at set
# ---------------------------------------------------------------------------


class TestCompletion:
    def test_completed_at_is_iso_string(self, tmp_path: Path, monkeypatch) -> None:
        _patch_run(tmp_path, monkeypatch, ["Alice", "alice@x.com", "Acme"])
        state = json.loads(
            (tmp_path / ".lockedin" / "interview-state.json").read_text()
        )
        assert state["completed_at"] is not None
        # Must look like an ISO timestamp
        assert "T" in state["completed_at"]
        assert "Z" in state["completed_at"] or "+" in state["completed_at"]

    def test_completed_interview_prompts_restart(
        self, tmp_path: Path, monkeypatch, capsys
    ) -> None:
        # Seed a completed state file
        state_dir = tmp_path / ".lockedin"
        state_dir.mkdir(parents=True)
        (state_dir / "interview-state.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "template": "test",
                    "lang": "en",
                    "started_at": "2026-01-01T00:00:00Z",
                    "updated_at": "2026-01-01T01:00:00Z",
                    "answers": {"q_name": "Done User"},
                    "completed_at": "2026-01-01T01:00:00Z",
                }
            ),
            encoding="utf-8",
        )
        # Decline to restart
        _patch_run(tmp_path, monkeypatch, ["N"])
        out = capsys.readouterr().out
        assert "complete" in out.lower() or "start over" in out.lower()

    def test_completed_interview_decline_returns_empty(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        state_dir = tmp_path / ".lockedin"
        state_dir.mkdir(parents=True)
        (state_dir / "interview-state.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "template": "test",
                    "lang": "en",
                    "started_at": "2026-01-01T00:00:00Z",
                    "updated_at": "2026-01-01T01:00:00Z",
                    "answers": {},
                    "completed_at": "2026-01-01T01:00:00Z",
                }
            ),
            encoding="utf-8",
        )
        entities = _patch_run(tmp_path, monkeypatch, ["n"])
        assert entities == []


# ---------------------------------------------------------------------------
# 8. fresh=True — forces restart
# ---------------------------------------------------------------------------


class TestFreshKwarg:
    def test_fresh_deletes_existing_state(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        # Create a state file with prior answer
        state_dir = tmp_path / ".lockedin"
        state_dir.mkdir(parents=True)
        state_file = state_dir / "interview-state.json"
        state_file.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "template": "test",
                    "lang": "en",
                    "started_at": "2026-01-01T00:00:00Z",
                    "updated_at": "2026-01-01T00:00:00Z",
                    "answers": {"q_name": "OldName"},
                    "completed_at": None,
                }
            ),
            encoding="utf-8",
        )
        # Run with fresh=True; first question re-asked
        _patch_run(tmp_path, monkeypatch, ["NewName", "new@x.com", "Corp"], fresh=True)
        state = json.loads(state_file.read_text())
        assert state["answers"]["q_name"] == "NewName"

    def test_fresh_does_not_print_resume_notice(
        self, tmp_path: Path, monkeypatch, capsys
    ) -> None:
        state_dir = tmp_path / ".lockedin"
        state_dir.mkdir(parents=True)
        (state_dir / "interview-state.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "template": "test",
                    "lang": "en",
                    "started_at": "2026-01-01T00:00:00Z",
                    "updated_at": "2026-01-01T00:00:00Z",
                    "answers": {"q_name": "OldName"},
                    "completed_at": None,
                }
            ),
            encoding="utf-8",
        )
        _patch_run(tmp_path, monkeypatch, ["NewName", "new@x.com", "Corp"], fresh=True)
        out = capsys.readouterr().out
        assert "Resuming" not in out


# ---------------------------------------------------------------------------
# 9. sections=[...] kwarg — only named sections asked
# ---------------------------------------------------------------------------


class TestSectionsFilter:
    def test_only_identity_section(self, tmp_path: Path, monkeypatch) -> None:
        # Only ask identity section; work section has q_company requiring q_name
        _patch_run(
            tmp_path,
            monkeypatch,
            ["Alice", "alice@x.com"],
            sections=["identity"],
        )
        state = json.loads(
            (tmp_path / ".lockedin" / "interview-state.json").read_text()
        )
        # q_name and q_email answered
        assert "q_name" in state["answers"]
        # q_company NOT asked (not in identity section)
        assert "q_company" not in state["answers"]

    def test_only_work_section_without_prereqs(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        # q_company requires q_name which won't be answered → should be skipped
        _patch_run(
            tmp_path,
            monkeypatch,
            [],
            sections=["work"],
        )
        state = json.loads(
            (tmp_path / ".lockedin" / "interview-state.json").read_text()
        )
        # q_company skipped because q_name prerequisite not met
        assert "q_company" not in state["answers"]

    def test_two_sections_filter(self, tmp_path: Path, monkeypatch) -> None:
        # Ask both sections
        _patch_run(
            tmp_path,
            monkeypatch,
            ["Alice", "alice@x.com", "Globex"],
            sections=["identity", "work"],
        )
        state = json.loads(
            (tmp_path / ".lockedin" / "interview-state.json").read_text()
        )
        assert "q_name" in state["answers"]
        assert "q_company" in state["answers"]

    def test_sections_filter_preserves_state_for_other_sections(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        # Seed state with q_company already answered
        state_dir = tmp_path / ".lockedin"
        state_dir.mkdir(parents=True)
        (state_dir / "interview-state.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "template": "test",
                    "lang": "en",
                    "started_at": "2026-01-01T00:00:00Z",
                    "updated_at": "2026-01-01T00:00:00Z",
                    "answers": {"q_company": "PriorCorp"},
                    "completed_at": None,
                }
            ),
            encoding="utf-8",
        )
        # Run only identity section
        _patch_run(
            tmp_path, monkeypatch, ["Alice", "alice@x.com"], sections=["identity"]
        )
        state = json.loads(
            (tmp_path / ".lockedin" / "interview-state.json").read_text()
        )
        # q_company from prior state should still be present
        assert state["answers"].get("q_company") == "PriorCorp"
        assert state["answers"].get("q_name") == "Alice"


# ---------------------------------------------------------------------------
# 10. Atomic write — tmp file then rename
# ---------------------------------------------------------------------------


class TestAtomicWrite:
    def test_atomic_write_renames_tmp(self, tmp_path: Path) -> None:
        target = tmp_path / "state.json"
        data = {"hello": "world"}
        _atomic_write(target, data)
        assert target.exists()
        assert not target.with_suffix(".json.tmp").exists()
        assert json.loads(target.read_text()) == data

    def test_atomic_write_no_partial_on_success(self, tmp_path: Path) -> None:
        target = tmp_path / "state.json"
        _atomic_write(target, {"key": "value"})
        # Tmp file must not exist after successful write
        tmp_file = target.with_suffix(".json.tmp")
        assert not tmp_file.exists()

    def test_atomic_write_overwrites_existing(self, tmp_path: Path) -> None:
        target = tmp_path / "state.json"
        _atomic_write(target, {"v": 1})
        _atomic_write(target, {"v": 2})
        assert json.loads(target.read_text())["v"] == 2


# ---------------------------------------------------------------------------
# 11. LOCKEDIN_VAULT env var honored
# ---------------------------------------------------------------------------


class TestVaultEnvVar:
    def test_vault_env_var_used(self, tmp_path: Path, monkeypatch) -> None:
        custom_vault = tmp_path / "my_vault"
        custom_vault.mkdir()
        monkeypatch.setenv("LOCKEDIN_VAULT", str(custom_vault))

        result = _vault_path()
        assert result == custom_vault.resolve()

    def test_state_file_in_custom_vault(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        custom_vault = tmp_path / "custom_vault"
        custom_vault.mkdir()
        _patch_run(
            custom_vault, monkeypatch, ["Alice", "a@b.com", "Corp"]
        )
        state_file = custom_vault / ".lockedin" / "interview-state.json"
        assert state_file.exists()

    def test_default_vault_without_env_var(self, monkeypatch) -> None:
        monkeypatch.delenv("LOCKEDIN_VAULT", raising=False)
        result = _vault_path()
        assert "LockedIn" in str(result) or "Documents" in str(result)


# ---------------------------------------------------------------------------
# 12. Progress display
# ---------------------------------------------------------------------------


class TestProgressDisplay:
    def test_progress_banner_printed(
        self, tmp_path: Path, monkeypatch, capsys
    ) -> None:
        _patch_run(tmp_path, monkeypatch, ["Alice", "[pause]"])
        out = capsys.readouterr().out
        # Should contain section/total format
        assert "Section" in out and "/" in out

    def test_progress_shows_question_number(
        self, tmp_path: Path, monkeypatch, capsys
    ) -> None:
        _patch_run(tmp_path, monkeypatch, ["Alice", "[pause]"])
        out = capsys.readouterr().out
        assert "Q " in out or "Q1" in out or "· Q" in out


# ---------------------------------------------------------------------------
# 13. Load-state helper unit tests
# ---------------------------------------------------------------------------


class TestLoadState:
    def test_returns_none_when_absent(self, tmp_path: Path) -> None:
        result = _load_state(tmp_path / "no-such.json")
        assert result is None

    def test_returns_dict_on_valid_json(self, tmp_path: Path) -> None:
        f = tmp_path / "state.json"
        f.write_text(json.dumps({"key": "val"}), encoding="utf-8")
        result = _load_state(f)
        assert result == {"key": "val"}

    def test_returns_empty_dict_on_corrupt_json(
        self, tmp_path: Path, capsys
    ) -> None:
        f = tmp_path / "state.json"
        f.write_text("{ corrupt }", encoding="utf-8")
        result = _load_state(f)
        assert result == {}

    def test_corrupt_json_prints_to_stderr(
        self, tmp_path: Path, capsys
    ) -> None:
        f = tmp_path / "state.json"
        f.write_text("not json", encoding="utf-8")
        _load_state(f)
        err = capsys.readouterr().err
        assert err.strip() != ""


# ---------------------------------------------------------------------------
# 14. Backward compat — existing callers keep working
# ---------------------------------------------------------------------------


class TestBackwardCompat:
    def test_non_interactive_still_raises(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.setenv("LOCKEDIN_VAULT", str(tmp_path))
        with pytest.raises(NotImplementedError):
            run("experience", non_interactive=True)

    def test_positional_args_still_work(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        # run(template, non_interactive, lang) signature preserved
        monkeypatch.setenv("LOCKEDIN_VAULT", str(tmp_path))
        monkeypatch.setattr(interview_mod, "_ask", lambda p: "[pause]")
        monkeypatch.setattr(interview_mod, "_yaml_load", lambda _: _make_minimal_config())
        monkeypatch.setattr(
            interview_mod, "_resolve_template", lambda _: Path("/fake/q.yaml")
        )
        # Should not raise
        result = run("test", False, "en")
        assert isinstance(result, list)
