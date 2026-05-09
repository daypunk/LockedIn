"""Ingest .md documents into the ontology (Phase 2 step 11)."""

from __future__ import annotations

from pathlib import Path


def ingest(path: Path, domain: str = "career") -> dict:
    raise NotImplementedError("ingest.markdown.ingest: implement in Phase 2 step 11")
