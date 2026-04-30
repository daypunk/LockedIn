"""Pre-alpha smoke tests.

These confirm the package is importable and the ontology constants are in
place. Real behavioral tests land per-feature.
"""

from __future__ import annotations


def test_package_imports() -> None:
    import selfgraph

    assert selfgraph.__version__


def test_ontology_constants_loaded() -> None:
    from selfgraph.ontology import EDGE_PREDICATES, ENTITY_TYPES

    assert "person" in ENTITY_TYPES
    assert "project" in ENTITY_TYPES
    assert "works_on" in EDGE_PREDICATES
    assert len(set(ENTITY_TYPES)) == len(ENTITY_TYPES), "duplicate entity types"
    assert len(set(EDGE_PREDICATES)) == len(EDGE_PREDICATES), "duplicate edge predicates"


def test_ontology_entity_validates_type() -> None:
    import pytest

    from selfgraph.ontology import Entity

    Entity(type="person", title="Test", slug="test")  # ok

    with pytest.raises(ValueError):
        Entity(type="not-a-type", title="X", slug="x")


def test_ontology_edge_validates_predicate() -> None:
    import pytest

    from selfgraph.ontology import Edge

    Edge(subject="a", predicate="works_on", object="b")  # ok

    with pytest.raises(ValueError):
        Edge(subject="a", predicate="not-a-predicate", object="b")


def test_cli_help_runs_with_no_args() -> None:
    from selfgraph.cli import main

    rc = main([])
    assert rc == 0


def test_cli_version_exits_zero() -> None:
    import pytest

    from selfgraph.cli import main

    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0


def test_cli_skill_only_command_redirects() -> None:
    from selfgraph.cli import SKILL_REDIRECT_EXIT, main

    rc = main(["render", "jaso", "--company", "X"])
    assert rc == SKILL_REDIRECT_EXIT
