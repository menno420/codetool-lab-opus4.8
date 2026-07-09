"""Command-line interface for mdverify."""

from __future__ import annotations

import argparse
import fnmatch
import glob
import sys
import time
from pathlib import Path

from . import __version__
from .config import load_config
from .errors import ConfigError, UsageError
from .parser import parse_blocks
from .report import report, should_color, summarize
from .runner import run_file

MD_EXTENSIONS = {".md", ".markdown"}
DEFAULT_IGNORE_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    "__pycache__",
}

_GLOB_CHARS = set("*?[")


def build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser."""
    parser = argparse.ArgumentParser(
        prog="mdverify",
        description="Verify runnable code blocks in Markdown files still work.",
        epilog="Exit codes: 0 = all passed, 1 = failures, 2 = usage/config error.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        metavar="PATH",
        help="files, directories, or globs to check (default: current directory)",
    )
    parser.add_argument(
        "-c",
        "--config",
        metavar="PATH",
        help="path to a config file (.mdverify.json, or a .toml/pyproject.toml on Python 3.11+)",
    )
    parser.add_argument(
        "--ignore",
        metavar="GLOB",
        action="append",
        default=[],
        help="ignore paths matching GLOB (repeatable)",
    )
    parser.add_argument(
        "--lang",
        metavar="LANG",
        action="append",
        default=[],
        help="only run blocks in LANG (repeatable)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        metavar="SECONDS",
        help="per-block timeout in seconds (default: 30, or config)",
    )
    parser.add_argument("--fail-fast", action="store_true", help="stop at the first failing block")
    parser.add_argument(
        "--require-runner",
        action="store_true",
        help="treat languages with no runner as failures instead of skips",
    )
    parser.add_argument(
        "--format",
        choices=["pretty", "plain", "json"],
        default="pretty",
        help="output format (default: pretty)",
    )
    parser.add_argument("--no-color", action="store_true", help="disable ANSI colour")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="show output of passing blocks"
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="only report failures and the summary"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_blocks",
        help="list discovered blocks without running them",
    )
    parser.add_argument("--version", action="version", version=f"mdverify {__version__}")
    return parser


def _is_ignored(path: Path, ignore_globs: list[str]) -> bool:
    if any(part in DEFAULT_IGNORE_DIRS for part in path.parts):
        return True
    text = str(path)
    return any(fnmatch.fnmatch(text, pattern) for pattern in ignore_globs)


def discover_files(paths: list[str], ignore_globs: list[str]) -> list[Path]:
    """Resolve ``paths`` (files, directories, globs) into Markdown files."""
    found: list[Path] = []

    for raw in paths:
        candidate = Path(raw)
        if _GLOB_CHARS & set(raw) and not candidate.exists():
            found.extend(Path(m) for m in glob.glob(raw, recursive=True))
        elif candidate.is_dir():
            found.extend(sorted(candidate.rglob("*")))
        elif candidate.is_file():
            found.append(candidate)
        else:
            raise UsageError(f"path does not exist: {raw}")

    result: list[Path] = []
    seen: set[str] = set()
    for path in found:
        if not path.is_file() or path.suffix.lower() not in MD_EXTENSIONS:
            continue
        if _is_ignored(path, ignore_globs):
            continue
        key = str(path)
        if key not in seen:
            seen.add(key)
            result.append(path)
    return result


def _run_list(files: list[Path], stream) -> int:
    total = 0
    for path in files:
        blocks = parse_blocks(path.read_text(encoding="utf-8"), source_file=str(path))
        for block in blocks:
            total += 1
            directives = sorted(k for k, v in block.attrs.items() if v is True)
            suffix = f"  [{', '.join(directives)}]" if directives else ""
            stream.write(f"{block.location}  {block.language or '-'}{suffix}\n")
    if total == 0:
        stream.write("no code blocks found\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Program entry point. Returns a process exit code (does not exit)."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"mdverify: config error: {exc}", file=sys.stderr)
        return 2

    ignore_globs = list(config.ignore) + list(args.ignore)
    paths = args.paths or ["."]

    try:
        files = discover_files(paths, ignore_globs)
    except UsageError as exc:
        print(f"mdverify: {exc}", file=sys.stderr)
        return 2

    if not files:
        print("mdverify: no Markdown files found", file=sys.stderr)
        return 0

    if args.list_blocks:
        return _run_list(files, sys.stdout)

    timeout = args.timeout if args.timeout is not None else config.timeout
    config.timeout = timeout
    langs = {lang.lower() for lang in args.lang} or None

    start = time.monotonic()
    results = []
    read_error = False
    for path in files:
        try:
            file_results = run_file(
                str(path),
                config,
                langs=langs,
                require_runner=args.require_runner,
                fail_fast=args.fail_fast,
            )
        except (UnicodeDecodeError, OSError) as exc:
            reason = getattr(exc, "reason", None) or getattr(exc, "strerror", None) or str(exc)
            print(f"mdverify: cannot read {path}: {reason}", file=sys.stderr)
            read_error = True
            continue
        results.extend(file_results)
        if args.fail_fast and any(not r.ok for r in file_results):
            break
    duration = time.monotonic() - start

    if not results:
        if read_error:
            return 2
        print("mdverify: no runnable blocks found", file=sys.stderr)
        return 0

    color = should_color(args.no_color, sys.stdout)
    report(
        results,
        fmt=args.format,
        color=color,
        verbose=args.verbose,
        quiet=args.quiet,
        duration=duration,
    )

    counts = summarize(results)
    if read_error:
        return 2
    return 1 if counts["failed"] else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
