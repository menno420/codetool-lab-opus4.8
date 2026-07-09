"""Tests for the reporting layer."""

from __future__ import annotations

import io
import json

from mdverify.block import CodeBlock
from mdverify.report import report, should_color, summarize, summary_line
from mdverify.runner import BlockResult, Status


def _results():
    return [
        BlockResult(CodeBlock("python", "x", line=1, source_file="a.md"), Status.PASSED, "ok", 0),
        BlockResult(
            CodeBlock("python", "x", line=5, source_file="a.md"),
            Status.FAILED,
            "exited with code 1",
            1,
            stderr="Traceback: boom",
        ),
        BlockResult(
            CodeBlock("text", "x", line=9, source_file="a.md"),
            Status.SKIPPED,
            "no runner",
        ),
    ]


def test_summarize_counts():
    counts = summarize(_results())
    assert counts == {"passed": 1, "failed": 1, "skipped": 1, "errors": 0}


def test_errors_count_as_failed():
    results = [BlockResult(CodeBlock("node", "x"), Status.ERROR, "not found")]
    counts = summarize(results)
    assert counts["errors"] == 1
    assert counts["failed"] == 1


def test_pretty_report_contains_labels():
    out = io.StringIO()
    report(_results(), fmt="pretty", color=False, stream=out)
    text = out.getvalue()
    assert "PASS" in text
    assert "FAIL" in text
    assert "SKIP" in text
    assert "a.md:5" in text


def test_failure_detail_includes_stderr():
    out = io.StringIO()
    report(_results(), fmt="plain", stream=out)
    assert "boom" in out.getvalue()


def test_plain_report_has_no_ansi():
    out = io.StringIO()
    report(_results(), fmt="plain", color=True, stream=out)
    assert "\033[" not in out.getvalue()


def test_pretty_report_can_have_ansi():
    out = io.StringIO()
    report(_results(), fmt="pretty", color=True, stream=out)
    assert "\033[" in out.getvalue()


def test_quiet_hides_passing_lines():
    out = io.StringIO()
    report(_results(), fmt="plain", quiet=True, stream=out)
    text = out.getvalue()
    assert "a.md:1" not in text
    assert "a.md:5" in text


def test_json_report_is_valid():
    out = io.StringIO()
    report(_results(), fmt="json", stream=out)
    data = json.loads(out.getvalue())
    assert len(data) == 3
    assert data[0]["status"] == "passed"
    assert data[1]["exit_code"] == 1


def test_summary_line_format():
    line = summary_line(_results(), duration=1.5, file_count=1)
    assert line == "1 passed, 1 failed, 1 skipped in 1.50s (1 file)"


def test_summary_line_pluralizes_file_count():
    single = summary_line(_results(), duration=1.5, file_count=1)
    plural = summary_line(_results(), duration=1.5, file_count=3)
    assert single.endswith("(1 file)")
    assert plural.endswith("(3 files)")


def test_should_color_respects_no_color_env(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")

    class TTY(io.StringIO):
        def isatty(self):
            return True

    assert should_color(False, TTY()) is False


def test_should_color_off_when_not_tty():
    assert should_color(False, io.StringIO()) is False


def test_should_color_off_when_flag(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)

    class TTY(io.StringIO):
        def isatty(self):
            return True

    assert should_color(True, TTY()) is False
    assert should_color(False, TTY()) is True
