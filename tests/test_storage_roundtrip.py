"""Round-trip and graph derivation tests for the storage layer."""

from __future__ import annotations

from pathlib import Path

import pytest

from lockedin.ontology import Entity
from lockedin.storage.graph import derive_graph_json, write_graph_json
from lockedin.storage.notes import read_entity, vault_path_for, write_entity


def _sample_person() -> Entity:
    return Entity(
        type="person",
        title="Sample User",
        slug="sample-user",
        body="Some markdown body.\nLine two.\n",
        fields={"current_role": "PM", "email": "x@y.com"},
        links=[
            {"predicate": "works_on", "object": "project-a", "weight": 1.0},
            {"predicate": "held_role_at", "object": "company-a", "weight": 1.0},
        ],
        created="2026-04-30T10:00:00Z",
        updated="2026-04-30T10:00:00Z",
    )


def test_write_then_read_recovers_entity(tmp_path: Path) -> None:
    entity = _sample_person()
    write_entity(tmp_path, entity)
    path = vault_path_for(tmp_path, entity)
    loaded = read_entity(path)
    assert loaded.type == entity.type
    assert loaded.title == entity.title
    assert loaded.slug == entity.slug
    assert loaded.fields == entity.fields
    assert loaded.links == entity.links
    assert loaded.created == entity.created
    assert loaded.updated == entity.updated
    assert loaded.body == entity.body


def test_round_trip_byte_identical(tmp_path: Path) -> None:
    """read → write produces a file whose bytes match the original."""
    entity = _sample_person()
    path = write_entity(tmp_path, entity)
    original_bytes = path.read_bytes()

    loaded = read_entity(path)
    write_entity(tmp_path, loaded)
    assert path.read_bytes() == original_bytes


def test_write_fills_timestamps_when_none(tmp_path: Path) -> None:
    entity = Entity(type="person", title="X", slug="x")
    assert entity.created is None and entity.updated is None
    write_entity(tmp_path, entity)
    assert entity.created is not None
    assert entity.updated == entity.created


def test_korean_title_round_trip(tmp_path: Path) -> None:
    entity = Entity(
        type="company",
        title="회사 이름",
        slug="company-ko",
        body="한국어 본문.\n",
        created="2026-04-30T10:00:00Z",
        updated="2026-04-30T10:00:00Z",
    )
    path = write_entity(tmp_path, entity)
    loaded = read_entity(path)
    assert loaded.title == "회사 이름"
    assert loaded.body == "한국어 본문.\n"


def test_invalid_entity_type_rejected() -> None:
    with pytest.raises(ValueError):
        Entity(type="not-a-type", title="X", slug="x")


def test_derive_graph_json_walks_vault(tmp_path: Path) -> None:
    person = _sample_person()
    project = Entity(
        type="project",
        title="Project A",
        slug="project-a",
        created="2026-04-30T10:00:00Z",
        updated="2026-04-30T10:00:00Z",
    )
    company = Entity(
        type="company",
        title="Company A",
        slug="company-a",
        created="2026-04-30T10:00:00Z",
        updated="2026-04-30T10:00:00Z",
    )
    write_entity(tmp_path, person)
    write_entity(tmp_path, project)
    write_entity(tmp_path, company)

    graph = derive_graph_json(tmp_path)
    assert {n["id"] for n in graph["nodes"]} == {"sample-user", "project-a", "company-a"}
    edges = [(e["source"], e["predicate"], e["target"]) for e in graph["edges"]]
    assert ("sample-user", "works_on", "project-a") in edges
    assert ("sample-user", "held_role_at", "company-a") in edges


def test_derive_graph_json_empty_when_vault_missing(tmp_path: Path) -> None:
    nonexistent = tmp_path / "no-such-vault"
    graph = derive_graph_json(nonexistent)
    assert graph == {"nodes": [], "edges": []}


def test_write_graph_json_emits_outputs_dir(tmp_path: Path) -> None:
    write_entity(tmp_path, _sample_person())
    out = write_graph_json(tmp_path)
    assert out == tmp_path / "outputs" / "graph.json"
    assert out.exists()
