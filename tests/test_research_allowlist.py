"""
test_research_allowlist.py

CI lint: every URL cited in a skills/*/research-notes.md file must use a
host that is present in tests/research-allowlist.txt.

Three tests:
  - test_research_allowlist_is_well_formed     — file exists, >=10 entries, no empty
  - test_no_duplicate_hosts_in_allowlist       — no duplicate entries
  - test_all_cited_hosts_are_in_research_allowlist — the main lint
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

# ---- paths ----------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent
ALLOWLIST_FILE = REPO_ROOT / "tests" / "research-allowlist.txt"
SKILLS_DIR = REPO_ROOT / "plugins" / "lockedin" / "skills"

# ---- URL pattern ----------------------------------------------------------
# Match http(s) URLs; stop at whitespace, ), ], or common sentence-ending
# punctuation that is unlikely to be part of a URL.
_URL_RE = re.compile(r"https?://[^\s)\]]+")

# Characters that trail URLs due to surrounding markdown/prose punctuation.
_TRAILING_STRIP = ".,:;!?"


# ---- helpers ---------------------------------------------------------------

def _load_allowlist() -> list[str]:
    """Return the non-comment, non-blank entries from the allowlist file."""
    entries = []
    for line in ALLOWLIST_FILE.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            entries.append(stripped)
    return entries


def _normalise_host(hostname: str) -> str:
    """Lower-case and strip a leading 'www.' prefix."""
    hostname = hostname.lower()
    if hostname.startswith("www."):
        hostname = hostname[4:]
    return hostname


def _is_real_hostname(hostname: str) -> bool:
    """
    Return True only for hostnames that look like genuine domain names.
    Rejects format placeholders such as '...' that appear in citation
    template examples inside the research-notes.md format section.
    A real hostname must contain at least one letter.
    """
    return bool(re.search(r"[a-zA-Z]", hostname))


def _extract_cited_urls(notes_file: Path) -> list[tuple[int, str]]:
    """
    Return a list of (line_number, url) pairs found in *notes_file*.
    Line numbers are 1-based. URLs are stripped of trailing punctuation.
    """
    results = []
    for lineno, line in enumerate(
        notes_file.read_text(encoding="utf-8").splitlines(), start=1
    ):
        for raw_url in _URL_RE.findall(line):
            url = raw_url.rstrip(_TRAILING_STRIP)
            results.append((lineno, url))
    return results


# ---- tests -----------------------------------------------------------------


def test_research_allowlist_is_well_formed():
    """The allowlist file must exist and contain at least 10 host entries."""
    assert ALLOWLIST_FILE.exists(), (
        f"Allowlist file not found: {ALLOWLIST_FILE}"
    )
    entries = _load_allowlist()
    assert len(entries) >= 10, (
        f"Allowlist has only {len(entries)} entries — "
        "expected at least 10 (sanity guard against accidental wipeout)."
    )
    empty = [e for e in entries if not e.strip()]
    assert not empty, f"Allowlist contains empty/blank entries: {empty!r}"


def test_no_duplicate_hosts_in_allowlist():
    """No host should appear more than once in the allowlist."""
    entries = _load_allowlist()
    seen: set[str] = set()
    dupes: list[str] = []
    for entry in entries:
        if entry in seen:
            dupes.append(entry)
        seen.add(entry)
    assert not dupes, (
        f"Duplicate entries in {ALLOWLIST_FILE.name}: {dupes!r}. "
        "Remove the extra copies."
    )


def test_all_cited_hosts_are_in_research_allowlist():
    """
    Every URL cited in any skills/*/research-notes.md must use a host
    that is present in tests/research-allowlist.txt.
    """
    allowed: set[str] = set(_load_allowlist())

    notes_files = sorted(SKILLS_DIR.glob("*/research-notes.md"))
    assert notes_files, (
        f"No research-notes.md files found under {SKILLS_DIR}. "
        "Check that SKILLS_DIR is correct."
    )

    violations: list[str] = []

    for notes_file in notes_files:
        for lineno, url in _extract_cited_urls(notes_file):
            hostname = urlparse(url).hostname
            if hostname is None:
                continue
            if not _is_real_hostname(hostname):
                continue
            normalised = _normalise_host(hostname)
            if normalised not in allowed:
                violations.append(
                    f"  host={repr(normalised):<40s}  file={notes_file.relative_to(REPO_ROOT)}:{lineno}  url={url}"
                )

    assert not violations, (
        "The following URLs cite hosts NOT in tests/research-allowlist.txt:\n"
        + "\n".join(violations)
        + "\n\nEither add the host to tests/research-allowlist.txt "
        "(if it is a trustworthy source) or remove the citation."
    )
