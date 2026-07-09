"""Tests for block execution and result evaluation."""

from __future__ import annotations

import shutil
import sys

import pytest

from mdverify.block import CodeBlock
from mdverify.config import Runner, default_config
from mdverify.runner import BlockResult, Status, build_command, run_block

PY = Runner("python", [sys.executable, "{file}"], ".py")
BASH = Runner("bash", ["bash", "{file}"], ".sh")

needs_bash = pytest.mark.skipif(shutil.which("bash") is None, reason="bash not available")


def _block(content, **attrs):
    return CodeBlock("python", content, attrs=dict(attrs))


def test_build_command_substitutes_placeholder():
    assert build_command(["x", "{file}", "-v"], "/tmp/a.py") == ["x", "/tmp/a.py", "-v"]


def test_build_command_appends_when_no_placeholder():
    assert build_command(["x", "-v"], "/tmp/a.py") == ["x", "-v", "/tmp/a.py"]


def test_passing_python_block():
    result = run_block(_block("print('hi')"), PY, timeout=10)
    assert result.status is Status.PASSED
    assert result.exit_code == 0
    assert result.stdout.strip() == "hi"


def test_failing_python_block():
    result = run_block(_block("raise SystemExit(2)"), PY, timeout=10)
    assert result.status is Status.FAILED
    assert result.exit_code == 2
    assert "2" in result.reason


def test_expect_error_passes_on_nonzero():
    block = _block("raise SystemExit(1)", **{"expect-error": True})
    result = run_block(block, PY, timeout=10)
    assert result.status is Status.PASSED


def test_expect_error_fails_on_zero():
    block = _block("print('fine')", **{"expect-error": True})
    result = run_block(block, PY, timeout=10)
    assert result.status is Status.FAILED
    assert "non-zero" in result.reason


@needs_bash
def test_passing_bash_block():
    result = run_block(CodeBlock("bash", "echo hello"), BASH, timeout=10)
    assert result.status is Status.PASSED
    assert result.stdout.strip() == "hello"


def test_output_assertion_match():
    block = _block("print('a')\nprint('b')")
    result = run_block(block, PY, timeout=10, expected="a\nb")
    assert result.status is Status.PASSED


def test_output_assertion_match_ignores_trailing_whitespace():
    block = _block("print('a  ')")
    result = run_block(block, PY, timeout=10, expected="a")
    assert result.status is Status.PASSED


def test_output_assertion_mismatch_has_diff():
    block = _block("print('a')\nprint('x')")
    result = run_block(block, PY, timeout=10, expected="a\nb")
    assert result.status is Status.FAILED
    assert result.diff is not None
    assert "-b" in result.diff
    assert "+x" in result.diff


def test_timeout_fails():
    block = _block("import time; time.sleep(5)")
    result = run_block(block, PY, timeout=0.3)
    assert result.status is Status.FAILED
    assert "timed out" in result.reason


def test_missing_interpreter_is_error():
    bogus = Runner("bogus", ["definitely-not-a-real-binary-xyz", "{file}"], ".x")
    result = run_block(CodeBlock("bogus", "whatever"), bogus, timeout=10)
    assert result.status is Status.ERROR
    assert "not found" in result.reason


def test_result_as_dict_is_serialisable():
    result = run_block(_block("print('hi')"), PY, timeout=10)
    data = result.as_dict()
    assert data["status"] == "passed"
    assert data["language"] == "python"


def test_default_config_runs_python():
    config = default_config()
    runner = config.resolve("python")
    result = run_block(_block("print('via config')"), runner, timeout=10)
    assert result.status is Status.PASSED


def test_ok_property():
    assert BlockResult(_block("x"), Status.PASSED).ok
    assert BlockResult(_block("x"), Status.SKIPPED).ok
    assert not BlockResult(_block("x"), Status.FAILED).ok
    assert not BlockResult(_block("x"), Status.ERROR).ok
