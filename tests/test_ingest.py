"""Tests for the refactored ingest layer.

Covers:
- extract_text for each format (md, txt, pdf, docx) with tmp_path fixtures
- parse() returns the expected dict shape
- parse() contains at least one date, url, email, candidate_org for crafted input
- Missing optional dep path: pdf/docx extract_text returns None gracefully
- parse() never raises on malformed input
- ingest_dry_run integration smoke test still passes
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from lockedin.commands.ingest_dry import ingest_dry_run
from lockedin.ingest import docx as docx_mod
from lockedin.ingest import markdown as md_mod
from lockedin.ingest import pdf as pdf_mod
from lockedin.ingest import text as text_mod
from lockedin.ingest._parse_helpers import (
    _find_candidate_orgs,
    _find_dates,
    _find_emails,
    _find_urls,
)

# ---------------------------------------------------------------------------
# Sample document content with grounding fixtures embedded
# ---------------------------------------------------------------------------

RICH_CONTENT = """\
# Work Experience

Joined Acme Corp in January 2020 and left in 2022-06.
Contact: jane.doe@example.com
Portfolio: https://jane.example.com/portfolio
Worked at Global Tech Inc. on distributed systems.
Global Tech Inc. shipped 3 major releases.

## Education

State University, 2014-09 to 2018-05
"""

# ---------------------------------------------------------------------------
# text.py
# ---------------------------------------------------------------------------


class TestTextExtractText:
    def test_reads_utf8(self, tmp_path: Path) -> None:
        f = tmp_path / "notes.txt"
        f.write_text("hello world\n", encoding="utf-8")
        assert text_mod.extract_text(f) == "hello world\n"

    def test_returns_none_on_missing_file(self, tmp_path: Path) -> None:
        assert text_mod.extract_text(tmp_path / "no-such.txt") is None

    def test_never_raises_on_directory(self, tmp_path: Path) -> None:
        # Passing a directory should not raise; OSError returns None.
        result = text_mod.extract_text(tmp_path)
        # Either None or some string is acceptable; must not raise.
        assert result is None or isinstance(result, str)


class TestTextParse:
    def test_dict_shape(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.txt"
        f.write_text(RICH_CONTENT, encoding="utf-8")
        result = text_mod.parse(f)
        assert set(result) == {"text", "format", "sections", "dates", "urls", "emails", "candidate_orgs"}

    def test_format_is_text(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.txt"
        f.write_text("hello", encoding="utf-8")
        assert text_mod.parse(f)["format"] == "text"

    def test_sections_is_list(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.txt"
        f.write_text("hello", encoding="utf-8")
        result = text_mod.parse(f)
        assert isinstance(result["sections"], list)
        assert len(result["sections"]) >= 1

    def test_section_shape(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.txt"
        f.write_text("hello", encoding="utf-8")
        section = text_mod.parse(f)["sections"][0]
        assert "heading" in section and "body" in section and "level" in section

    def test_finds_date_in_content(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.txt"
        f.write_text(RICH_CONTENT, encoding="utf-8")
        dates = text_mod.parse(f)["dates"]
        assert any("2020" in d for d in dates)

    def test_finds_url_in_content(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.txt"
        f.write_text(RICH_CONTENT, encoding="utf-8")
        urls = text_mod.parse(f)["urls"]
        assert any("example.com" in u for u in urls)

    def test_finds_email_in_content(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.txt"
        f.write_text(RICH_CONTENT, encoding="utf-8")
        emails = text_mod.parse(f)["emails"]
        assert "jane.doe@example.com" in emails

    def test_finds_candidate_org_in_content(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.txt"
        f.write_text(RICH_CONTENT, encoding="utf-8")
        orgs = text_mod.parse(f)["candidate_orgs"]
        # "Global Tech Inc." appears twice, so heuristic should pick it up.
        assert any("Global Tech" in o for o in orgs)

    def test_never_raises_on_missing_file(self, tmp_path: Path) -> None:
        result = text_mod.parse(tmp_path / "no-such.txt")
        assert result["text"] == ""
        assert isinstance(result["sections"], list)

    def test_never_raises_on_empty_file(self, tmp_path: Path) -> None:
        f = tmp_path / "empty.txt"
        f.write_text("", encoding="utf-8")
        result = text_mod.parse(f)
        assert isinstance(result["sections"], list)


# ---------------------------------------------------------------------------
# markdown.py
# ---------------------------------------------------------------------------


class TestMarkdownExtractText:
    def test_reads_content(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text("# Title\n\nbody.", encoding="utf-8")
        assert "# Title" in (md_mod.extract_text(f) or "")

    def test_returns_none_on_missing_file(self, tmp_path: Path) -> None:
        assert md_mod.extract_text(tmp_path / "no-such.md") is None


class TestMarkdownParse:
    def test_dict_shape(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text(RICH_CONTENT, encoding="utf-8")
        result = md_mod.parse(f)
        assert set(result) == {"text", "format", "sections", "dates", "urls", "emails", "candidate_orgs"}

    def test_format_is_markdown(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text("# Hi", encoding="utf-8")
        assert md_mod.parse(f)["format"] == "markdown"

    def test_sections_parsed_from_headings(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text("# Section One\n\nbody1\n\n## Section Two\n\nbody2", encoding="utf-8")
        sections = md_mod.parse(f)["sections"]
        headings = [s["heading"] for s in sections]
        assert "Section One" in headings
        assert "Section Two" in headings

    def test_section_levels(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text("# H1\n## H2\n### H3", encoding="utf-8")
        sections = md_mod.parse(f)["sections"]
        levels = {s["heading"]: s["level"] for s in sections}
        assert levels.get("H1") == 1
        assert levels.get("H2") == 2
        assert levels.get("H3") == 3

    def test_finds_date(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text(RICH_CONTENT, encoding="utf-8")
        assert any("2020" in d for d in md_mod.parse(f)["dates"])

    def test_finds_url(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text(RICH_CONTENT, encoding="utf-8")
        assert any("example.com" in u for u in md_mod.parse(f)["urls"])

    def test_finds_email(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text(RICH_CONTENT, encoding="utf-8")
        assert "jane.doe@example.com" in md_mod.parse(f)["emails"]

    def test_finds_candidate_org(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text(RICH_CONTENT, encoding="utf-8")
        orgs = md_mod.parse(f)["candidate_orgs"]
        assert any("Global Tech" in o for o in orgs)

    def test_no_headings_returns_one_section(self, tmp_path: Path) -> None:
        f = tmp_path / "plain.md"
        f.write_text("no headings here\njust prose", encoding="utf-8")
        sections = md_mod.parse(f)["sections"]
        assert len(sections) == 1
        assert sections[0]["heading"] == ""

    def test_never_raises_on_missing_file(self, tmp_path: Path) -> None:
        result = md_mod.parse(tmp_path / "no-such.md")
        assert result["text"] == ""

    def test_never_raises_on_empty_file(self, tmp_path: Path) -> None:
        f = tmp_path / "empty.md"
        f.write_text("", encoding="utf-8")
        result = md_mod.parse(f)
        assert isinstance(result["sections"], list)


# ---------------------------------------------------------------------------
# pdf.py — optional dep path
# ---------------------------------------------------------------------------


class TestPdfExtractText:
    def test_returns_none_when_pypdf_missing(self, tmp_path: Path) -> None:
        """When pypdf is not importable, extract_text must return None."""
        f = tmp_path / "fake.pdf"
        f.write_bytes(b"%PDF fake content")
        # Temporarily hide pypdf from sys.modules.
        with patch.dict(sys.modules, {"pypdf": None}):
            # Re-import the module to pick up patched sys.modules.
            import importlib
            mod = importlib.import_module("lockedin.ingest.pdf")
            importlib.reload(mod)
            result = mod.extract_text(f)
        assert result is None

    def test_returns_none_on_missing_file(self, tmp_path: Path) -> None:
        result = pdf_mod.extract_text(tmp_path / "no-such.pdf")
        assert result is None


class TestPdfParse:
    def test_dict_shape_on_failure(self, tmp_path: Path) -> None:
        """parse() on a missing file returns the correct empty shape."""
        result = pdf_mod.parse(tmp_path / "no-such.pdf")
        assert set(result) == {"text", "format", "sections", "dates", "urls", "emails", "candidate_orgs"}
        assert result["text"] == ""
        assert result["format"] == "pdf"
        assert isinstance(result["sections"], list)

    def test_never_raises_on_malformed_input(self, tmp_path: Path) -> None:
        f = tmp_path / "bad.pdf"
        f.write_bytes(b"not a real pdf")
        # If pypdf is present it may raise internally; parse() must absorb it.
        result = pdf_mod.parse(f)
        assert isinstance(result, dict)
        assert "text" in result

    @pytest.mark.skipif(
        importlib.util.find_spec("pypdf") is None, reason="pypdf not installed"
    )
    def test_parse_with_pypdf_available(self, tmp_path: Path) -> None:
        """When pypdf is present, parse() on a non-PDF returns gracefully."""
        f = tmp_path / "bad.pdf"
        f.write_bytes(b"not a real pdf")
        result = pdf_mod.parse(f)
        assert isinstance(result["sections"], list)


# ---------------------------------------------------------------------------
# docx.py — optional dep path
# ---------------------------------------------------------------------------


class TestDocxExtractText:
    def test_returns_none_when_docx_missing(self, tmp_path: Path) -> None:
        """When python-docx is not importable, extract_text must return None."""
        f = tmp_path / "fake.docx"
        f.write_bytes(b"PK fake content")
        with patch.dict(sys.modules, {"docx": None}):
            mod = importlib.import_module("lockedin.ingest.docx")
            importlib.reload(mod)
            result = mod.extract_text(f)
        assert result is None

    def test_returns_none_on_missing_file(self, tmp_path: Path) -> None:
        result = docx_mod.extract_text(tmp_path / "no-such.docx")
        assert result is None


class TestDocxParse:
    def test_dict_shape_on_failure(self, tmp_path: Path) -> None:
        result = docx_mod.parse(tmp_path / "no-such.docx")
        assert set(result) == {"text", "format", "sections", "dates", "urls", "emails", "candidate_orgs"}
        assert result["text"] == ""
        assert result["format"] == "docx"
        assert isinstance(result["sections"], list)

    def test_never_raises_on_malformed_input(self, tmp_path: Path) -> None:
        f = tmp_path / "bad.docx"
        f.write_bytes(b"not a real docx")
        result = docx_mod.parse(f)
        assert isinstance(result, dict)
        assert "text" in result


# ---------------------------------------------------------------------------
# _parse_helpers — unit tests for date/url/email/org regexes
# ---------------------------------------------------------------------------


class TestFindDates:
    def test_iso_date(self) -> None:
        assert "2023-07-15" in _find_dates("On 2023-07-15 we shipped it.")

    def test_year_month(self) -> None:
        assert "2022-06" in _find_dates("Ended 2022-06 at the company.")

    def test_bare_year(self) -> None:
        assert "2020" in _find_dates("Joined in 2020.")

    def test_month_name_year(self) -> None:
        dates = _find_dates("Started January 2019.")
        assert any("January" in d and "2019" in d for d in dates)

    def test_korean_date(self) -> None:
        dates = _find_dates("2021년 3월에 입사했습니다.")
        assert any("2021년" in d for d in dates)

    def test_deduplication(self) -> None:
        dates = _find_dates("2020 and again 2020")
        assert dates.count("2020") == 1

    def test_empty_string(self) -> None:
        assert _find_dates("") == []


class TestFindUrls:
    def test_https(self) -> None:
        assert "https://example.com/page" in _find_urls("See https://example.com/page for details.")

    def test_strips_trailing_punctuation(self) -> None:
        urls = _find_urls("Visit https://example.com/page.")
        assert all(not u.endswith(".") for u in urls)

    def test_deduplication(self) -> None:
        urls = _find_urls("https://a.com and https://a.com")
        assert urls.count("https://a.com") == 1

    def test_empty_string(self) -> None:
        assert _find_urls("") == []


class TestFindEmails:
    def test_standard_email(self) -> None:
        assert "user@example.com" in _find_emails("Contact user@example.com please.")

    def test_deduplication(self) -> None:
        emails = _find_emails("a@b.com and a@b.com")
        assert emails.count("a@b.com") == 1

    def test_empty_string(self) -> None:
        assert _find_emails("") == []


class TestFindCandidateOrgs:
    def test_org_suffix_line(self) -> None:
        text = "Worked at\nAcme Corp\nThen Global Tech Inc.\n"
        orgs = _find_candidate_orgs(text)
        assert any("Global Tech Inc" in o for o in orgs)

    def test_repeated_capitalized_phrase(self) -> None:
        # "Cloud Systems" appears twice → should be a candidate.
        text = "Cloud Systems deployed the feature. Cloud Systems also fixed the bug."
        orgs = _find_candidate_orgs(text)
        assert any("Cloud Systems" in o for o in orgs)

    def test_single_occurrence_not_included(self) -> None:
        # "Blue Widget" appears once only — must NOT appear in candidate orgs.
        text = "Blue Widget was mentioned once."
        orgs = _find_candidate_orgs(text)
        assert not any("Blue Widget" in o for o in orgs)

    def test_empty_string(self) -> None:
        assert _find_candidate_orgs("") == []


# ---------------------------------------------------------------------------
# ingest_dry_run — integration smoke test after refactor
# ---------------------------------------------------------------------------


class TestIngestDryRunIntegration:
    def test_md_and_txt_still_reported(self, tmp_path: Path, capsys) -> None:
        (tmp_path / "doc.md").write_text("# Title\n\nbody.", encoding="utf-8")
        (tmp_path / "notes.txt").write_text("plain\nlines", encoding="utf-8")
        rc = ingest_dry_run(str(tmp_path))
        assert rc == 0
        out = capsys.readouterr().out
        assert "parsed: 2" in out
        assert "doc.md" in out
        assert "notes.txt" in out

    def test_missing_path_returns_1(self, tmp_path: Path, capsys) -> None:
        rc = ingest_dry_run(str(tmp_path / "no-such"))
        assert rc == 1
        assert "path not found" in capsys.readouterr().out

    def test_empty_dir_returns_0(self, tmp_path: Path, capsys) -> None:
        rc = ingest_dry_run(str(tmp_path))
        assert rc == 0
        assert "no supported files" in capsys.readouterr().out

    def test_markdown_extension_dispatched(self, tmp_path: Path, capsys) -> None:
        (tmp_path / "doc.markdown").write_text("hello", encoding="utf-8")
        rc = ingest_dry_run(str(tmp_path))
        assert rc == 0
        out = capsys.readouterr().out
        assert "parsed: 1" in out

    def test_next_step_hint_present(self, tmp_path: Path, capsys) -> None:
        (tmp_path / "f.txt").write_text("data", encoding="utf-8")
        ingest_dry_run(str(tmp_path))
        out = capsys.readouterr().out
        assert "/lockedin ingest" in out
