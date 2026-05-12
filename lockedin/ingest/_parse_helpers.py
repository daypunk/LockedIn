"""Shared regex helpers for the ingest parse modules.

All functions are pure stdlib, deterministic, and never raise.
They are designed for *grounding hints* — high-recall is NOT the goal.
It is preferable to return an empty list than to invent facts.
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Date patterns
# ---------------------------------------------------------------------------

# Individual sub-patterns ordered from most-specific to least-specific so
# that a longer match is consumed before the fallback bare-YYYY fires.
_DATE_RE = re.compile(
    r"""
    (?:
        \d{4}-\d{2}-\d{2}           # YYYY-MM-DD
      | \d{4}-\d{2}(?!\d)           # YYYY-MM  (not followed by digit)
      | (?:January|February|March|April|May|June|July|August
          |September|October|November|December
          |Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)
        \s+\d{4}                    # Month-name YYYY
      | \d{4}년\s*\d{1,2}월?        # Korean YYYY년 MM월
      | \b\d{4}\b                   # bare YYYY (last resort)
    )
    """,
    re.VERBOSE | re.UNICODE,
)


def _find_dates(text: str) -> list[str]:
    """Return deduplicated date-like strings from text. Never raises."""
    try:
        seen: list[str] = []
        seen_set: set[str] = set()
        for m in _DATE_RE.finditer(text):
            val = m.group(0).strip()
            if val not in seen_set:
                seen_set.add(val)
                seen.append(val)
        return seen
    except Exception:  # noqa: BLE001
        return []


# ---------------------------------------------------------------------------
# URL patterns
# ---------------------------------------------------------------------------

_URL_RE = re.compile(r"https?://[^\s\"'<>)\]]+")


def _find_urls(text: str) -> list[str]:
    """Return deduplicated HTTP/HTTPS URLs found in text. Never raises."""
    try:
        seen: list[str] = []
        seen_set: set[str] = set()
        for m in _URL_RE.finditer(text):
            val = m.group(0).rstrip(".,;:!?")
            if val not in seen_set:
                seen_set.add(val)
                seen.append(val)
        return seen
    except Exception:  # noqa: BLE001
        return []


# ---------------------------------------------------------------------------
# Email patterns
# ---------------------------------------------------------------------------

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")


def _find_emails(text: str) -> list[str]:
    """Return deduplicated email addresses found in text. Never raises."""
    try:
        seen: list[str] = []
        seen_set: set[str] = set()
        for m in _EMAIL_RE.finditer(text):
            val = m.group(0)
            if val not in seen_set:
                seen_set.add(val)
                seen.append(val)
        return seen
    except Exception:  # noqa: BLE001
        return []


# ---------------------------------------------------------------------------
# Candidate org heuristics
# ---------------------------------------------------------------------------

# Corporate suffix anywhere in a line — capture the full line for high-precision
# candidates.  We strip later.
_ORG_SUFFIX_RE = re.compile(
    r"[A-Z][^\n]{1,79}(?:Inc\.?|Ltd\.?|LLC|Corp\.?|GmbH|S\.A\.|주식회사|유한회사)[^\n]{0,20}",
    re.UNICODE,
)

# Capitalized multi-word phrase: 2–4 consecutive Title-case words.
# We count occurrences and only include those that appear 2+ times.
_CAP_PHRASE_RE = re.compile(
    r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}",
    re.UNICODE,
)

# Words to exclude from candidate orgs (common proper nouns that aren't orgs).
_ORG_STOP_WORDS: frozenset[str] = frozenset(
    {
        "January", "February", "March", "April", "June", "July", "August",
        "September", "October", "November", "December",
        "Jan Feb", "Feb Mar",
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
        "New York", "San Francisco", "Los Angeles", "South Korea",
        "Work Experience", "Work History",
    }
)


def _find_candidate_orgs(text: str) -> list[str]:
    """Return deduplicated phrases that heuristically look like org names.

    Conservative by design: false negatives are acceptable; false positives
    that invent facts are not. Never raises.
    """
    try:
        seen: list[str] = []
        seen_set: set[str] = set()

        def _add(val: str) -> None:
            val = val.strip().rstrip(".,;:")
            if val and val not in seen_set and val not in _ORG_STOP_WORDS:
                seen_set.add(val)
                seen.append(val)

        # Org-suffix lines — high precision: grab the phrase up to and including
        # the suffix token.
        for m in _ORG_SUFFIX_RE.finditer(text):
            # Extract just up to the suffix word to avoid trailing context.
            line = m.group(0).strip()
            # Find the last occurrence of any suffix in the matched string and
            # trim to include it.
            suffix_match = re.search(
                r"(Inc\.?|Ltd\.?|LLC|Corp\.?|GmbH|S\.A\.|주식회사|유한회사)",
                line,
            )
            if suffix_match:
                candidate = line[: suffix_match.end()].strip()
                _add(candidate)

        # Capitalized multi-word phrases — require 2+ occurrences to reduce noise.
        phrase_counts: dict[str, int] = {}
        for m in _CAP_PHRASE_RE.finditer(text):
            phrase = m.group(0).strip()
            if phrase not in _ORG_STOP_WORDS:
                phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
        for phrase, count in phrase_counts.items():
            if count >= 2:
                _add(phrase)

        return seen
    except Exception:  # noqa: BLE001
        return []
