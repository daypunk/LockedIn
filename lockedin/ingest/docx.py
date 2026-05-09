"""Ingest .docx (Word) documents into the ontology.

Optional dependency: `pip install lockedin[docx]` (python-docx).
"""

from __future__ import annotations

from pathlib import Path


def ingest(path: Path, domain: str = "career") -> dict:
    raise NotImplementedError("ingest.docx.ingest: implement in document ingestion layer")
