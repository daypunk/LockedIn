"""Ingest .pdf documents into the ontology (Phase 2 step 11).

Optional dependency: `pip install lockedin[pdf]` (pypdf). On failure, fall
back to pdfminer.six per R5 mitigation.
"""

from __future__ import annotations

from pathlib import Path


def ingest(path: Path, domain: str = "career") -> dict:
    raise NotImplementedError("ingest.pdf.ingest: implement in Phase 2 step 11")
