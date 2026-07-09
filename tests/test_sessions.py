"""Tests for session/state-sharing between code blocks (``session=NAME``)."""

from __future__ import annotations

import json
import shutil

import pytest

from mdverify.block import CodeBlock, parse_info
from mdverify.cli import main
from mdverify.config import default_config
from mdverify.runner import Status, group_sessions, run_file

needs_bash = pytest.mark.skipif(shutil.which("bash") is None, reason="bash not available")


def _write(tmp_path, name, body):
    doc = tmp_path / name
    doc.write_text(body)
    return doc


def _only(results):
    assert len(results) == 1
    return results[0]


# --- directive parsing -----------------------------------------------------


def test_session_directive_parsed_braced():
    _, attrs = parse_info("python {session=setup}")
    assert attrs["session"] == "setup"


def test_session_directive_parsed_bare():
    _, attrs = parse_info("python session=setup")
    assert attrs["session"] == "setup"


def test_session_property_returns_name():
    assert CodeBlock("python", "", attrs={"session": "setup"}).session == "setup"


def test_session_property_none_when_absent():
    assert CodeBlock("python", "").session is None


def test_session_property_none_when_blank():
    assert CodeBlock("python", "", attrs={"session": "  "}).session is None


def test_group_sessions_preserves_document_order():
    blocks = [
        CodeBlock("python", "a", line=1, attrs={"session": "s"}),
        CodeBlock("python", "b", line=2),
        CodeBlock("python", "c", line=3, attrs={"session": "s"}),
        CodeBlock("python", "d", line=4, attrs={"session": "t"}),
    ]
    groups = group_sessions(blocks)
    assert [b.content for b in groups["s"]] == ["a", "c"]
    assert [b.content for b in groups["t"]] == ["d"]


# --- state sharing (the core feature) --------------------------------------


def test_python_session_shares_state(tmp_path):
    doc = _write(
        tmp_path,
        "share.md",
        "```python {session=s}\nx = 41\n```\n\n"
        "```python {session=s}\nassert x == 41\nprint(x)\n```\n",
    )
    result = _only(run_file(str(doc), default_config()))
    assert result.status is Status.PASSED
    assert result.session == "s"
    assert result.block_count == 2


def test_without_session_state_is_not_shared(tmp_path):
    # The exact same two blocks, but without a session directive: the second
    # block runs in a fresh process and its NameError makes the file fail.
    doc = _write(
        tmp_path,
        "noshare.md",
        "```python\nx = 41\n```\n\n```python\nassert x == 41\nprint(x)\n```\n",
    )
    results = run_file(str(doc), default_config())
    assert len(results) == 2
    assert results[0].status is Status.PASSED
    assert results[1].status is Status.FAILED
    assert "NameError" in results[1].stderr


@needs_bash
def test_bash_session_shares_state(tmp_path):
    doc = _write(
        tmp_path,
        "bash.md",
        "```bash {session=b}\nstamp=from-block-1\n```\n\n"
        '```bash {session=b}\n[ "$stamp" = "from-block-1" ] && echo ok\n```\n',
    )
    result = _only(run_file(str(doc), default_config()))
    assert result.status is Status.PASSED
    assert result.stdout.strip() == "ok"


@needs_bash
def test_bash_session_shares_working_directory(tmp_path):
    target = tmp_path / "artifact.txt"
    doc = _write(
        tmp_path,
        "bashfs.md",
        f"```bash {{session=fs}}\necho hi > {target}\n```\n\n"
        f"```bash {{session=fs}}\ncat {target}\n```\n",
    )
    result = _only(run_file(str(doc), default_config()))
    assert result.status is Status.PASSED
    assert result.stdout.strip() == "hi"


# --- failure / error attribution -------------------------------------------


def test_failing_member_fails_session_once(tmp_path):
    doc = _write(
        tmp_path,
        "fail.md",
        "```python {session=s}\nx = 1\n```\n\n```python {session=s}\nraise SystemExit(3)\n```\n",
    )
    result = _only(run_file(str(doc), default_config()))
    assert result.status is Status.FAILED
    assert result.exit_code == 3
    assert result.session == "s"
    # Anchored at the first member's line.
    assert result.block.line == 1


def test_mixed_language_session_is_error_not_crash(tmp_path):
    doc = _write(
        tmp_path,
        "mixed.md",
        "```python {session=s}\nx = 1\n```\n\n```bash {session=s}\necho hi\n```\n",
    )
    result = _only(run_file(str(doc), default_config()))
    assert result.status is Status.ERROR
    assert "mixes languages" in result.reason
    assert "python" in result.reason and "bash" in result.reason


# --- skip interaction ------------------------------------------------------


def test_skip_excludes_member_but_session_runs(tmp_path):
    # The skipped middle member would raise; excluding it lets the session pass.
    doc = _write(
        tmp_path,
        "skipone.md",
        "```python {session=s}\nx = 1\n```\n\n"
        "```python {session=s skip}\nraise SystemExit(9)\n```\n\n"
        "```python {session=s}\nassert x == 1\nprint('ran')\n```\n",
    )
    result = _only(run_file(str(doc), default_config()))
    assert result.status is Status.PASSED
    assert result.stdout.strip() == "ran"
    assert result.block_count == 3


def test_all_members_skipped_session_is_skipped(tmp_path):
    doc = _write(
        tmp_path,
        "skipall.md",
        "```python {session=s skip}\nx = 1\n```\n\n```python {session=s skip}\ny = 2\n```\n",
    )
    result = _only(run_file(str(doc), default_config()))
    assert result.status is Status.SKIPPED
    assert result.session == "s"


# --- output-block pairing interaction --------------------------------------


def test_paired_output_after_session_member_is_ignored(tmp_path):
    # An ``output`` block following a session member must not create a spurious
    # comparison failure: sessions assert exit-0 only.
    doc = _write(
        tmp_path,
        "outpair.md",
        "```python {session=s}\nprint('one')\n```\n\n```output\nDELIBERATELY WRONG\n```\n\n"
        "```python {session=s}\nprint('two')\n```\n",
    )
    results = run_file(str(doc), default_config())
    assert len(results) == 1
    assert results[0].status is Status.PASSED


# --- regression guard: non-session blocks are unchanged --------------------


def test_standalone_blocks_still_behave_as_before(tmp_path):
    doc = _write(
        tmp_path,
        "plain.md",
        "```python\nprint('a')\n```\n\n```output\na\n```\n\n```python {skip}\nboom\n```\n",
    )
    results = run_file(str(doc), default_config())
    assert len(results) == 2
    assert results[0].status is Status.PASSED
    assert results[0].session is None
    assert results[1].status is Status.SKIPPED


# --- --list grouping -------------------------------------------------------


def test_list_shows_session_grouping(tmp_path, capsys):
    doc = _write(
        tmp_path,
        "list.md",
        "```python {session=setup}\nx = 1\n```\n\n```python {session=setup}\nprint(x)\n```\n",
    )
    assert main(["--list", str(doc)]) == 0
    out = capsys.readouterr().out
    assert "session: setup" in out
    assert "2 blocks" in out
    # Non-session blocks would still list one line each; here the two members
    # collapse into a single session entry.
    assert out.count("session: setup") == 1


# --- CLI integration -------------------------------------------------------


def test_cli_passing_session_returns_zero(fixture, capsys):
    assert main([str(fixture("session_pass.md"))]) == 0
    out = capsys.readouterr().out
    assert "PASS" in out
    assert "session: setup" in out


def test_cli_failing_session_returns_one(fixture):
    assert main([str(fixture("session_fail.md"))]) == 1


def test_cli_json_includes_session_info(fixture, capsys):
    assert main(["--format", "json", str(fixture("session_pass.md"))]) == 0
    data = json.loads(capsys.readouterr().out)
    assert len(data) == 1
    assert data[0]["status"] == "passed"
    assert data[0]["session"] == "setup"
    assert data[0]["block_count"] == 2
