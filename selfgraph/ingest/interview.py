"""Q&A interview engine.

Stub for Phase 1 step 9. The interview is stdlib-only and reads its question
bank from `selfgraph/skill/templates/<domain>/questions.yaml`. Output is a
list of `Entity` instances that the caller persists via storage.notes.
"""

from __future__ import annotations

from selfgraph.ontology import Entity


def run(template: str = "career", non_interactive: bool = False) -> list[Entity]:
    raise NotImplementedError("ingest.interview.run: implement in Phase 1 step 9")
