"""Command-line interface for DraftSmith."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from draftsmith import __version__
from draftsmith.brief import Brief, BriefError
from draftsmith.draft import render_draft
from draftsmith.editorial import analyze
from draftsmith.outline import build_outline, total_words

SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}


def _build(args: argparse.Namespace) -> int:
    brief = Brief.from_toml(args.brief)
    sections = build_outline(brief)
    draft = render_draft(brief, sections)
    if args.out:
        Path(args.out).write_text(draft, encoding="utf-8")
        print(
            f"wrote {args.out} ({total_words(sections)} words budgeted across {len(sections)} sections)"
        )
    else:
        print(draft)
    return 0


def _lint(args: argparse.Namespace) -> int:
    markdown = Path(args.file).read_text(encoding="utf-8")
    report = analyze(markdown, keyword=args.keyword)
    issues = sorted(report.issues, key=lambda issue: SEVERITY_ORDER.get(issue.severity, 9))
    if not issues:
        print("no issues found")
    for issue in issues:
        print(f"{issue.severity:<7} {issue.rule:<18} {issue.message}")
    print(
        f"\n{len(report.errors)} error(s), {len(report.issues) - len(report.errors)} warning(s)"
        f" · score {report.score}/100"
    )
    return 0 if report.passed else 1


def _score(args: argparse.Namespace) -> int:
    markdown = Path(args.file).read_text(encoding="utf-8")
    print(json.dumps(analyze(markdown, keyword=args.keyword).as_dict(), indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="draftsmith",
        description="Turn a TOML brief into a structured blog draft, then lint it.",
    )
    parser.add_argument("--version", action="version", version=f"draftsmith {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="render a draft skeleton from a brief")
    build.add_argument("brief", help="path to a brief .toml file")
    build.add_argument("-o", "--out", help="write markdown to this file instead of stdout")
    build.set_defaults(func=_build)

    lint = sub.add_parser("lint", help="check an existing draft")
    lint.add_argument("file", help="markdown file to review")
    lint.add_argument("--keyword", help="primary keyword to verify")
    lint.set_defaults(func=_lint)

    score = sub.add_parser("score", help="print metrics as JSON")
    score.add_argument("file")
    score.add_argument("--keyword")
    score.set_defaults(func=_score)
    return parser


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except BriefError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"error: file not found: {exc.filename}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
