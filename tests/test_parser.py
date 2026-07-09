"""Tests for fenced code block extraction."""

from __future__ import annotations

from mdverify.parser import parse_blocks


def test_backtick_block():
    blocks = parse_blocks("```python\nprint(1)\n```\n")
    assert len(blocks) == 1
    assert blocks[0].language == "python"
    assert blocks[0].content == "print(1)"


def test_tilde_block():
    blocks = parse_blocks("~~~python\nprint(1)\n~~~\n")
    assert len(blocks) == 1
    assert blocks[0].language == "python"
    assert blocks[0].content == "print(1)"


def test_tilde_fence_allows_backticks_in_body():
    blocks = parse_blocks("~~~md\nuse `code` spans\n~~~\n")
    assert blocks[0].content == "use `code` spans"


def test_longer_fence_run():
    text = "````python\ninner ``` still inside\n````\n"
    blocks = parse_blocks(text)
    assert len(blocks) == 1
    assert "still inside" in blocks[0].content


def test_closing_fence_must_be_at_least_as_long():
    text = "````\na\n```\nb\n````\n"
    blocks = parse_blocks(text)
    assert len(blocks) == 1
    assert blocks[0].content == "a\n```\nb"


def test_indented_fence_dedents_body():
    text = "  ```python\n  print(1)\n    indented\n  ```\n"
    blocks = parse_blocks(text)
    assert blocks[0].content == "print(1)\n  indented"


def test_info_string_extraction():
    blocks = parse_blocks("```python title=demo\nx=1\n```\n")
    assert blocks[0].language == "python"
    assert blocks[0].info == "python title=demo"


def test_no_language():
    blocks = parse_blocks("```\nplain\n```\n")
    assert blocks[0].language == ""


def test_unterminated_fence_consumes_rest():
    text = "intro\n```python\nprint(1)\nprint(2)\n"
    blocks = parse_blocks(text)
    assert len(blocks) == 1
    assert blocks[0].content == "print(1)\nprint(2)"


def test_multiple_blocks():
    text = "```python\na\n```\n\n```bash\nb\n```\n"
    blocks = parse_blocks(text)
    assert [b.language for b in blocks] == ["python", "bash"]


def test_block_with_blank_lines_in_body():
    text = "```python\na\n\n\nb\n```\n"
    blocks = parse_blocks(text)
    assert blocks[0].content == "a\n\n\nb"


def test_line_numbers_are_one_based():
    text = "line1\nline2\n```python\nx\n```\n"
    blocks = parse_blocks(text)
    assert blocks[0].line == 3


def test_no_blocks_returns_empty():
    assert parse_blocks("just some prose\nno fences here\n") == []


def test_empty_block_body():
    blocks = parse_blocks("```python\n```\n")
    assert len(blocks) == 1
    assert blocks[0].content == ""


def test_source_file_recorded():
    blocks = parse_blocks("```py\nx\n```\n", source_file="doc.md")
    assert blocks[0].source_file == "doc.md"


def test_more_than_three_leading_spaces_is_not_a_fence():
    # Four leading spaces make it an indented code block, not a fence.
    blocks = parse_blocks("    ```python\n    x\n    ```\n")
    assert blocks == []


def test_closing_fence_with_trailing_whitespace():
    blocks = parse_blocks("```python\nx\n```   \n")
    assert len(blocks) == 1
    assert blocks[0].content == "x"
