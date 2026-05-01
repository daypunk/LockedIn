"""selfgraph ingest <path> --dry-run — parse documents and report.

Pure-CLI utility. Walks the given path, picks readers for each supported
extension (`.md`, `.txt`, `.pdf`, `.docx`), and prints a summary report.
**No vault writes**, no LLM calls, no ambiguity resolution. The smart
ingest path that resolves ambiguities and merges into the ontology lives
in the skill (host AI asks the user).
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path


def _read_text_file(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _read_pdf(path: Path) -> str | None:
    try:
        from pypdf import PdfReader  # type: ignore[import-not-found]
    except ImportError:
        return None
    try:
        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception:  # pragma: no cover  # noqa: BLE001
        return None


def _read_docx(path: Path) -> str | None:
    try:
        import docx  # type: ignore[import-not-found]  # python-docx
    except ImportError:
        return None
    try:
        document = docx.Document(str(path))
        return "\n".join(p.text for p in document.paragraphs)
    except Exception:  # pragma: no cover  # noqa: BLE001
        return None


READERS: dict[str, Callable[[Path], str | None]] = {
    ".md": _read_text_file,
    ".markdown": _read_text_file,
    ".txt": _read_text_file,
    ".pdf": _read_pdf,
    ".docx": _read_docx,
}


def _walk(path: Path) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix.lower() in READERS else []
    return [
        p
        for p in sorted(path.rglob("*"))
        if p.is_file() and p.suffix.lower() in READERS and not p.name.startswith(".")
    ]


def ingest_dry_run(path_arg: str, *, domain: str = "career") -> int:
    path = Path(path_arg).expanduser()
    if not path.exists():
        print(f"path not found: {path}")
        return 1

    files = _walk(path)
    print("# selfgraph ingest --dry-run")
    print(f"# scanned: {path}")
    print(f"# domain : {domain}")
    print()

    if not files:
        print("(no supported files: .md / .markdown / .txt / .pdf / .docx)")
        return 0

    parsed: list[dict] = []
    skipped: list[tuple[Path, str]] = []

    for f in files:
        suffix = f.suffix.lower()
        reader = READERS[suffix]
        text = reader(f)
        if text is None:
            reason = "missing optional dep" if suffix in (".pdf", ".docx") else "read error"
            skipped.append((f, reason))
            continue
        parsed.append(
            {
                "path": f,
                "format": suffix,
                "chars": len(text),
                "lines": text.count("\n") + (1 if text and not text.endswith("\n") else 0),
                "first_line": text.split("\n", 1)[0][:80] if text else "",
            }
        )

    print(f"## parsed: {len(parsed)}")
    for item in parsed:
        print(f"  {item['path']}")
        print(f"    format={item['format']}  chars={item['chars']}  lines={item['lines']}")
        if item["first_line"]:
            print(f"    first: {item['first_line']!r}")

    if skipped:
        print()
        print(f"## skipped: {len(skipped)}")
        for path_, reason in skipped:
            print(f"  {path_}  ({reason})")
        if any(reason == "missing optional dep" for _, reason in skipped):
            print('  hint: pip install "selfgraph[pdf,docx]"')

    print()
    print("# next: this was a dry-run. To merge into the vault and resolve")
    print("# ambiguities, run inside Claude Code:")
    print(f"#   /selfgraph ingest {path_arg} --domain {domain}")
    return 0
