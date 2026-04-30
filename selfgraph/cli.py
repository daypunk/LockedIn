"""selfgraph CLI entry point.

Two execution surfaces, deliberately separated:

* **Pure CLI utilities** (deterministic, run anywhere — no LLM, no
  subscription needed): `install`, `doctor`, `validate`, `template`,
  `render graph`, `init --non-interactive --fixture FILE`,
  `ingest --dry-run`.

* **Claude Code skill commands** (need an LLM in the loop, run inside
  Claude Code on the user's existing subscription): interactive `init`,
  smart `ingest`, `render jaso/resume/portfolio`, `query`.

When a skill-only subcommand is invoked from a plain terminal, the CLI
prints a short pointer explaining how to invoke it inside Claude Code,
then exits with code 3 (distinct from 2 = "not yet implemented").
"""

from __future__ import annotations

import argparse
import sys

from selfgraph import __version__

SKILL_REDIRECT_EXIT = 3

_REDIRECT_TEMPLATE = """\
selfgraph: '{cmd}' runs inside Claude Code — the skill drives the LLM
side, your subscription pays for the reasoning.

Open Claude Code in this directory and run:

    /selfgraph {invocation}

Or use natural language. Examples:
    "내 경력 정리해줘"          → /selfgraph init
    "이 PDF 흡수해줘"           → /selfgraph ingest <path>
    "자소서 1번 문항 써줘"      → /selfgraph render jaso

Pure-CLI alternatives that work outside Claude Code (no LLM):
    selfgraph render graph                                # graph.html
    selfgraph init --non-interactive --fixture seed.yaml  # deterministic seed
    selfgraph ingest <path> --dry-run                     # diff preview only
    selfgraph validate                                    # check vault schema
    selfgraph doctor                                      # diagnose runtime
    selfgraph install [--check|--upgrade|--uninstall]     # skill registration
"""


def _redirect(cmd: str, invocation: str | None = None) -> int:
    print(_REDIRECT_TEMPLATE.format(cmd=cmd, invocation=invocation or cmd))
    return SKILL_REDIRECT_EXIT


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="selfgraph",
        description=(
            "Your experience as a knowledge graph. Claude Code-native. "
            "Most user-facing flows run inside Claude Code as a skill; the "
            "subcommands below marked (CLI) work in any terminal."
        ),
    )
    parser.add_argument("--version", action="version", version=f"selfgraph {__version__}")
    sub = parser.add_subparsers(dest="cmd", metavar="<subcommand>")

    # ── skill-driven (with deterministic-flag escape hatches) ───────────────
    p_init = sub.add_parser(
        "init",
        help="Q&A interview to seed the ontology (skill). With --non-interactive --fixture: deterministic CLI seed.",
    )
    p_init.add_argument("--lang", choices=["en", "ko"], default="en")
    p_init.add_argument("--non-interactive", action="store_true")
    p_init.add_argument("--fixture", help="YAML fixture (deterministic CLI path)")
    p_init.add_argument("--vault", help="vault path (default ~/.selfgraph/)")

    p_ingest = sub.add_parser(
        "ingest",
        help="parse documents into the ontology (skill). With --dry-run: deterministic diff.",
    )
    p_ingest.add_argument("path", help="file or directory to ingest")
    p_ingest.add_argument("--domain", default="career")
    p_ingest.add_argument("--dry-run", action="store_true")

    p_render = sub.add_parser(
        "render",
        help="render an artifact. graph: deterministic CLI. jaso/resume/portfolio: skill.",
    )
    p_render.add_argument("kind", choices=["jaso", "resume", "portfolio", "graph"])
    p_render.add_argument("--target", help="renderer profile (e.g. us-tech-senior)")
    p_render.add_argument("--company", help="company name (jaso only)")
    p_render.add_argument("--question", help="question id or text (jaso only)")
    p_render.add_argument("--self-evaluate", action="store_true")

    p_query = sub.add_parser("query", help="natural-language graph query (skill).")
    p_query.add_argument("text")

    # ── pure CLI utilities (deterministic) ──────────────────────────────────
    p_template = sub.add_parser("template", help="(CLI) manage ontology templates")
    p_template.add_argument("action", choices=["list", "add", "remove"])
    p_template.add_argument("name", nargs="?")

    p_install = sub.add_parser("install", help="(CLI) register skill files into Claude Code")
    grp = p_install.add_mutually_exclusive_group()
    grp.add_argument("--auto-register", action="store_true")
    grp.add_argument("--upgrade", action="store_true")
    grp.add_argument("--uninstall", action="store_true")
    grp.add_argument("--check", action="store_true")
    grp.add_argument("--setup-hud", action="store_true",
                     help="wire selfgraph HUD into Claude Code's statusLine")
    grp.add_argument("--remove-hud", action="store_true",
                     help="undo --setup-hud (restore previous statusLine)")
    p_install.add_argument("--target")
    p_install.add_argument("--force", action="store_true")

    sub.add_parser("doctor", help="(CLI) print runtime / skill / key state")

    p_validate = sub.add_parser("validate", help="(CLI) check vault against schema")
    p_validate.add_argument("--vault")

    p_hud = sub.add_parser(
        "hud",
        help="(CLI) emit a one-line statusLine snippet for Claude Code",
    )
    p_hud.add_argument("--color", action="store_true")
    p_hud.add_argument("--no-color", action="store_true")
    p_hud.add_argument("--vault")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.cmd is None:
        parser.print_help()
        return 0

    # init: deterministic when --fixture is given (non-interactive implied)
    if args.cmd == "init":
        if args.fixture:
            from selfgraph.commands.init import init_from_fixture
            return init_from_fixture(args.fixture, args.vault, lang=args.lang)
        if args.non_interactive:
            print("--non-interactive requires --fixture FILE", file=sys.stderr)
            return 2
        return _redirect("init")

    # ingest: deterministic only with --dry-run
    if args.cmd == "ingest":
        if args.dry_run:
            from selfgraph.commands.ingest_dry import ingest_dry_run
            return ingest_dry_run(args.path, domain=args.domain)
        return _redirect("ingest", f"ingest {args.path}")

    # render: graph is deterministic; jaso/resume/portfolio need the skill
    if args.cmd == "render":
        if args.kind == "graph":
            from selfgraph.commands.render_graph import run_render_graph
            return run_render_graph(None)
        invocation_parts = ["render", args.kind]
        if args.target:
            invocation_parts += ["--target", args.target]
        if args.company:
            invocation_parts += ["--company", f'"{args.company}"']
        if args.question:
            invocation_parts += ["--question", str(args.question)]
        return _redirect("render", " ".join(invocation_parts))

    # query: skill only
    if args.cmd == "query":
        return _redirect("query", f'query "{args.text}"')

    # pure CLI commands (deterministic)
    if args.cmd == "doctor":
        from selfgraph.commands.doctor import run_doctor
        return run_doctor()

    if args.cmd == "validate":
        from selfgraph.commands.validate import validate
        return validate(args.vault)

    if args.cmd == "install":
        from selfgraph.commands.install import (
            install_auto_register,
            install_check,
            install_remove_hud,
            install_setup_hud,
            install_uninstall,
            install_upgrade,
        )
        if args.check:
            return install_check(args.target)
        if args.upgrade:
            return install_upgrade(args.target, force=args.force)
        if args.uninstall:
            return install_uninstall(args.target)
        if args.setup_hud:
            return install_setup_hud(args.target, force=args.force)
        if args.remove_hud:
            return install_remove_hud(args.target)
        if args.auto_register:
            return install_auto_register(args.target, force=args.force)
        return install_check(args.target)

    if args.cmd == "template":
        from selfgraph.commands.template import template
        return template(args.action, args.name)

    if args.cmd == "hud":
        from selfgraph.commands.hud import hud
        hud_argv: list[str] = []
        if args.color:
            hud_argv.append("--color")
        if args.no_color:
            hud_argv.append("--no-color")
        if args.vault:
            hud_argv += ["--vault", args.vault]
        return hud(hud_argv)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
