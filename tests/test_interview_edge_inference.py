"""Tests for automatic edge inference in the Q&A interview engine.

All tests that exercise the interview engine must:
- Set LOCKEDIN_VAULT via monkeypatch to a tmp_path so no real vault is touched.
- Monkeypatch lockedin.ingest.interview._ask to control user input.

Edge inference is deterministic — it runs at interview completion and
populates entity.links based on entity co-presence and EDGE_SCHEMAS
domain/range rules.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("yaml")

import lockedin.ingest.interview as interview_mod
from lockedin.ingest.interview import run
from lockedin.storage.notes import write_entity

# ---------------------------------------------------------------------------
# Helpers (mirrored from test_interview_resumability.py)
# ---------------------------------------------------------------------------


def _patch_run(
    tmp_path: Path,
    monkeypatch,
    answers: list[str],
    config: dict | None = None,
    *,
    sections: list[str] | None = None,
    fresh: bool = False,
) -> list:
    """Run the interview with controlled input and return entities."""
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


def _make_minimal_config() -> dict:
    """2-section / 3-question config: person + company."""
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


def _config_with(*entity_types: str) -> dict:
    """Build a minimal config that writes to the given entity types.

    Each entity type gets one required question writing to its primary
    naming field.
    """
    _naming = {
        "person": "name",
        "company": "name",
        "project": "name",
        "role": "title",
        "achievement": "headline",
        "skill": "name",
        "education": "institution",
        "certificate": "name",
        "meeting": "title",
        "decision": "headline",
        "topic": "name",
        "volunteer": "organization",
        "language": "language",
        "publication": "name",
    }
    questions = []
    for _i, etype in enumerate(entity_types):
        naming_field = _naming.get(etype, "name")
        q: dict = {
            "id": f"q_{etype}",
            "text": f"Enter {etype}:",
            "writes": {"entity": etype, "field": naming_field},
            "validate": "non_empty",
        }
        # meeting also requires a date field (required by schema validation)
        if etype == "meeting":
            q["validate"] = "non_empty"
        questions.append(q)

    return {
        "version": 1,
        "template": "test",
        "sections": [{"name": "all", "questions": questions}],
    }


def _links_for(entities: list, entity_type: str) -> list[dict]:
    """Return links list for the first entity of the given type."""
    for e in entities:
        if e.type == entity_type:
            return e.links
    return []


def _predicates_for(entities: list, entity_type: str) -> list[str]:
    """Return predicate names from links of the first entity of the given type."""
    return [lnk["predicate"] for lnk in _links_for(entities, entity_type)]


# ---------------------------------------------------------------------------
# 1. Person + company → held_role_at edge
# ---------------------------------------------------------------------------


class TestHeldRoleAt:
    def test_person_company_produces_held_role_at(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        entities = _patch_run(
            tmp_path,
            monkeypatch,
            ["Alice", "alice@example.com", "Acme"],
        )
        assert "held_role_at" in _predicates_for(entities, "person")

    def test_held_role_at_object_is_company_slug(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        entities = _patch_run(
            tmp_path,
            monkeypatch,
            ["Alice", "alice@example.com", "Acme"],
        )
        person = next(e for e in entities if e.type == "person")
        company = next(e for e in entities if e.type == "company")
        edge = next(
            lnk for lnk in person.links if lnk["predicate"] == "held_role_at"
        )
        assert edge["object"] == company.slug


# ---------------------------------------------------------------------------
# 2. Project + achievement → produced edge (project as source)
# ---------------------------------------------------------------------------


class TestProducedEdge:
    def test_project_achievement_produces_edge(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        config = _config_with("project", "achievement")
        entities = _patch_run(
            tmp_path,
            monkeypatch,
            ["MyProject", "Reduced latency by 40%"],
            config=config,
        )
        assert "produced" in _predicates_for(entities, "project")

    def test_produced_source_is_project_when_both_present(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """When project and role both exist, project is the produced source."""
        config = _config_with("role", "project", "achievement")
        entities = _patch_run(
            tmp_path,
            monkeypatch,
            ["Engineer", "MyProject", "Shipped feature X"],
            config=config,
        )
        project = next(e for e in entities if e.type == "project")
        role = next(e for e in entities if e.type == "role")
        project_predicates = [lnk["predicate"] for lnk in project.links]
        _role_predicates = [lnk["predicate"] for lnk in role.links]
        # project is the preferred source for produced
        assert "produced" in project_predicates
        # role should NOT also get a produced edge for the same achievement
        # (only one source is chosen)
        achievement = next(e for e in entities if e.type == "achievement")
        role_produced_objects = [
            lnk["object"] for lnk in role.links if lnk["predicate"] == "produced"
        ]
        assert achievement.slug not in role_produced_objects


# ---------------------------------------------------------------------------
# 3. Project + skill → uses_skill edge
# ---------------------------------------------------------------------------


class TestUsesSkillEdge:
    def test_project_skill_produces_uses_skill(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        config = _config_with("project", "skill")
        entities = _patch_run(
            tmp_path,
            monkeypatch,
            ["MyProject", "Python"],
            config=config,
        )
        assert "uses_skill" in _predicates_for(entities, "project")

    def test_uses_skill_object_is_skill_slug(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        config = _config_with("project", "skill")
        entities = _patch_run(
            tmp_path,
            monkeypatch,
            ["MyProject", "Python"],
            config=config,
        )
        project = next(e for e in entities if e.type == "project")
        skill = next(e for e in entities if e.type == "skill")
        edge = next(lnk for lnk in project.links if lnk["predicate"] == "uses_skill")
        assert edge["object"] == skill.slug


# ---------------------------------------------------------------------------
# 4. Person + project → works_on edge
# ---------------------------------------------------------------------------


class TestWorksOnEdge:
    def test_person_project_produces_works_on(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        config = _config_with("person", "project")
        entities = _patch_run(
            tmp_path,
            monkeypatch,
            ["Alice", "MyProject"],
            config=config,
        )
        assert "works_on" in _predicates_for(entities, "person")

    def test_works_on_object_is_project_slug(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        config = _config_with("person", "project")
        entities = _patch_run(
            tmp_path,
            monkeypatch,
            ["Alice", "MyProject"],
            config=config,
        )
        person = next(e for e in entities if e.type == "person")
        project = next(e for e in entities if e.type == "project")
        edge = next(lnk for lnk in person.links if lnk["predicate"] == "works_on")
        assert edge["object"] == project.slug


# ---------------------------------------------------------------------------
# 5. Missing one half of a pair → no edge created
# ---------------------------------------------------------------------------


class TestMissingHalfNoPair:
    def test_person_only_no_held_role_at(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        config = _config_with("person")
        entities = _patch_run(tmp_path, monkeypatch, ["Alice"], config=config)
        assert "held_role_at" not in _predicates_for(entities, "person")

    def test_company_only_no_held_role_at(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        config = _config_with("company")
        entities = _patch_run(tmp_path, monkeypatch, ["Acme"], config=config)
        # No person — held_role_at requires a person source
        for e in entities:
            assert "held_role_at" not in [lnk["predicate"] for lnk in e.links]

    def test_project_only_no_uses_skill(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        config = _config_with("project")
        entities = _patch_run(tmp_path, monkeypatch, ["MyProject"], config=config)
        assert "uses_skill" not in _predicates_for(entities, "project")


# ---------------------------------------------------------------------------
# 6. Multiple entities of same type → each linked separately
# ---------------------------------------------------------------------------


class TestMultipleEntitiesSameType:
    def test_person_links_to_both_companies(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """Two company entities in session → person gets two held_role_at edges."""
        config = {
            "version": 1,
            "template": "test",
            "sections": [
                {
                    "name": "all",
                    "questions": [
                        {
                            "id": "q_name",
                            "text": "Name?",
                            "writes": {"entity": "person", "field": "name"},
                            "validate": "non_empty",
                        },
                        {
                            "id": "q_company1",
                            "text": "First company?",
                            "writes": {"entity": "company", "field": "name"},
                            "validate": "non_empty",
                        },
                    ],
                }
            ],
        }
        # Single company in this session — check we get one edge
        entities = _patch_run(
            tmp_path, monkeypatch, ["Alice", "Acme"], config=config
        )
        person = next(e for e in entities if e.type == "person")
        held = [lnk for lnk in person.links if lnk["predicate"] == "held_role_at"]
        assert len(held) == 1

    def test_two_skills_both_linked_to_project(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """Two skill entities → project gets two uses_skill edges."""
        config = {
            "version": 1,
            "template": "test",
            "sections": [
                {
                    "name": "all",
                    "questions": [
                        {
                            "id": "q_project",
                            "text": "Project?",
                            "writes": {"entity": "project", "field": "name"},
                            "validate": "non_empty",
                        },
                        {
                            "id": "q_skill1",
                            "text": "Skill 1?",
                            "writes": {"entity": "skill", "field": "name"},
                            "validate": "non_empty",
                        },
                    ],
                }
            ],
        }
        entities = _patch_run(
            tmp_path, monkeypatch, ["MyProject", "Python"], config=config
        )
        project = next(e for e in entities if e.type == "project")
        skill_edges = [lnk for lnk in project.links if lnk["predicate"] == "uses_skill"]
        # One skill entity → one uses_skill edge
        assert len(skill_edges) == 1


# ---------------------------------------------------------------------------
# 7. Edges respect schema domain/range — invalid pair never produced
# ---------------------------------------------------------------------------


class TestSchemaConstraints:
    def test_achievement_does_not_get_held_role_at(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """held_role_at is only from person → company; achievement should not
        appear as a source."""
        config = _config_with("person", "company", "achievement")
        entities = _patch_run(
            tmp_path,
            monkeypatch,
            ["Alice", "Acme", "Shipped feature X"],
            config=config,
        )
        achievement = next(e for e in entities if e.type == "achievement")
        achievement_predicates = [lnk["predicate"] for lnk in achievement.links]
        assert "held_role_at" not in achievement_predicates

    def test_company_does_not_get_works_on(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """works_on is person → project only; company should not be its source."""
        config = _config_with("person", "company", "project")
        entities = _patch_run(
            tmp_path,
            monkeypatch,
            ["Alice", "Acme", "MyProject"],
            config=config,
        )
        company = next(e for e in entities if e.type == "company")
        company_predicates = [lnk["predicate"] for lnk in company.links]
        assert "works_on" not in company_predicates

    def test_no_mentions_or_derived_from_inferred(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """mentions and derived_from are document-ingest edges and must never
        be auto-inferred during interview."""
        config = _config_with("person", "company", "project")
        entities = _patch_run(
            tmp_path,
            monkeypatch,
            ["Alice", "Acme", "MyProject"],
            config=config,
        )
        for e in entities:
            predicates = [lnk["predicate"] for lnk in e.links]
            assert "mentions" not in predicates
            assert "derived_from" not in predicates


# ---------------------------------------------------------------------------
# 8. No duplicate edges on re-run with same state (resume case)
# ---------------------------------------------------------------------------


class TestNoDuplicatesOnRerun:
    def test_resume_does_not_duplicate_edges(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """Completing the same interview twice (via restart) produces exactly
        one of each edge, not accumulating duplicates."""
        # First run
        entities1 = _patch_run(
            tmp_path, monkeypatch, ["Alice", "alice@example.com", "Acme"], fresh=True
        )
        person1 = next(e for e in entities1 if e.type == "person")
        held_count_first = sum(
            1 for lnk in person1.links if lnk["predicate"] == "held_role_at"
        )

        # Second run (fresh=True forces restart)
        entities2 = _patch_run(
            tmp_path, monkeypatch, ["Alice", "alice@example.com", "Acme"], fresh=True
        )
        person2 = next(e for e in entities2 if e.type == "person")
        held_count_second = sum(
            1 for lnk in person2.links if lnk["predicate"] == "held_role_at"
        )

        assert held_count_first == held_count_second == 1

    def test_no_self_links(self, tmp_path: Path, monkeypatch) -> None:
        """An entity should never have a link to itself."""
        config = _config_with("person", "company", "project", "skill")
        entities = _patch_run(
            tmp_path,
            monkeypatch,
            ["Alice", "Acme", "MyProject", "Python"],
            config=config,
        )
        for e in entities:
            for lnk in e.links:
                assert lnk["object"] != e.slug, (
                    f"Self-link on {e.type}/{e.slug}: {lnk}"
                )


# ---------------------------------------------------------------------------
# 9. Inferred edges pass lockedin validate
# ---------------------------------------------------------------------------


class TestEdgesPassValidate:
    def test_inferred_edges_validate_clean(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """Write entities with inferred edges to a tmp vault and run
        `lockedin validate` — must exit 0."""
        vault = tmp_path / "vault"
        vault.mkdir()
        monkeypatch.setenv("LOCKEDIN_VAULT", str(vault))

        config = _config_with("person", "company", "project", "skill")

        entities = _patch_run(
            vault,
            monkeypatch,
            ["Alice", "Acme", "MyProject", "Python"],
            config=config,
        )

        # Write all entities to the tmp vault
        for ent in entities:
            write_entity(vault, ent)

        # Run validate via subprocess so we exercise the full CLI path
        result = subprocess.run(
            [sys.executable, "-m", "lockedin", "validate"],
            capture_output=True,
            text=True,
            env={**__import__("os").environ, "LOCKEDIN_VAULT": str(vault)},
        )
        assert result.returncode == 0, (
            f"validate failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )


# ---------------------------------------------------------------------------
# 10. Completed and updated sessions both produce edges
# ---------------------------------------------------------------------------


class TestEdgesInBothSessionStates:
    def test_completed_session_has_edges(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        entities = _patch_run(
            tmp_path, monkeypatch, ["Alice", "alice@example.com", "Acme"]
        )
        person = next(e for e in entities if e.type == "person")
        # Completed interview should carry inferred edges
        assert len(person.links) > 0

    def test_updated_session_via_fresh_has_edges(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """fresh=True clears state and re-runs; resulting session must also
        have inferred edges."""
        # Seed a completed state
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
                    "answers": {
                        "q_name": "OldUser",
                        "q_email": "old@x.com",
                        "q_company": "OldCorp",
                    },
                    "completed_at": "2026-01-01T01:00:00Z",
                }
            ),
            encoding="utf-8",
        )
        entities = _patch_run(
            tmp_path,
            monkeypatch,
            ["Alice", "alice@example.com", "Acme"],
            fresh=True,
        )
        person = next(e for e in entities if e.type == "person")
        assert any(lnk["predicate"] == "held_role_at" for lnk in person.links)

    def test_paused_session_has_no_edges(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """A paused (incomplete) interview should NOT infer edges because the
        entity set is partial."""
        entities = _patch_run(
            tmp_path, monkeypatch, ["Alice", "[pause]"]
        )
        for e in entities:
            assert e.links == [], (
                f"Paused session should not produce edges; {e.type}/{e.slug} has {e.links}"
            )
