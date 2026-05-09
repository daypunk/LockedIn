"""Q&A interview engine.

Loads the per-domain question bank from
``plugins/selfgraph/skills/selfgraph/templates/<template>/questions.yaml``,
walks the sections respecting ``requires`` ordering, applies
``follow_up`` probes when conditions match, and returns a list of
``Entity`` objects with ``provenance="interview"``.

The engine is deterministic Python, not an LLM. The selfgraph skill
calls it via Bash so the LLM side can wrap each prompt in a more
conversational form. Power users can also run it directly.

PyYAML is required and lives behind the ``selfgraph[yaml]`` extra. The
import is lazy so importing ``selfgraph.ingest.interview`` itself does
not require PyYAML.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from selfgraph.ontology import Entity

_DATE_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")


def _yaml_load(path: Path) -> dict[str, Any]:
    """Load a YAML file. Raises a readable error if PyYAML is missing."""
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as exc:  # pragma: no cover — exercised on minimal install
        raise RuntimeError(
            "selfgraph interview requires PyYAML. "
            "Install via `pip install selfgraph[yaml]`."
        ) from exc
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _resolve_template(template: str) -> Path:
    """Find questions.yaml for a given template name.

    Search order:

    1. Plugin source path (when running from a checkout):
       ``plugins/selfgraph/skills/selfgraph/templates/<template>/questions.yaml``
    2. Installed skill path:
       ``~/.claude/skills/selfgraph/templates/<template>/questions.yaml``
    """
    here = Path(__file__).resolve()
    # selfgraph/ingest/interview.py → repo root is here.parent.parent.parent
    repo_root = here.parent.parent.parent
    candidates = [
        repo_root
        / "plugins"
        / "selfgraph"
        / "skills"
        / "selfgraph"
        / "templates"
        / template
        / "questions.yaml",
        Path.home()
        / ".claude"
        / "skills"
        / "selfgraph"
        / "templates"
        / template
        / "questions.yaml",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"Template {template!r} not found. Searched: "
        + ", ".join(str(c) for c in candidates)
    )


def _validate_answer(rule: str | None, answer: str) -> tuple[bool, str]:
    """Return (passes, error_message). Rule is one of:
    required, non_empty, url, email, year, date, or None for permissive."""
    answer = (answer or "").strip()
    if not rule:
        return True, ""
    if rule in ("required", "non_empty"):
        return (len(answer) > 0, "An answer is required.")
    if rule == "url":
        return (
            answer.startswith(("http://", "https://")),
            "Should start with http:// or https://.",
        )
    if rule == "email":
        return ("@" in answer and "." in answer, "Looks malformed for an email.")
    if rule == "year":
        try:
            year = int(answer)
        except ValueError:
            return False, "Should be a four-digit year."
        return (1800 < year < 2200, "Year out of plausible range.")
    if rule == "date":
        return (
            bool(_DATE_RE.match(answer)),
            "Should be YYYY-MM-DD or YYYY-MM.",
        )
    return True, ""  # unknown rule: be permissive


def _check_follow_up_condition(condition: str, answer: str) -> bool:
    """Mini condition language. Supported:
    starts_with:<text>, contains:<text>, len_lt:<n>, len_gt:<n>.
    """
    if not condition or ":" not in condition:
        return False
    op, _, arg = condition.partition(":")
    answer = answer or ""
    try:
        if op == "starts_with":
            return answer.startswith(arg)
        if op == "contains":
            return arg in answer
        if op == "len_lt":
            return len(answer) < int(arg)
        if op == "len_gt":
            return len(answer) > int(arg)
    except (TypeError, ValueError):
        return False
    return False


def _slugify(text: str) -> str:
    """Best-effort slug from a free-form answer. Lowercase, dash-joined,
    capped at 64 chars, never empty."""
    cleaned = re.sub(r"[^\w\s-]", "", (text or "").strip().lower())
    cleaned = re.sub(r"[\s_]+", "-", cleaned).strip("-")
    return (cleaned or "unknown")[:64]


def _ask(prompt: str) -> str:
    """Wrap input() so tests can monkeypatch this single function."""
    return input(prompt).strip()


def run(
    template: str = "career",
    non_interactive: bool = False,
    lang: str = "en",
) -> list[Entity]:
    """Run the Q&A interview and return new Entity objects.

    Each returned entity carries ``provenance="interview"`` in its
    fields. The caller persists them via ``selfgraph.storage.notes``.

    ``non_interactive=True`` is reserved for fixture-driven seeding
    (``selfgraph init --fixture FILE``) and is rejected here.
    """
    if non_interactive:
        raise NotImplementedError(
            "Non-interactive interview not supported. "
            "Use `selfgraph init --fixture FILE` for deterministic seeding."
        )

    config = _yaml_load(_resolve_template(template))

    answers: dict[str, str] = {}
    # (entity_type, slug) → Entity
    entities: dict[tuple[str, str], Entity] = {}
    # entity_type → current slug of the "in-progress" instance for that type
    primary_slug: dict[str, str] = {}

    def _get_entity(entity_type: str) -> Entity:
        slug = primary_slug.get(entity_type)
        if slug and (entity_type, slug) in entities:
            return entities[(entity_type, slug)]
        new_slug = f"{entity_type}-pending"
        ent = Entity(
            type=entity_type,
            title=f"{entity_type} (pending)",
            slug=new_slug,
            fields={"provenance": "interview"},
        )
        primary_slug[entity_type] = new_slug
        entities[(entity_type, new_slug)] = ent
        return ent

    def _finalize_slug(ent: Entity) -> None:
        for naming_field in ("name", "title", "headline", "institution"):
            if naming_field in ent.fields and ent.fields[naming_field]:
                value = str(ent.fields[naming_field])
                new_slug = _slugify(value)
                if new_slug != ent.slug:
                    old_key = (ent.type, ent.slug)
                    if old_key in entities:
                        del entities[old_key]
                    ent.slug = new_slug
                    ent.title = value
                    entities[(ent.type, new_slug)] = ent
                    primary_slug[ent.type] = new_slug
                break

    sections = config.get("sections") or []
    for section in sections:
        section_questions = section.get("questions") or []
        for question in section_questions:
            qid = question.get("id")
            if not qid:
                continue

            # Skip if any required prerequisite is unanswered.
            requires = question.get("requires") or []
            if not all(req in answers for req in requires):
                continue

            # Pick prompt text in the requested language.
            prompt = (
                question.get("text_ko")
                if lang == "ko" and "text_ko" in question
                else question.get("text", "(no prompt)")
            )
            print(f"\n{prompt}")
            answer = _ask("> ")

            # Validate. Allow one retry on failure, then skip.
            rule = question.get("validate")
            passes, err = _validate_answer(rule, answer)
            if not passes:
                print(f"  (invalid: {err}) Trying once more.")
                answer = _ask("> ")
                passes, err = _validate_answer(rule, answer)
                if not passes:
                    print(f"  (still invalid: {err}) Skipping.")
                    continue

            # Follow-up probes.
            for fup in question.get("follow_up") or []:
                if _check_follow_up_condition(fup.get("if", ""), answer):
                    fup_prompt = (
                        fup.get("text_ko")
                        if lang == "ko" and "text_ko" in fup
                        else fup.get("text", "")
                    )
                    if fup_prompt:
                        print(f"  {fup_prompt}")
                        fup_answer = _ask("> ")
                        if fup_answer:
                            answer = f"{answer}\n{fup_answer}"

            answers[qid] = answer

            # Apply write to the appropriate entity.
            writes = question.get("writes") or {}
            target_type = writes.get("entity")
            target_field = writes.get("field")
            if target_type and target_field:
                ent = _get_entity(target_type)
                ent.fields[target_field] = answer
                if target_field in ("name", "title", "headline", "institution"):
                    _finalize_slug(ent)

    return list(entities.values())
