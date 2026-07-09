"""Integration tests driving ``main()`` directly."""

from __future__ import annotations

import json

import pytest

from mdverify import __version__
from mdverify.cli import main


def test_passing_fixture_returns_zero(fixture, capsys):
    assert main([str(fixture("passing.md"))]) == 0
    assert "PASS" in capsys.readouterr().out


def test_failing_fixture_returns_one(fixture):
    assert main([str(fixture("failing.md"))]) == 1


def test_output_match_passes(fixture):
    assert main([str(fixture("output_match.md"))]) == 0


def test_output_mismatch_fails(fixture, capsys):
    assert main([str(fixture("output_mismatch.md"))]) == 1
    assert "diff" in capsys.readouterr().out


def test_expect_error_fixture_passes(fixture):
    assert main([str(fixture("expect_error.md"))]) == 0


def test_directives_fixture_passes(fixture):
    assert main([str(fixture("directives.md"))]) == 0


def test_unknown_language_skips_and_passes(fixture, capsys):
    assert main([str(fixture("unknown_lang.md"))]) == 0
    assert "SKIP" in capsys.readouterr().out


def test_require_runner_turns_skip_into_failure(fixture):
    assert main(["--require-runner", str(fixture("unknown_lang.md"))]) == 1


def test_list_lists_blocks_without_running(fixture, capsys):
    assert main(["--list", str(fixture("passing.md"))]) == 0
    out = capsys.readouterr().out
    assert "passing.md:" in out
    assert "python" in out
    assert "bash" in out


def test_format_json_emits_valid_json(fixture, capsys):
    assert main(["--format", "json", str(fixture("passing.md"))]) == 0
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list)
    assert data[0]["status"] == "passed"


def test_version_prints_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_directory_recursion_picks_up_fixtures(fixtures_dir):
    # The fixtures directory contains at least one failing fixture, so a
    # recursive run should report failures (exit 1).
    assert main([str(fixtures_dir)]) == 1


def test_lang_filter_only_runs_matching_blocks(fixture, capsys):
    assert main(["--lang", "bash", str(fixture("passing.md"))]) == 0
    out = capsys.readouterr().out
    assert "bash" in out
    assert "1 passed" in out


def test_missing_path_is_usage_error(capsys):
    assert main(["does-not-exist.md"]) == 2
    assert "does not exist" in capsys.readouterr().err


def test_config_error_returns_two(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    assert main(["-c", str(bad), "."]) == 2
    assert "config error" in capsys.readouterr().err


def test_fail_fast_stops_early(fixtures_dir, capsys):
    # With --fail-fast the run stops at the first failing block.
    rc = main(["--fail-fast", str(fixtures_dir)])
    assert rc == 1


def test_no_markdown_files_note(tmp_path, capsys):
    assert main([str(tmp_path)]) == 0
    assert "no Markdown files" in capsys.readouterr().err


def test_non_utf8_file_returns_two_with_clean_message(tmp_path, capsys):
    p = tmp_path / "bad.md"
    p.write_bytes(b"# hi\n\xff\xfe not utf8\n")
    assert main([str(p)]) == 2
    assert "cannot read" in capsys.readouterr().err
