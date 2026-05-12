"""Extract and parse Markdown documents (.md, .markdown).

Exposes two functions:

* ``extract_text(path)`` — return raw markdown source or None on read
  error.
* ``parse(path)`` — return a structured dict with sections derived from
  ATX headings (``#``/``##``/``###`` etc.), plus grounding hints for
  dates, URLs, emails, and candidate org names.

Pure stdlib, no optional dependencies.
"""

from __future__ import annotations

import re
from pathlib import Path

from lockedin.ingest._parse_helpers import (
    _find_candidate_orgs,
    _find_dates,
    _find_emails,
    _find_urls,
)


def extract_text(path: Path) -> str | None:
    """Return raw markdown source, or None on read error. Never raises."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def parse(path: Path) -> dict:
    """Return a structured parse dict.

    Keys: text, format, sections, dates, urls, emails, candidate_orgs.
    On extraction failure returns the same shape with empty/blank values.
    Never raises.
    """
    try:
        text = extract_text(path) or ""
        sections = _parse_md_sections(text)
        return {
            "text": text,
            "format": "markdown",
            "sections": sections,
            "dates": _find_dates(text),
            "urls": _find_urls(text),
            "emails": _find_emails(text),
            "candidate_orgs": _find_candidate_orgs(text),
        }
    except Exception:  # noqa: BLE001
        return {
            "text": "",
            "format": "markdown",
            "sections": [],
            "dates": [],
            "urls": [],
            "emails": [],
            "candidate_orgs": [],
        }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_ATX_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)")


def _parse_md_sections(text: str) -> list[dict]:
    """Parse ATX headings (``#`` to ``######``) into sections.

    Each section dict has ``heading`` (str), ``body`` (str), ``level`` (int).
    If no headings are found, returns a single section with heading="" and
    the full text as body.
    """
    if not text:
        return [{"heading": "", "body": "", "level": 1}]

    lines = text.splitlines()
    sections: list[dict] = []
    current_heading = ""
    current_level = 1
    current_body_lines: list[str] = []

    def _flush() -> None:
        body = "\n".join(current_body_lines).strip()
        sections.append({"heading": current_heading, "body": body, "level": current_level})

    for line in lines:
        m = _ATX_HEADING_RE.match(line)
        if m:
            if current_body_lines or current_heading:
                _flush()
            current_level = len(m.group(1))
            current_heading = m.group(2).strip()
            current_body_lines = []
        else:
            current_body_lines.append(line)

    # Flush final section.
    if current_heading or current_body_lines:
        _flush()

    if not sections:
        return [{"heading": "", "body": text.strip(), "level": 1}]

    # If nothing was a heading, return one section with all text.
    if all(s["heading"] == "" for s in sections):
        return [{"heading": "", "body": text.strip(), "level": 1}]

    return sections
