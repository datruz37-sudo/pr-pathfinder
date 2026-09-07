"""Command-line interface for pr-pathfinder."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pr_pathfinder import __version__
from pr_pathfinder.baseline import load_baseline, write_baseline
from pr_pathfinder.config import load_config
from pr_pathfinder.models import Severity
from pr_pathfinder.reporters import render_json, render_markdown, render_sarif, render_text
from pr_pathfinder.rules import builtin_rules
from pr_pathfinder.scanner import scan_repository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pr-pathfinder",
        description="Find friction in a repository's first-contributor journey.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check = subparsers.add_parser("check", help="scan a local repository")
    check.add_argument("path", nargs="?", default=".", help="repository path (default: current)")
    check.add_argument(
        "--format",
        choices=("text", "json", "markdown", "sarif"),
        default="text",
        help="report format",
    )
    check.add_argument(
        "--fail-on",
        choices=("none", "info", "warning", "error"),
        default="error",
        help="lowest finding severity that returns exit code 1",
    )
    check.add_argument(
        "--baseline",
        metavar="FILE",
        default=None,
        help="report only findings not recorded in a baseline file",
    )
    check.add_argument(
        "--write-baseline",
        metavar="FILE",
        default=None,
        help="record current findings to a baseline file and exit 0",
    )

    subparsers.add_parser("rules", help="list built-in checks")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "rules":
        for rule in builtin_rules():
            print(f"{rule.rule_id}\t{rule.summary}")
        return 0

    try:
        # Parsed twice (scanner loads it again): tiny file, keeps a single source of truth
        # for validation while the scanner stays usable as a library.
        config = load_config(Path(args.path))
        for warning in config.warnings:
            print(f"warning: {warning}", file=sys.stderr)
        if args.write_baseline is not None:
            result = scan_repository(Path(args.path))
            write_baseline(Path(args.write_baseline), result.findings)
            print(f"Baseline written to {args.write_baseline}", file=sys.stderr)
            return 0
        known: frozenset[str] | None = None
        if args.baseline is not None:
            known = load_baseline(Path(args.baseline))
        result = scan_repository(Path(args.path), baseline=known)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))

    renderers = {
        "text": render_text,
        "json": render_json,
        "markdown": render_markdown,
        "sarif": render_sarif,
    }
    print(renderers[args.format](result))
    if args.fail_on == "none":
        return 0
    return int(result.should_fail(Severity.parse(args.fail_on)))


if __name__ == "__main__":
    sys.exit(main())
