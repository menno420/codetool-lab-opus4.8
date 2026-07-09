"""Human- and machine-readable reporting of block results."""

from __future__ import annotations

import json
import os
import sys
from typing import TextIO

from .runner import BlockResult, Status

_LABELS = {
    Status.PASSED: "PASS",
    Status.FAILED: "FAIL",
    Status.ERROR: "ERROR",
    Status.SKIPPED: "SKIP",
}

_COLORS = {
    Status.PASSED: "\033[32m",
    Status.FAILED: "\033[31m",
    Status.ERROR: "\033[35m",
    Status.SKIPPED: "\033[33m",
}
_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"


def should_color(no_color: bool, stream: TextIO) -> bool:
    """Decide whether ANSI colour should be emitted."""
    if no_color or os.environ.get("NO_COLOR"):
        return False
    return bool(getattr(stream, "isatty", lambda: False)())


def summarize(results: list[BlockResult]) -> dict[str, int]:
    """Count results by outcome (errors are grouped with failures)."""
    counts = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0}
    for result in results:
        if result.status is Status.PASSED:
            counts["passed"] += 1
        elif result.status is Status.SKIPPED:
            counts["skipped"] += 1
        elif result.status is Status.ERROR:
            counts["errors"] += 1
            counts["failed"] += 1
        else:
            counts["failed"] += 1
    return counts


def _paint(text: str, code: str, color: bool) -> str:
    return f"{code}{text}{_RESET}" if color else text


def _indent(text: str, prefix: str = "    ") -> str:
    return "\n".join(prefix + line for line in text.split("\n"))


def _detail_lines(result: BlockResult, color: bool) -> list[str]:
    lines = [f"    reason: {result.reason}"]
    if result.exit_code is not None:
        lines.append(f"    exit code: {result.exit_code}")
    stderr = result.stderr.strip()
    if stderr:
        lines.append("    stderr:")
        lines.append(_indent(stderr, "      "))
    if result.diff:
        lines.append("    diff (expected vs actual):")
        lines.append(_indent(result.diff, "      "))
    return lines


def _text_report(
    results: list[BlockResult],
    color: bool,
    verbose: bool,
    quiet: bool,
) -> list[str]:
    lines: list[str] = []
    current_file: str | None = object()  # sentinel distinct from any path
    for result in results:
        block = result.block
        show = not quiet or not result.ok

        if show and block.source_file != current_file:
            current_file = block.source_file
            header = block.source_file or "<stdin>"
            lines.append(_paint(header, _BOLD, color))

        if show:
            label = _LABELS[result.status]
            painted = _paint(f"{label:5}", _COLORS[result.status], color)
            suffix = ""
            if result.session is not None:
                noun = "block" if result.block_count == 1 else "blocks"
                suffix = f"  (session: {result.session}, {result.block_count} {noun})"
            lines.append(f"  {painted} {block.location}  {block.language or '-'}{suffix}")

        if not result.ok:
            lines.extend(_detail_lines(result, color))
        elif verbose and (result.stdout.strip() or result.stderr.strip()):
            if result.stdout.strip():
                lines.append("    stdout:")
                lines.append(_indent(result.stdout.strip(), "      "))
            if result.stderr.strip():
                lines.append("    stderr:")
                lines.append(_indent(result.stderr.strip(), "      "))
    return lines


def summary_line(
    results: list[BlockResult],
    duration: float,
    file_count: int,
    color: bool = False,
) -> str:
    """Render the trailing one-line summary."""
    counts = summarize(results)
    noun = "file" if file_count == 1 else "files"
    text = (
        f"{counts['passed']} passed, {counts['failed']} failed, "
        f"{counts['skipped']} skipped in {duration:.2f}s ({file_count} {noun})"
    )
    if not color:
        return text
    code = _COLORS[Status.FAILED] if counts["failed"] else _COLORS[Status.PASSED]
    return _paint(text, _BOLD + code, color)


def report(
    results: list[BlockResult],
    *,
    fmt: str = "pretty",
    color: bool = False,
    verbose: bool = False,
    quiet: bool = False,
    duration: float = 0.0,
    stream: TextIO | None = None,
) -> None:
    """Write a report of ``results`` to ``stream`` (default stdout)."""
    stream = stream or sys.stdout

    if fmt == "json":
        stream.write(json.dumps([r.as_dict() for r in results], indent=2))
        stream.write("\n")
        return

    if fmt == "plain":
        color = False

    file_count = len({r.block.source_file for r in results})
    lines = _text_report(results, color, verbose, quiet)
    if lines:
        stream.write("\n".join(lines))
        stream.write("\n")
    stream.write(summary_line(results, duration, file_count, color))
    stream.write("\n")
