"""CommonMark-ish fenced code block extraction.

Only the fenced-code-block grammar is implemented -- enough to reliably pull
runnable snippets out of documentation. An opening fence is a line with up to
three leading spaces followed by a run of at least three backticks or tildes
and an optional info string. The matching closing fence uses the same fence
character, is at least as long, and contains nothing but optional trailing
whitespace. An unterminated fence consumes the rest of the document, matching
CommonMark behaviour.
"""

from __future__ import annotations

import re

from .block import CodeBlock, make_block

_OPEN_RE = re.compile(r"^(?P<indent> {0,3})(?P<fence>`{3,}|~{3,})(?P<info>.*)$")


def _closes(line: str, fence_char: str, min_len: int) -> bool:
    """Return True when ``line`` is a valid closing fence."""
    indent = len(line) - len(line.lstrip(" "))
    if indent > 3:
        return False
    stripped = line.strip()
    run = 0
    for char in stripped:
        if char == fence_char:
            run += 1
        else:
            break
    if run < min_len:
        return False
    return stripped[run:].strip() == ""


def _dedent(line: str, indent: int) -> str:
    """Remove up to ``indent`` leading spaces from ``line``."""
    removed = 0
    index = 0
    while index < len(line) and removed < indent and line[index] == " ":
        index += 1
        removed += 1
    return line[index:]


def parse_blocks(text: str, source_file: str | None = None) -> list[CodeBlock]:
    """Extract all fenced code blocks from ``text`` in document order."""
    lines = text.split("\n")
    blocks: list[CodeBlock] = []
    index = 0
    total = len(lines)

    while index < total:
        match = _OPEN_RE.match(lines[index])
        if not match:
            index += 1
            continue

        fence = match.group("fence")
        fence_char = fence[0]
        fence_len = len(fence)
        info = match.group("info")
        indent = len(match.group("indent"))

        # A backtick info string may not itself contain a backtick (CommonMark).
        if fence_char == "`" and "`" in info:
            index += 1
            continue

        open_line = index + 1  # 1-based
        index += 1
        body: list[str] = []
        while index < total and not _closes(lines[index], fence_char, fence_len):
            body.append(_dedent(lines[index], indent))
            index += 1

        closed = index < total
        if closed:
            index += 1  # consume the closing fence
        elif body and body[-1] == "":
            # Unterminated fence at EOF: drop the phantom line produced by the
            # document's final newline so the body matches a closed block.
            body.pop()

        blocks.append(make_block(info, "\n".join(body), open_line, source_file))

    return blocks
