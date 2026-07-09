"""Tests for opt-in console-session ($-prefixed) shell-assertion blocks."""

from __future__ import annotations

import json
import shutil

import pytest

from mdverify.block import CodeBlock, parse_info
from mdverify.cli import main
from mdverify.config import default_config, load_config
from mdverify.console import ConsoleParseError, parse_console_session
from mdverify.runner import Status, run_console_block, run_file

needs_bash = pytest.mark.skipif(shutil.which("bash") is None, reason="bash not available")
BASH = ["bash", "-c"]


def _console(content: str, **attrs) -> CodeBlock:
    attrs.setdefault("run", True)
    return CodeBlock("console", content, attrs=dict(attrs))


# --- transcript parsing (no shell needed) ---------------------------------


def test_parse_two_commands():
    cmds = parse_console_session("$ echo a\na\n$ echo b\nb")
    assert [(c.command, c.expected) for c in cmds] == [("echo a", "a"), ("echo b", "b")]


def test_parse_command_with_empty_expected():
    cmds = parse_console_session("$ true")
    assert len(cmds) == 1
    assert cmds[0].command == "true"
    assert cmds[0].expected == ""


def test_parse_continuation_joins_with_newline():
    cmds = parse_console_session("$ echo a \\\n> b\na b")
    assert cmds[0].command == "echo a \\\nb"
    assert cmds[0].expected == "a b"


def test_parse_leading_blank_lines_are_ok():
    cmds = parse_console_session("\n\n$ echo hi\nhi")
    assert cmds[0].command == "echo hi"


def test_parse_output_before_prompt_is_malformed():
    with pytest.raises(ConsoleParseError, match="expected a line starting with"):
        parse_console_session("some output\n$ echo hi\nhi")


def test_command_label_is_single_line():
    cmds = parse_console_session("$ echo a \\\n> b")
    assert cmds[0].label == "$ echo a \\\\nb"


# --- directive parsing -----------------------------------------------------


def test_run_directive_recognized_braced():
    _, attrs = parse_info("console {run}")
    assert attrs["run"] is True


def test_run_directive_recognized_bare():
    _, attrs = parse_info("console run")
    assert attrs["run"] is True


def test_exec_directive_aliases_run():
    _, attrs = parse_info("console {exec}")
    assert attrs["run"] is True


def test_block_run_property():
    assert CodeBlock("console", "", attrs={"run": True}).run is True
    assert CodeBlock("console", "").run is False


# --- execution -------------------------------------------------------------


@needs_bash
def test_two_matching_commands_pass():
    block = _console("$ echo one\none\n$ echo two\ntwo")
    result = run_console_block(block, BASH, timeout=10)
    assert result.status is Status.PASSED


@needs_bash
def test_output_mismatch_fails_with_diff_naming_command():
    block = _console("$ echo one\nWRONG")
    result = run_console_block(block, BASH, timeout=10)
    assert result.status is Status.FAILED
    assert "$ echo one" in result.reason
    assert result.diff is not None
    assert "-WRONG" in result.diff
    assert "+one" in result.diff


@needs_bash
def test_nonzero_exit_fails():
    block = _console("$ exit 3")
    result = run_console_block(block, BASH, timeout=10)
    assert result.status is Status.FAILED
    assert result.exit_code == 3
    assert "$ exit 3" in result.reason


@needs_bash
def test_empty_expected_output_passes():
    block = _console("$ true")
    result = run_console_block(block, BASH, timeout=10)
    assert result.status is Status.PASSED


@needs_bash
def test_multiline_command_via_continuation_runs():
    block = _console("$ echo a \\\n> b\na b")
    result = run_console_block(block, BASH, timeout=10)
    assert result.status is Status.PASSED


@needs_bash
def test_stderr_shown_on_command_failure():
    block = _console("$ echo boom >&2; exit 1")
    result = run_console_block(block, BASH, timeout=10)
    assert result.status is Status.FAILED
    assert "boom" in result.stderr


def test_malformed_block_fails_with_helpful_message():
    block = _console("printed before any prompt\n$ echo hi\nhi")
    # No shell is spawned before the parse error, so this needs no bash.
    result = run_console_block(block, BASH, timeout=10)
    assert result.status is Status.FAILED
    assert "expected a line starting with '$ '" in result.reason


def test_missing_shell_is_error():
    block = _console("$ echo hi\nhi")
    result = run_console_block(block, ["definitely-not-a-real-shell-xyz", "-c"], timeout=10)
    assert result.status is Status.ERROR
    assert "not found" in result.reason


# --- opt-in / backward compatibility --------------------------------------


@needs_bash
def test_console_without_run_is_skipped_and_does_not_execute(tmp_path):
    marker = tmp_path / "marker"
    doc = tmp_path / "doc.md"
    doc.write_text(f"```console\n$ touch {marker}\n```\n")
    results = run_file(str(doc), default_config())
    assert len(results) == 1
    assert results[0].status is Status.SKIPPED
    assert not marker.exists()


@needs_bash
def test_console_with_run_executes_via_run_file(tmp_path):
    doc = tmp_path / "doc.md"
    doc.write_text("```console {run}\n$ echo hi\nhi\n```\n")
    results = run_file(str(doc), default_config())
    assert len(results) == 1
    assert results[0].status is Status.PASSED


@needs_bash
def test_run_directive_on_non_console_language_is_ignored(tmp_path):
    # A python block tagged {run} still runs as python, not as a shell session.
    doc = tmp_path / "doc.md"
    doc.write_text("```python {run}\nprint('py')\n```\n")
    results = run_file(str(doc), default_config())
    assert len(results) == 1
    assert results[0].status is Status.PASSED
    assert results[0].stdout.strip() == "py"


# --- config ----------------------------------------------------------------


def test_default_console_config():
    config = default_config()
    assert "console" in config.console_languages
    assert "shell-session" in config.console_languages
    assert config.console_shell == ["bash", "-c"]


@needs_bash
def test_console_shell_override_respected(tmp_path):
    (tmp_path / ".mdverify.json").write_text(json.dumps({"console_shell": ["sh", "-c"]}))
    config = load_config(start_dir=str(tmp_path))
    assert config.console_shell == ["sh", "-c"]
    block = _console("$ echo hi\nhi")
    result = run_console_block(block, config.console_shell, timeout=10)
    assert result.status is Status.PASSED


@needs_bash
def test_console_languages_extendable(tmp_path):
    (tmp_path / ".mdverify.json").write_text(json.dumps({"console_languages": ["console", "term"]}))
    config = load_config(start_dir=str(tmp_path))
    assert "term" in config.console_languages
    doc = tmp_path / "doc.md"
    doc.write_text("```term {run}\n$ echo hi\nhi\n```\n")
    results = run_file(str(doc), config)
    assert results[0].status is Status.PASSED


def test_bad_console_shell_raises(tmp_path):
    path = tmp_path / ".mdverify.json"
    path.write_text(json.dumps({"console_shell": []}))
    with pytest.raises(Exception, match="console_shell"):
        load_config(str(path))


def test_bad_console_languages_raises(tmp_path):
    path = tmp_path / ".mdverify.json"
    path.write_text(json.dumps({"console_languages": "console"}))
    with pytest.raises(Exception, match="console_languages"):
        load_config(str(path))


# --- CLI integration -------------------------------------------------------


@needs_bash
def test_cli_passing_console_fixture(fixture):
    assert main([str(fixture("console_pass.md"))]) == 0


@needs_bash
def test_cli_failing_console_fixture(fixture, capsys):
    assert main([str(fixture("console_fail.md"))]) == 1
    assert "diff" in capsys.readouterr().out


@needs_bash
def test_cli_json_identifies_failing_command(fixture, capsys):
    assert main(["--format", "json", str(fixture("console_fail.md"))]) == 1
    data = json.loads(capsys.readouterr().out)
    assert data[0]["status"] == "failed"
    assert "$ echo mdverify" in data[0]["reason"]


def test_cli_list_shows_runnable_console_block(fixture, capsys):
    assert main(["--list", str(fixture("console_pass.md"))]) == 0
    out = capsys.readouterr().out
    assert "console_pass.md:" in out
    assert "console" in out
    assert "run" in out
