"""Extract and parse plain-text documents (.txt and similar).

Exposes two functions:

* ``extract_text(path)`` — return raw text or None on read error.
* ``parse(path)`` — return a structured dict with grounding hints
  (sections, dates, urls, emails, candidate_orgs) for the skill side.

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
    """Return raw text from a plain-text file, or None on read error. Never raises."""
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
        sections = _parse_text_sections(text)
        return {
            "text": text,
            "format": "text",
            "sections": sections,
            "dates": _find_dates(text),
            "urls": _find_urls(text),
            "emails": _find_emails(text),
            "candidate_orgs": _find_candidate_orgs(text),
        }
    except Exception:  # noqa: BLE001
        return {
            "text": "",
            "format": "text",
            "sections": [],
            "dates": [],
            "urls": [],
            "emails": [],
            "candidate_orgs": [],
        }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

# Heading heuristic: ALL-CAPS short lines (3–60 chars) with no trailing punct.
_HEADING_RE = re.compile(r"^[A-Z][A-Z\s]{2,59}$")


def _parse_text_sections(text: str) -> list[dict]:
    """Conservative section parser for plain text.

    Flags ALL-CAPS short lines as headings (level 1). If no headings are
    found, returns a single section with heading="" and full text as body.
    """
    if not text:
        return [{"heading": "", "body": "", "level": 1}]

    lines = text.splitlines()
    sections: list[dict] = []
    current_heading = ""
    current_body_lines: list[str] = []

    def _flush() -> None:
        body = "\n".join(current_body_lines).strip()
        sections.append({"heading": current_heading, "body": body, "level": 1})

    for line in lines:
        stripped = line.strip()
        if stripped and _HEADING_RE.match(stripped):
            if current_body_lines or current_heading:
                _flush()
            current_heading = stripped
            current_body_lines = []
        else:
            current_body_lines.append(line)

    # Flush last section.
    if current_heading or current_body_lines:
        _flush()

    if not sections:
        return [{"heading": "", "body": text.strip(), "level": 1}]

    # If nothing was flagged as a heading, collapse into one section.
    if all(s["heading"] == "" for s in sections):
        return [{"heading": "", "body": text.strip(), "level": 1}]

    return sections
