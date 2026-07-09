"""Execution of code blocks and evaluation of their results."""

from __future__ import annotations

import difflib
import enum
import os
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from .block import CodeBlock, pair_outputs
from .config import Config, Runner
from .console import ConsoleCommand, ConsoleParseError, parse_console_session
from .parser import parse_blocks


class Status(str, enum.Enum):
    """Outcome of running (or not running) a single block."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class BlockResult:
    """The result of evaluating one :class:`CodeBlock`."""

    block: CodeBlock
    status: Status
    reason: str = ""
    exit_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    duration: float = 0.0
    diff: str | None = None

    @property
    def ok(self) -> bool:
        """True when this result should not fail the run."""
        return self.status in (Status.PASSED, Status.SKIPPED)

    def as_dict(self) -> dict:
        """A JSON-serialisable representation for the ``json`` reporter."""
        return {
            "status": self.status.value,
            "language": self.block.language,
            "file": self.block.source_file,
            "line": self.block.line,
            "exit_code": self.exit_code,
            "reason": self.reason,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration": round(self.duration, 4),
            "diff": self.diff,
        }


def build_command(template: list[str], file_path: str) -> list[str]:
    """Substitute ``{file}`` in ``template`` or append ``file_path``."""
    if any("{file}" in part for part in template):
        return [part.replace("{file}", file_path) for part in template]
    return [*template, file_path]


def _normalize_output(text: str) -> str:
    """Strip trailing whitespace per line and one leading/trailing newline."""
    joined = "\n".join(line.rstrip() for line in text.split("\n"))
    if joined.startswith("\n"):
        joined = joined[1:]
    if joined.endswith("\n"):
        joined = joined[:-1]
    return joined


def _make_diff(expected: str, actual: str) -> str:
    expected_lines = _normalize_output(expected).split("\n")
    actual_lines = _normalize_output(actual).split("\n")
    diff = difflib.unified_diff(
        expected_lines,
        actual_lines,
        fromfile="expected",
        tofile="actual",
        lineterm="",
    )
    return "\n".join(diff)


def _write_temp(content: str, ext: str) -> str:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=ext, prefix="mdverify-", delete=False, encoding="utf-8"
    ) as handle:
        handle.write(content)
        if not content.endswith("\n"):
            handle.write("\n")
        return handle.name


def _evaluate(
    block: CodeBlock,
    exit_code: int,
    stdout: str,
    stderr: str,
    duration: float,
    expected: str | None,
) -> BlockResult:
    if block.expect_error:
        if exit_code != 0:
            return BlockResult(
                block,
                Status.PASSED,
                "exited non-zero as expected",
                exit_code,
                stdout,
                stderr,
                duration,
            )
        return BlockResult(
            block,
            Status.FAILED,
            "expected a non-zero exit but the block succeeded",
            exit_code,
            stdout,
            stderr,
            duration,
        )

    if exit_code != 0:
        return BlockResult(
            block,
            Status.FAILED,
            f"exited with code {exit_code}",
            exit_code,
            stdout,
            stderr,
            duration,
        )

    if expected is not None and _normalize_output(stdout) != _normalize_output(expected):
        return BlockResult(
            block,
            Status.FAILED,
            "output did not match the expected block",
            exit_code,
            stdout,
            stderr,
            duration,
            diff=_make_diff(expected, stdout),
        )

    return BlockResult(block, Status.PASSED, "ok", exit_code, stdout, stderr, duration)


def run_block(
    block: CodeBlock,
    runner: Runner,
    timeout: float,
    expected: str | None = None,
) -> BlockResult:
    """Execute a single block and classify the outcome."""
    tmp = _write_temp(block.content, runner.ext)
    command = build_command(runner.command, tmp)
    start = time.monotonic()
    try:
        try:
            proc = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except FileNotFoundError:
            duration = time.monotonic() - start
            return BlockResult(
                block,
                Status.ERROR,
                f"runner '{runner.language}' not found: "
                f"'{command[0]}' is not installed or not on PATH",
                duration=duration,
            )
        except subprocess.TimeoutExpired as exc:
            duration = time.monotonic() - start
            return BlockResult(
                block,
                Status.FAILED,
                f"timed out after {timeout:g}s",
                stdout=exc.stdout or "",
                stderr=exc.stderr or "",
                duration=duration,
            )
    finally:
        try:
            os.unlink(tmp)
        except OSError:  # pragma: no cover - best effort cleanup
            pass

    duration = time.monotonic() - start
    return _evaluate(block, proc.returncode, proc.stdout, proc.stderr, duration, expected)


def run_console_block(
    block: CodeBlock,
    shell: list[str],
    timeout: float,
) -> BlockResult:
    """Execute a console-session block as ``$``-prefixed shell assertions.

    Each command runs in its own subprocess via ``shell`` (default
    ``["bash", "-c"]``); state is **not** shared across commands. The block
    passes only when every command exits ``0`` and its stdout matches the
    expected transcript lines. The first failing command decides the result.
    """
    try:
        commands = parse_console_session(block.content)
    except ConsoleParseError as exc:
        return BlockResult(block, Status.FAILED, str(exc))

    start = time.monotonic()
    for command in commands:
        result = _run_console_command(block, command, shell, timeout, start)
        if result is not None:
            return result

    duration = time.monotonic() - start
    reason = "ok" if commands else "no commands to run"
    return BlockResult(block, Status.PASSED, reason, exit_code=0, duration=duration)


def _run_console_command(
    block: CodeBlock,
    command: ConsoleCommand,
    shell: list[str],
    timeout: float,
    start: float,
) -> BlockResult | None:
    """Run one console command; return a failing/error result or ``None`` on pass."""
    try:
        proc = subprocess.run(
            [*shell, command.command],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return BlockResult(
            block,
            Status.ERROR,
            f"console shell not found: '{shell[0]}' is not installed or not on PATH",
            duration=time.monotonic() - start,
        )
    except subprocess.TimeoutExpired as exc:
        return BlockResult(
            block,
            Status.FAILED,
            f"command timed out after {timeout:g}s: {command.label}",
            stdout=exc.stdout or "",
            stderr=exc.stderr or "",
            duration=time.monotonic() - start,
        )

    duration = time.monotonic() - start
    if proc.returncode != 0:
        return BlockResult(
            block,
            Status.FAILED,
            f"command exited with code {proc.returncode}: {command.label}",
            exit_code=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            duration=duration,
        )

    if _normalize_output(proc.stdout) != _normalize_output(command.expected):
        return BlockResult(
            block,
            Status.FAILED,
            f"command output did not match expected: {command.label}",
            exit_code=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            duration=duration,
            diff=_make_diff(command.expected, proc.stdout),
        )

    return None


def _classify(
    block: CodeBlock,
    config: Config,
    expected: str | None,
    require_runner: bool,
) -> BlockResult:
    if block.is_skipped:
        return BlockResult(block, Status.SKIPPED, "skipped by directive")

    if block.language in config.console_languages and block.run:
        timeout = block.timeout_override if block.timeout_override is not None else config.timeout
        return run_console_block(block, config.console_shell, timeout)

    runner = config.resolve(block.language)
    if runner is None:
        if not block.language:
            reason = "no language on the code fence"
        else:
            reason = f"no runner for language '{block.language}'"
        status = Status.FAILED if require_runner else Status.SKIPPED
        return BlockResult(block, status, reason)

    timeout = block.timeout_override if block.timeout_override is not None else config.timeout
    return run_block(block, runner, timeout, expected)


def run_file(
    path: str,
    config: Config,
    *,
    langs: set[str] | None = None,
    require_runner: bool = False,
    fail_fast: bool = False,
) -> list[BlockResult]:
    """Parse ``path`` and run every runnable block it contains."""
    text = Path(path).read_text(encoding="utf-8")
    blocks = parse_blocks(text, source_file=str(path))
    outputs = pair_outputs(blocks, config.output_languages)

    results: list[BlockResult] = []
    for index, block in enumerate(blocks):
        if block.language in config.output_languages:
            continue
        if langs is not None and block.language not in langs:
            continue
        result = _classify(block, config, outputs.get(index), require_runner)
        results.append(result)
        if fail_fast and not result.ok:
            break
    return results
