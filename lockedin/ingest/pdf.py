"""Extract and parse PDF documents.

Exposes two functions:

* ``extract_text(path)`` — return concatenated page text from a PDF, or
  None if pypdf is not installed or the file is unreadable.
* ``parse(path)`` — return a structured dict with conservative section
  detection and grounding hints for dates, URLs, emails, and candidate
  org names.

Optional dependency: ``pip install lockedin[pdf]`` (pypdf). The import
is lazy; importing this module without pypdf installed is safe and
``extract_text`` will return None.
"""

from __future__ import annotations

from pathlib import Path

from lockedin.ingest._parse_helpers import (
    _find_candidate_orgs,
    _find_dates,
    _find_emails,
    _find_urls,
)
from lockedin.ingest._section_heuristics import parse_generic_sections


def extract_text(path: Path) -> str | None:
    """Return concatenated text from all PDF pages.

    Returns None if pypdf is not installed, the file is unreadable, or
    any other error occurs. Never raises.
    """
    try:
        from pypdf import PdfReader  # type: ignore[import-not-found]
    except ImportError:
        return None
    try:
        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception:  # noqa: BLE001
        return None


def parse(path: Path) -> dict:
    """Return a structured parse dict.

    Keys: text, format, sections, dates, urls, emails, candidate_orgs.
    On extraction failure returns the same shape with empty/blank values.
    Never raises.
    """
    try:
        text = extract_text(path) or ""
        sections = parse_generic_sections(text)
        return {
            "text": text,
            "format": "pdf",
            "sections": sections,
            "dates": _find_dates(text),
            "urls": _find_urls(text),
            "emails": _find_emails(text),
            "candidate_orgs": _find_candidate_orgs(text),
        }
    except Exception:  # noqa: BLE001
        return {
            "text": "",
            "format": "pdf",
            "sections": [],
            "dates": [],
            "urls": [],
            "emails": [],
            "candidate_orgs": [],
        }
