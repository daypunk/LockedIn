"""Anti-drift lint: README files promise PDF / DOCX / markdown / text ingest.

If a future commit re-stubs these ingest modules with NotImplementedError,
this test catches it before users hit broken behavior. Pairs with the
ingest layer at lockedin/ingest/{pdf,docx,markdown,text}.py — the modules
must keep exposing real extract_text() and parse() functions that handle
empty input gracefully.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from lockedin.ingest import docx, markdown, pdf, text

REPO_ROOT = Path(__file__).resolve().parent.parent

README_FILES = (
    REPO_ROOT / "README.md",
    REPO_ROOT / "README.ko.md",
    REPO_ROOT / "README.ja.md",
    REPO_ROOT / "README.zh.md",
)

INGEST_MODULES = (pdf, docx, markdown, text)


def test_all_readmes_exist() -> None:
    missing = [f.name for f in README_FILES if not f.exists()]
    assert not missing, f"missing README files: {missing}"


@pytest.mark.parametrize("module", INGEST_MODULES)
def test_module_exports_extract_text(module) -> None:
    assert hasattr(module, "extract_text"), (
        f"{module.__name__}.extract_text removed — would break ingest pipeline "
        f"and contradict README promises about document ingestion."
    )


@pytest.mark.parametrize("module", INGEST_MODULES)
def test_module_exports_parse(module) -> None:
    assert hasattr(module, "parse"), (
        f"{module.__name__}.parse removed — would break ingest pipeline "
        f"and contradict README promises about document ingestion."
    )


@pytest.mark.parametrize(
    ("module", "suffix"),
    [
        (pdf, ".pdf"),
        (docx, ".docx"),
        (markdown, ".md"),
        (text, ".txt"),
    ],
)
def test_extract_text_not_restubbed(module, suffix: str, tmp_path: Path) -> None:
    """Regression guard: a future commit must not re-introduce NotImplementedError."""
    fake_file = tmp_path / f"empty{suffix}"
    fake_file.write_text("", encoding="utf-8")
    try:
        module.extract_text(fake_file)  # may return None or "" — both fine
    except NotImplementedError as exc:
        pytest.fail(
            f"{module.__name__}.extract_text re-stubbed with NotImplementedError: {exc}. "
            f"All four READMEs promise document ingestion; do not regress this."
        )


@pytest.mark.parametrize(
    ("module", "suffix"),
    [
        (pdf, ".pdf"),
        (docx, ".docx"),
        (markdown, ".md"),
        (text, ".txt"),
    ],
)
def test_parse_not_restubbed(module, suffix: str, tmp_path: Path) -> None:
    fake_file = tmp_path / f"empty{suffix}"
    fake_file.write_text("", encoding="utf-8")
    try:
        result = module.parse(fake_file)
    except NotImplementedError as exc:
        pytest.fail(
            f"{module.__name__}.parse re-stubbed with NotImplementedError: {exc}. "
            f"All four READMEs promise document ingestion; do not regress this."
        )
    assert isinstance(result, dict), f"{module.__name__}.parse must return a dict"
    for key in ("text", "format", "sections", "dates", "urls", "emails", "candidate_orgs"):
        assert key in result, f"{module.__name__}.parse missing key {key!r} in output"


def test_readmes_mention_document_ingest() -> None:
    """Living documentation: each README mentions document ingestion in some form.

    If a future commit silently drops the document-ingest promise from a README,
    the asymmetry between code (still supports ingest) and docs (no longer says so)
    would be a quieter form of drift. Catch the surface mention.
    """
    keywords = ("PDF", "pdf", "DOCX", "docx", "履歴書", "이력서", "简历", "resume")
    for readme in README_FILES:
        content = readme.read_text(encoding="utf-8")
        if not any(kw in content for kw in keywords):
            pytest.fail(
                f"{readme.name} no longer mentions any of {keywords} — "
                f"document ingestion promise dropped from README without code change."
            )
