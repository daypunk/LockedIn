"""Q&A interview engine.

Loads the per-domain question bank from
``plugins/lockedin/skills/lockedin/templates/<template>/questions.yaml``,
walks the sections respecting ``requires`` ordering, applies
``follow_up`` probes when conditions match, and returns a list of
``Entity`` objects with ``provenance="interview"``.

The engine is deterministic Python, not an LLM. The lockedin skill
calls it via Bash so the LLM side can wrap each prompt in a more
conversational form. Power users can also run it directly.

PyYAML is required and lives behind the ``lockedin[yaml]`` extra. The
import is lazy so importing ``lockedin.ingest.interview`` itself does
not require PyYAML.

Resumability (v1):
    After each validated answer, the engine atomically writes state to
    ``<vault>/.lockedin/interview-state.json``. If the file exists on
    the next ``run()`` call, answered questions are skipped and the
    interview continues from where it left off.

    Pause keywords: ``[pause]``, ``[stop]``, ``[exit]``, ``:pause``, ``:q``
    Skip keywords:  ``[skip]``, ``:skip``  (only for non-required questions)
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lockedin.ontology import EDGE_SCHEMAS, Entity

_DATE_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")

_PAUSE_KEYWORDS = frozenset({"[pause]", "[stop]", "[exit]", ":pause", ":q"})
_SKIP_KEYWORDS = frozenset({"[skip]", ":skip"})

_STATE_SCHEMA_VERSION = 1


# ---------------------------------------------------------------------------
# Vault / state-file helpers
# ---------------------------------------------------------------------------


def _vault_path() -> Path:
    """Resolve the user vault, honouring ``LOCKEDIN_VAULT`` env var."""
    raw = os.environ.get("LOCKEDIN_VAULT", "")
    if raw:
        return Path(raw).expanduser().resolve()
    return Path("~/Documents/LockedIn").expanduser()


def _state_path(vault: Path) -> Path:
    return vault / ".lockedin" / "interview-state.json"


def _ensure_state_dir(vault: Path) -> None:
    (vault / ".lockedin").mkdir(parents=True, exist_ok=True)


def _atomic_write(path: Path, data: dict[str, Any]) -> None:
    """Write *data* as JSON to *path* using a tmp → rename sequence."""
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.rename(path)


def _load_state(path: Path) -> dict[str, Any] | None:
    """Load state JSON. Returns None if file absent, {} if corrupt (with warning)."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        print(
            "lockedin: state file appears corrupt — starting fresh.",
            file=sys.stderr,
        )
        return {}


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# YAML helpers
# ---------------------------------------------------------------------------


def _yaml_load(path: Path) -> dict[str, Any]:
    """Load a YAML file. Raises a readable error if PyYAML is missing."""
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as exc:  # pragma: no cover — exercised on minimal install
        raise RuntimeError(
            "lockedin interview requires PyYAML. "
            "Install via `pip install lockedin[yaml]`."
        ) from exc
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _resolve_template(template: str) -> Path:
    """Find questions.yaml for a given template name.

    Search order:

    1. Plugin source path (when running from a checkout):
       ``plugins/lockedin/skills/lockedin/templates/<template>/questions.yaml``
    2. Installed skill path:
       ``~/.claude/skills/lockedin/templates/<template>/questions.yaml``
    """
    here = Path(__file__).resolve()
    # lockedin/ingest/interview.py → repo root is here.parent.parent.parent
    repo_root = here.parent.parent.parent
    candidates = [
        repo_root
        / "plugins"
        / "lockedin"
        / "skills"
        / "lockedin"
        / "templates"
        / template
        / "questions.yaml",
        Path.home()
        / ".claude"
        / "skills"
        / "lockedin"
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


# ---------------------------------------------------------------------------
# Validation / follow-up helpers
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Edge inference
# ---------------------------------------------------------------------------

# Predicates created by document ingest, not interview co-presence.
_SKIP_PREDICATES = frozenset({"mentions", "derived_from"})

# For multi-domain predicates, preferred source type when both are present.
# Key: predicate name, Value: (preferred_type, fallback_type)
_DOMAIN_PREFERENCE: dict[str, tuple[str, str]] = {
    "produced": ("project", "role"),
    "uses_skill": ("project", "role"),
    "covers": ("project", "meeting"),  # publication is also valid but rarer
    "made": ("person", "meeting"),
}


def _infer_edges(
    entities: dict[tuple[str, str], Entity],
    insertion_order: list[tuple[str, str]],
) -> None:
    """Infer ontology edges from entity co-presence in an interview session.

    Walks ``EDGE_SCHEMAS``, finds all (src, dst) pairs that satisfy the
    predicate's domain/range given the entities present, and appends
    edge dicts to ``src.links``.  Existing links on each entity are
    cleared first so repeated calls produce identical results
    (idempotent / recomputed from scratch).

    The ``insertion_order`` list controls which entity is chosen as
    source when a predicate allows multiple domain types (e.g.
    ``produced`` can come from a project or a role — we prefer the
    most-recently-created entity of the preferred type, falling back to
    the other type).

    Parameters
    ----------
    entities:
        Mapping of (entity_type, slug) → Entity as maintained by run().
    insertion_order:
        List of (entity_type, slug) keys in the order they were first
        created.  Used to pick the "most recent" source for multi-domain
        predicates.
    """
    # Clear existing inferred links so re-runs don't accumulate duplicates.
    for ent in entities.values():
        ent.links = []

    # Build convenience lookup: type → list of slugs (in insertion order)
    type_to_slugs: dict[str, list[str]] = {}
    for et, slug in insertion_order:
        if (et, slug) in entities:
            type_to_slugs.setdefault(et, []).append(slug)

    def _latest_slug_for_types(preferred: str, *fallbacks: str) -> str | None:
        """Return slug of the most-recently-created entity for the first
        type (in preference order) that has at least one entity."""
        for t in (preferred, *fallbacks):
            slugs = type_to_slugs.get(t)
            if slugs:
                return slugs[-1]  # last inserted = most recent
        return None

    for predicate, spec in EDGE_SCHEMAS.items():
        if predicate in _SKIP_PREDICATES:
            continue

        pref = _DOMAIN_PREFERENCE.get(predicate)

        if pref is not None:
            # Multi-domain predicate: pick one source entity.
            preferred_type, fallback_type = pref
            # Build the full ordered type list from the spec to respect all
            # domain members (e.g. "covers" has domain (meeting, project, publication))
            domain_types = list(spec.domain)
            # Move preferred to front, keep rest in spec order
            ordered = [preferred_type] + [t for t in domain_types if t != preferred_type]
            src_slug = _latest_slug_for_types(*ordered)
            if src_slug is None:
                continue
            # Find which type this slug belongs to
            src_type = next(
                et for et, sl in insertion_order if sl == src_slug and (et, sl) in entities
            )
            src_entity = entities[(src_type, src_slug)]

            for dst_type in spec.range:
                for dst_slug in type_to_slugs.get(dst_type, []):
                    edge = {"predicate": predicate, "object": dst_slug, "weight": 1.0}
                    if edge not in src_entity.links:
                        src_entity.links.append(edge)
        else:
            # Simple predicate: for each src/dst pair that matches domain×range
            for src_type in spec.domain:
                for src_slug in type_to_slugs.get(src_type, []):
                    src_entity = entities[(src_type, src_slug)]
                    for dst_type in spec.range:
                        for dst_slug in type_to_slugs.get(dst_type, []):
                            # Skip self-links
                            if src_slug == dst_slug and src_type == dst_type:
                                continue
                            edge = {
                                "predicate": predicate,
                                "object": dst_slug,
                                "weight": 1.0,
                            }
                            if edge not in src_entity.links:
                                src_entity.links.append(edge)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def run(
    template: str = "experience",
    non_interactive: bool = False,
    lang: str = "en",
    *,
    sections: list[str] | None = None,
    fresh: bool = False,
) -> list[Entity]:
    """Run the Q&A interview and return new Entity objects.

    Each returned entity carries ``provenance="interview"`` in its
    fields. The caller persists them via ``lockedin.storage.notes``.

    ``non_interactive=True`` is reserved for fixture-driven seeding
    (``lockedin init --fixture FILE``) and is rejected here.

    Parameters
    ----------
    template:
        Name of the question bank to load (default ``"experience"``).
    non_interactive:
        Rejected — use ``lockedin init --fixture FILE`` instead.
    lang:
        Language code for prompts (``"en"`` or ``"ko"``).
    sections:
        Optional allowlist of section names. When provided, only
        questions in matching sections are asked; state for other
        sections is preserved untouched.
    fresh:
        When ``True``, any existing state file is deleted before
        starting, forcing a full restart.
    """
    if non_interactive:
        raise NotImplementedError(
            "Non-interactive interview not supported. "
            "Use `lockedin init --fixture FILE` for deterministic seeding."
        )

    config = _yaml_load(_resolve_template(template))

    # ------------------------------------------------------------------
    # State setup
    # ------------------------------------------------------------------
    vault = _vault_path()
    state_file = _state_path(vault)
    _ensure_state_dir(vault)

    if fresh and state_file.exists():
        state_file.unlink()

    raw_state = _load_state(state_file)

    # raw_state is None  → no file, start fresh
    # raw_state is {}    → corrupt file (warning already printed), start fresh
    # raw_state is dict  → valid state, potentially resumable

    # Check if previously completed
    if raw_state and raw_state.get("completed_at"):
        print("Interview complete. Start over? [y/N]")
        answer = _ask("> ").lower()
        if answer not in ("y", "yes"):
            return []
        raw_state = None
        if state_file.exists():
            state_file.unlink()

    prior_answers: dict[str, str] = {}
    if raw_state and raw_state.get("template") == template:
        prior_answers = raw_state.get("answers") or {}

    # Count total answerable questions for progress display
    all_sections = config.get("sections") or []
    total_questions = sum(
        len(sec.get("questions") or []) for sec in all_sections
    )
    total_sections = len(all_sections)

    # Print resume notice if we have prior answers
    if prior_answers:
        answered_count = len(prior_answers)
        # Find where we are
        cumulative = 0
        resume_section_idx = 0
        resume_q_idx = 0
        for s_idx, sec in enumerate(all_sections):
            sec_qs = sec.get("questions") or []
            for q_idx, q in enumerate(sec_qs):
                qid = q.get("id")
                if qid and qid not in prior_answers:
                    resume_section_idx = s_idx + 1
                    resume_q_idx = cumulative + q_idx + 1
                    break
                cumulative += 1
            else:
                continue
            break
        print(
            f"Resuming interview. {answered_count} of {total_questions} answered. "
            f"Continuing from Section {resume_section_idx}/{total_sections} "
            f"· Question {resume_q_idx}."
        )

    # Initialise state record
    started_at = (raw_state or {}).get("started_at") or _now_iso()
    state: dict[str, Any] = {
        "schema_version": _STATE_SCHEMA_VERSION,
        "template": template,
        "lang": lang,
        "started_at": started_at,
        "updated_at": _now_iso(),
        "answers": dict(prior_answers),
        "completed_at": None,
    }
    _atomic_write(state_file, state)

    answers: dict[str, str] = dict(prior_answers)

    # (entity_type, slug) → Entity
    entities: dict[tuple[str, str], Entity] = {}
    # entity_type → current slug of the "in-progress" instance for that type
    primary_slug: dict[str, str] = {}
    # ordered list of (entity_type, slug) keys in creation order
    insertion_order: list[tuple[str, str]] = []

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
        insertion_order.append((entity_type, new_slug))
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
                    # Update insertion_order entry for this entity
                    for i, (et, sl) in enumerate(insertion_order):
                        if et == ent.type and sl == ent.slug:
                            insertion_order[i] = (ent.type, new_slug)
                            break
                    ent.slug = new_slug
                    ent.title = value
                    entities[(ent.type, new_slug)] = ent
                    primary_slug[ent.type] = new_slug
                break

    # ------------------------------------------------------------------
    # Replay prior answers into entity graph so entities are populated
    # ------------------------------------------------------------------
    for sec in all_sections:
        for question in sec.get("questions") or []:
            qid = question.get("id")
            if not qid or qid not in prior_answers:
                continue
            prior_ans = prior_answers[qid]
            writes = question.get("writes") or {}
            target_type = writes.get("entity")
            target_field = writes.get("field")
            if target_type and target_field and prior_ans:
                ent = _get_entity(target_type)
                ent.fields[target_field] = prior_ans
                if target_field in ("name", "title", "headline", "institution"):
                    _finalize_slug(ent)

    # ------------------------------------------------------------------
    # Walk sections
    # ------------------------------------------------------------------
    cumulative_q_idx = 0
    paused = False

    for s_idx, section in enumerate(all_sections):
        section_name = section.get("name", "")
        section_questions = section.get("questions") or []
        section_number = s_idx + 1

        # Section filter: if caller passed sections=[], skip non-matching
        if sections is not None and section_name not in sections:
            cumulative_q_idx += len(section_questions)
            continue

        for q_local_idx, question in enumerate(section_questions):
            q_number = cumulative_q_idx + q_local_idx + 1
            qid = question.get("id")
            if not qid:
                continue

            # Already answered in a prior session — skip silently
            if qid in prior_answers:
                continue

            # Skip if any required prerequisite is unanswered.
            requires = question.get("requires") or []
            if not all(req in answers for req in requires):
                continue

            # Progress banner
            print(
                f"\n[Section {section_number}/{total_sections} · Q {q_number}/{total_questions}]"
            )

            # Pick prompt text in the requested language.
            prompt = (
                question.get("text_ko")
                if lang == "ko" and "text_ko" in question
                else question.get("text", "(no prompt)")
            )
            print(f"{prompt}")
            answer = _ask("> ")

            # Pause check
            if answer.lower() in _PAUSE_KEYWORDS:
                print("Paused. Resume any time with the same command.")
                paused = True
                break

            rule = question.get("validate")
            is_required = rule in ("required", "non_empty")

            # Skip check
            if answer.lower() in _SKIP_KEYWORDS:
                if is_required:
                    print(
                        "This question is required — try again or type [pause] to come back later."
                    )
                    # Re-prompt once
                    answer = _ask("> ")
                    if answer.lower() in _PAUSE_KEYWORDS:
                        print("Paused. Resume any time with the same command.")
                        paused = True
                        break
                    if answer.lower() in _SKIP_KEYWORDS:
                        # Still skipping required — treat as pause
                        print("Paused. Resume any time with the same command.")
                        paused = True
                        break
                else:
                    # Optional question — record as skipped (empty), move on
                    answers[qid] = ""
                    state["answers"] = dict(answers)
                    state["updated_at"] = _now_iso()
                    _atomic_write(state_file, state)
                    continue

            # Validate. Allow one retry on failure, then skip.
            passes, err = _validate_answer(rule, answer)
            if not passes:
                print(f"  (invalid: {err}) Trying once more.")
                answer = _ask("> ")
                if answer.lower() in _PAUSE_KEYWORDS:
                    print("Paused. Resume any time with the same command.")
                    paused = True
                    break
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
                        if fup_answer.lower() in _PAUSE_KEYWORDS:
                            print("Paused. Resume any time with the same command.")
                            paused = True
                            break
                        if fup_answer:
                            answer = f"{answer}\n{fup_answer}"
                if paused:
                    break

            if paused:
                break

            answers[qid] = answer

            # Persist state atomically after each validated answer
            state["answers"] = dict(answers)
            state["updated_at"] = _now_iso()
            _atomic_write(state_file, state)

            # Apply write to the appropriate entity.
            writes = question.get("writes") or {}
            target_type = writes.get("entity")
            target_field = writes.get("field")
            if target_type and target_field:
                ent = _get_entity(target_type)
                ent.fields[target_field] = answer
                if target_field in ("name", "title", "headline", "institution"):
                    _finalize_slug(ent)

        if paused:
            break

        cumulative_q_idx += len(section_questions)

    # ------------------------------------------------------------------
    # Edge inference
    # ------------------------------------------------------------------
    if not paused:
        _infer_edges(entities, insertion_order)

    # ------------------------------------------------------------------
    # Completion / cleanup
    # ------------------------------------------------------------------
    if not paused:
        state["completed_at"] = _now_iso()
        state["updated_at"] = _now_iso()
        _atomic_write(state_file, state)
        # Guarantee the master view at <vault>/EXPERIENCE.md is current.
        # Individual write_entity calls already refresh it, but completing
        # an interview is a natural sync point — ensures the file matches
        # the final vault state even if writes were skipped or batched.
        try:
            from lockedin.render.master_view import refresh_master_view

            refresh_master_view(str(vault))
        except Exception:  # noqa: BLE001 — refresh is a polish, never crash interview
            pass
        # Next-steps guidance — F8 from the UX audit: vault is seeded,
        # tell the user what to try.
        entity_count = len(entities)
        print()
        print(f"Interview complete. {entity_count} entities saved to your vault.")
        print(
            "Try next: /lockedin render resume | render jaso | "
            "render interview | render ideas"
        )
        print(f"Or open {vault}/EXPERIENCE.md to see what you've captured.")

    return list(entities.values())
