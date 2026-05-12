"""Extract and parse .docx (Word) documents.

Exposes two functions:

* ``extract_text(path)`` — return paragraph text joined by newlines, or
  None if python-docx is not installed or the file is unreadable.
* ``parse(path)`` — return a structured dict with conservative section
  detection and grounding hints for dates, URLs, emails, and candidate
  org names.

Optional dependency: ``pip install lockedin[docx]`` (python-docx). The
import is lazy; importing this module without python-docx installed is
safe and ``extract_text`` will return None.
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
    """Return paragraph text from a .docx file joined by newlines.

    Returns None if python-docx is not installed, the file is unreadable,
    or any other error occurs. Never raises.
    """
    try:
        import docx  # type: ignore[import-not-found]  # python-docx
    except ImportError:
        return None
    try:
        document = docx.Document(str(path))
        return "\n".join(p.text for p in document.paragraphs)
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
            "format": "docx",
            "sections": sections,
            "dates": _find_dates(text),
            "urls": _find_urls(text),
            "emails": _find_emails(text),
            "candidate_orgs": _find_candidate_orgs(text),
        }
    except Exception:  # noqa: BLE001
        return {
            "text": "",
            "format": "docx",
            "sections": [],
            "dates": [],
            "urls": [],
            "emails": [],
            "candidate_orgs": [],
        }
