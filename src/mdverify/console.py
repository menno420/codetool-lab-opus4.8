"""Parsing of console-session (``$``-prefixed) assertion blocks.

A console-session block transcribes an interactive shell session: a line
beginning with the prompt ``$ `` is a command, and the lines that follow it
(until the next ``$ `` command or the end of the block) are that command's
expected stdout. A line beginning with ``> `` continues the previous command,
so a backslash-continued shell command spans multiple transcript lines.

This module only *parses* the transcript into ``(command, expected)`` pairs;
executing the commands and asserting their output lives in :mod:`runner`.
"""

from __future__ import annotations

from dataclasses import dataclass

PROMPT = "$ "
CONTINUATION = "> "

_MALFORMED = "console {run} block: expected a line starting with '$ ' before output"


class ConsoleParseError(ValueError):
    """Raised when a console-session block cannot be parsed (e.g. output first)."""


@dataclass
class ConsoleCommand:
    """A single command from a console session and its expected stdout.

    Attributes:
        command: The shell command text. Multi-line commands (joined via ``> ``
            continuation lines) are separated by newlines, exactly as a shell
            would receive them.
        expected: The expected stdout, as the transcript's following lines
            joined by newlines (no enforced trailing newline).
    """

    command: str
    expected: str

    @property
    def label(self) -> str:
        """A single-line ``$ ``-prefixed label for reports."""
        return "$ " + self.command.replace("\n", "\\n")


def parse_console_session(content: str) -> list[ConsoleCommand]:
    """Split a console-session block body into ``ConsoleCommand`` pairs.

    Leading blank lines (before the first ``$ `` prompt) are ignored. Any other
    non-blank content before the first prompt is a malformed transcript and
    raises :class:`ConsoleParseError`.
    """
    commands: list[ConsoleCommand] = []
    current: str | None = None
    output: list[str] = []
    seen_prompt = False

    def flush() -> None:
        nonlocal current, output
        if current is not None:
            commands.append(ConsoleCommand(current, "\n".join(output)))
        current = None
        output = []

    for raw in content.split("\n"):
        if raw.startswith(PROMPT):
            flush()
            current = raw[len(PROMPT) :]
            seen_prompt = True
        elif raw.startswith(CONTINUATION) and current is not None:
            current = current + "\n" + raw[len(CONTINUATION) :]
        elif not seen_prompt:
            if raw.strip():
                raise ConsoleParseError(_MALFORMED)
            # Leading blank line before the first prompt: ignore.
        else:
            output.append(raw)

    flush()
    return commands
