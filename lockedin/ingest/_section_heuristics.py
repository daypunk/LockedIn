"""Shared section-parsing heuristics for non-structured formats (PDF, DOCX).

Uses a conservative approach: ALL-CAPS short lines or lines with no
trailing punctuation and short length are flagged as potential headings.
If uncertain, returns a single section with heading="" and full text.
"""

from __future__ import annotations

import re

# ALL-CAPS line: 3–60 characters, no trailing punctuation.
_ALLCAPS_RE = re.compile(r"^[A-Z][A-Z\s]{2,59}$")

# Short line (<=60 chars) ending without sentence-terminal punctuation.
# Must have at least 3 characters and no lowercase in it OR be title-cased.
_SHORT_TITLELIKE_RE = re.compile(r"^[A-Z][^\n]{2,59}$")
_TRAILING_PUNCT_RE = re.compile(r"[.!?,;:]\s*$")


def _looks_like_heading(line: str) -> bool:
    stripped = line.strip()
    if not stripped or len(stripped) < 3 or len(stripped) > 60:
        return False
    # ALL-CAPS short line: high confidence.
    if _ALLCAPS_RE.match(stripped):
        return True
    # Short line, no trailing punctuation, starts with capital: moderate confidence.
    return bool(
        _SHORT_TITLELIKE_RE.match(stripped)
        and not _TRAILING_PUNCT_RE.search(stripped)
        and stripped[0].isupper()
    )


def parse_generic_sections(text: str) -> list[dict]:
    """Parse generic (PDF/DOCX) text into sections.

    Conservative: if no confident headings are found, returns a single
    section with heading="" and the full text as body (level 1).
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
        if _looks_like_heading(line):
            if current_body_lines or current_heading:
                _flush()
            current_heading = line.strip()
            current_body_lines = []
        else:
            current_body_lines.append(line)

    if current_heading or current_body_lines:
        _flush()

    if not sections:
        return [{"heading": "", "body": text.strip(), "level": 1}]

    # If everything landed in one heading-less blob, collapse.
    if all(s["heading"] == "" for s in sections):
        return [{"heading": "", "body": text.strip(), "level": 1}]

    return sections
