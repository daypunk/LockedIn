"""Calibration guard tests for render-jaso fixtures.

For each pass fixture: asserts it does NOT contain any high-severity
phrase from banned_phrases.json (cross-source quality guard).

For each fail fixture: asserts it DOES contain at least one phrase
from banned_phrases.json OR has a documented structural failure mode
(expected_revisions_required: true in YAML frontmatter).

These tests catch fixture rot before reviewer scoring would.
Pattern: load banned_phrases.json, regex-match against fixture text.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / "plugins" / "lockedin" / "skills" / "lockedin-render-jaso"
BANNED_PHRASES_PATH = SKILL_DIR / "banned_phrases.json"
RUBRIC_PATH = SKILL_DIR / "RUBRIC.md"
PASS_DIR = REPO_ROOT / "tests" / "fixtures" / "jaso" / "pass"
FAIL_DIR = REPO_ROOT / "tests" / "fixtures" / "jaso" / "fail"

_REQUIRED_FRONTMATTER_KEYS = {"fixture_kind", "target_question"}


def _load_banned_phrases() -> list[dict]:
    with BANNED_PHRASES_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    return data["phrases"]


def _build_pattern(phrase: str) -> re.Pattern:
    """Return a case-insensitive whole-phrase regex pattern."""
    escaped = re.escape(phrase)
    return re.compile(r"\b" + escaped + r"\b", re.IGNORECASE)


def _get_fixture_body(path: Path) -> str:
    """Return fixture text with YAML frontmatter stripped."""
    raw = path.read_text(encoding="utf-8")
    if raw.startswith("---"):
        end = raw.find("---", 3)
        if end != -1:
            return raw[end + 3:].strip()
    return raw


def _get_frontmatter_text(path: Path) -> str:
    """Return raw frontmatter block text (between the --- delimiters)."""
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        return ""
    end = raw.find("---", 3)
    if end == -1:
        return ""
    return raw[3:end]


def _frontmatter_says_revisions_required(path: Path) -> bool:
    """Check expected_revisions_required in YAML frontmatter."""
    front = _get_frontmatter_text(path)
    return "expected_revisions_required: true" in front


def test_banned_phrases_schema() -> None:
    """banned_phrases.json must exist, have ≥20 entries, each with required keys."""
    assert BANNED_PHRASES_PATH.exists(), (
        f"banned_phrases.json missing at {BANNED_PHRASES_PATH}"
    )
    phrases = _load_banned_phrases()
    assert len(phrases) >= 20, (
        f"Expected at least 20 banned phrases, got {len(phrases)}"
    )
    for entry in phrases:
        assert "phrase" in entry, f"Missing 'phrase' key in entry: {entry}"
        assert "category" in entry, f"Missing 'category' key in entry: {entry}"
        assert "severity" in entry, f"Missing 'severity' key in entry: {entry}"
        assert "sources" in entry, f"Missing 'sources' key in entry: {entry}"
        assert len(entry["sources"]) >= 2, (
            f"Phrase '{entry['phrase']}' has fewer than 2 sources: {entry['sources']}"
        )


def test_pass_fixtures_exist() -> None:
    pass_files = sorted(PASS_DIR.glob("*.md"))
    assert len(pass_files) >= 3, (
        f"Expected at least 3 pass fixtures under {PASS_DIR}, found {len(pass_files)}"
    )


def test_fail_fixtures_exist() -> None:
    fail_files = sorted(FAIL_DIR.glob("*.md"))
    assert len(fail_files) >= 3, (
        f"Expected at least 3 fail fixtures under {FAIL_DIR}, found {len(fail_files)}"
    )


def test_pass_fixtures_free_of_high_severity_banned_phrases() -> None:
    """Pass fixtures must not contain any high-severity banned phrase."""
    phrases = _load_banned_phrases()
    high_phrases = [p for p in phrases if p["severity"] == "high"]
    pass_files = sorted(PASS_DIR.glob("*.md"))
    assert pass_files, f"No pass fixtures found under {PASS_DIR}"

    violations: list[str] = []
    for fixture in pass_files:
        body = _get_fixture_body(fixture)
        for entry in high_phrases:
            pattern = _build_pattern(entry["phrase"])
            if pattern.search(body):
                violations.append(
                    f"{fixture.name}: contains high-severity banned phrase "
                    f"'{entry['phrase']}' (category: {entry['category']})"
                )

    assert not violations, (
        "Pass fixtures contain high-severity banned phrases — fixture rot detected:\n"
        + "\n".join(violations)
    )


def test_fail_fixtures_trigger_revision() -> None:
    """Fail fixtures must either contain a banned phrase or declare revisions_required."""
    phrases = _load_banned_phrases()
    patterns = [(_build_pattern(p["phrase"]), p["phrase"]) for p in phrases]
    fail_files = sorted(FAIL_DIR.glob("*.md"))
    assert fail_files, f"No fail fixtures found under {FAIL_DIR}"

    no_failure_signal: list[str] = []
    for fixture in fail_files:
        body = _get_fixture_body(fixture)
        has_banned = any(pat.search(body) for pat, _ in patterns)
        has_revision_flag = _frontmatter_says_revisions_required(fixture)
        if not has_banned and not has_revision_flag:
            no_failure_signal.append(
                f"{fixture.name}: no banned phrase found and frontmatter does not "
                f"declare expected_revisions_required: true"
            )

    assert not no_failure_signal, (
        "Fail fixtures have no detectable failure signal:\n"
        + "\n".join(no_failure_signal)
    )


def test_rubric_exists_and_nonempty() -> None:
    """RUBRIC.md must exist in the skill directory and be non-empty."""
    assert RUBRIC_PATH.exists(), f"RUBRIC.md missing at {RUBRIC_PATH}"
    content = RUBRIC_PATH.read_text(encoding="utf-8").strip()
    assert len(content) > 100, (
        f"RUBRIC.md at {RUBRIC_PATH} appears empty or trivially short "
        f"(length={len(content)})"
    )


def test_fixtures_have_valid_frontmatter() -> None:
    """All fixtures must have YAML frontmatter with fixture_kind and target_question."""
    yaml = pytest.importorskip("yaml")
    all_files = sorted(PASS_DIR.glob("*.md")) + sorted(FAIL_DIR.glob("*.md"))
    assert all_files, "No fixture files found in pass/ or fail/ directories"

    invalid: list[str] = []
    for fixture in all_files:
        front_text = _get_frontmatter_text(fixture)
        if not front_text.strip():
            invalid.append(f"{fixture.name}: missing YAML frontmatter")
            continue
        try:
            data = yaml.safe_load(front_text)
        except yaml.YAMLError as exc:
            invalid.append(f"{fixture.name}: YAML parse error — {exc}")
            continue
        if not isinstance(data, dict):
            invalid.append(f"{fixture.name}: frontmatter is not a YAML mapping")
            continue
        for key in _REQUIRED_FRONTMATTER_KEYS:
            if key not in data:
                invalid.append(
                    f"{fixture.name}: missing required frontmatter key '{key}'"
                )

    assert not invalid, (
        "Fixtures with invalid frontmatter:\n" + "\n".join(invalid)
    )
