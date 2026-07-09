"""Tests for directive/info-string parsing and output pairing."""

from __future__ import annotations

from mdverify.block import CodeBlock, pair_outputs, parse_info


def test_language_only():
    lang, attrs = parse_info("python")
    assert lang == "python"
    assert attrs == {}


def test_language_is_lowercased():
    lang, _ = parse_info("Python")
    assert lang == "python"


def test_empty_info():
    assert parse_info("") == ("", {})


def test_bare_flag():
    lang, attrs = parse_info("python skip")
    assert lang == "python"
    assert attrs["skip"] is True


def test_braced_attrs():
    lang, attrs = parse_info("python {skip}")
    assert lang == "python"
    assert attrs["skip"] is True


def test_braced_multiple_attrs():
    lang, attrs = parse_info("python {expect-error timeout=5}")
    assert attrs["expect-error"] is True
    assert attrs["timeout"] == "5"


def test_no_run_alias_maps_to_skip():
    _, attrs = parse_info("python no-run")
    assert attrs["skip"] is True


def test_mdverify_skip_alias():
    _, attrs = parse_info("python mdverify-skip")
    assert attrs["skip"] is True


def test_key_value():
    _, attrs = parse_info("python timeout=10")
    assert attrs["timeout"] == "10"


def test_quoted_value_is_stripped():
    _, attrs = parse_info('python title="hello"')
    assert attrs["title"] == "hello"


def test_unknown_flag_is_stored_not_crashing():
    _, attrs = parse_info("python line-numbers")
    assert attrs["line-numbers"] is True


def test_pandoc_class_is_ignored():
    lang, attrs = parse_info("python {.line-numbers}")
    assert lang == "python"
    assert "line-numbers" not in attrs
    assert ".line-numbers" not in attrs


def test_pure_pandoc_block_has_no_language():
    lang, attrs = parse_info("{.python}")
    assert lang == ""


def test_timeout_override_property():
    block = CodeBlock("python", "x", attrs={"timeout": "5"})
    assert block.timeout_override == 5.0


def test_timeout_override_invalid_is_none():
    block = CodeBlock("python", "x", attrs={"timeout": "abc"})
    assert block.timeout_override is None


def test_is_skipped_property():
    assert CodeBlock("python", "x", attrs={"skip": True}).is_skipped is True
    assert CodeBlock("python", "x").is_skipped is False


def test_expect_error_property():
    assert CodeBlock("python", "x", attrs={"expect-error": True}).expect_error is True


def test_location_property():
    block = CodeBlock("python", "x", line=4, source_file="a.md")
    assert block.location == "a.md:4"


def test_pair_outputs_basic():
    blocks = [
        CodeBlock("python", "print(1)"),
        CodeBlock("output", "1"),
    ]
    pairs = pair_outputs(blocks, {"output"})
    assert pairs == {0: "1"}


def test_pair_outputs_requires_immediate_neighbor():
    blocks = [
        CodeBlock("python", "print(1)"),
        CodeBlock("python", "print(2)"),
        CodeBlock("output", "2"),
    ]
    pairs = pair_outputs(blocks, {"output"})
    assert pairs == {1: "2"}


def test_pair_outputs_ignores_output_without_predecessor():
    blocks = [CodeBlock("output", "orphan")]
    assert pair_outputs(blocks, {"output"}) == {}
