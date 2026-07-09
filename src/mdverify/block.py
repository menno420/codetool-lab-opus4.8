"""The :class:`CodeBlock` model and Markdown info-string / directive parsing.

The info string is the text that follows the opening fence, e.g. the
``python title="demo" {timeout=5 expect-error}`` in::

    ```python title="demo" {timeout=5 expect-error}

The first whitespace-delimited token is the language. Everything after it is
parsed into ``attrs`` as either flags (``skip``) or ``key=value`` pairs
(``timeout=5``). Unknown flags and keys are stored but ignored so that
real-world info strings from other tooling never crash the parser.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Flags that mean "do not run this block", normalised to the canonical "skip".
_SKIP_ALIASES = {"skip", "mdverify-skip", "no-run", "norun"}

# Flags that opt a console-session block into execution, normalised to "run".
_RUN_ALIASES = {"run", "exec"}


@dataclass
class CodeBlock:
    """A single fenced code block extracted from a Markdown document.

    Attributes:
        language: The lowercased language token, or ``""`` when the fence had
            no info string.
        content: The verbatim block body (dedented, without an enforced
            trailing newline).
        line: 1-based line number of the opening fence, used in reports.
        info: The raw (stripped) info string.
        attrs: Parsed directives -- flags map to ``True``, ``key=value`` pairs
            map key to the string value.
        source_file: Path of the Markdown file the block came from, if known.
    """

    language: str
    content: str
    line: int = 0
    info: str = ""
    attrs: dict = field(default_factory=dict)
    source_file: str | None = None

    @property
    def is_skipped(self) -> bool:
        """True when a ``skip`` / ``no-run`` directive is present."""
        return bool(self.attrs.get("skip"))

    @property
    def expect_error(self) -> bool:
        """True when the block is expected to exit non-zero."""
        return bool(self.attrs.get("expect-error"))

    @property
    def run(self) -> bool:
        """True when a ``run`` / ``exec`` directive opts the block into execution.

        Only meaningful for console-session languages; on any other language the
        directive is recognised (so it never crashes the parser) but ignored.
        """
        return bool(self.attrs.get("run"))

    @property
    def session(self) -> str | None:
        """The session name from a ``session=NAME`` directive, or ``None``.

        Members of the same session (per file) share state: their bodies are
        concatenated in document order and run once. An empty or whitespace-only
        value is treated as no session.
        """
        raw = self.attrs.get("session")
        if isinstance(raw, str) and raw.strip():
            return raw.strip()
        return None

    @property
    def timeout_override(self) -> float | None:
        """Per-block timeout in seconds, or ``None`` when unset/invalid."""
        raw = self.attrs.get("timeout")
        if raw is None:
            return None
        try:
            value = float(raw)
        except (TypeError, ValueError):
            return None
        return value if value > 0 else None

    @property
    def location(self) -> str:
        """A ``file:line`` label for reports."""
        where = self.source_file if self.source_file else "<stdin>"
        return f"{where}:{self.line}"


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _parse_token(token: str, attrs: dict) -> None:
    """Parse a single attribute token into ``attrs`` (in place)."""
    token = token.strip()
    if not token:
        return
    # Pandoc-style classes / ids such as ".python" or "#id" -- accept & ignore.
    if token[0] in ".#":
        return
    if "=" in token:
        key, _, value = token.partition("=")
        key = key.strip().lower()
        if key:
            attrs[key] = _strip_quotes(value.strip())
        return
    flag = token.lower()
    if flag in _SKIP_ALIASES:
        attrs["skip"] = True
    elif flag in _RUN_ALIASES:
        attrs["run"] = True
    else:
        # Unknown flag: store it truthy so callers may inspect, but never crash.
        attrs[flag] = True


def parse_info(info: str) -> tuple[str, dict]:
    """Split an info string into ``(language, attrs)``.

    The language is the first token unless the info string is a pure
    Pandoc-style attribute block like ``{.python}``, in which case the
    language is empty and the braces are parsed as attributes.
    """
    info = (info or "").strip()
    if not info:
        return "", {}

    tokens = info.split()
    language = ""
    attr_tokens = tokens
    if not tokens[0].startswith("{"):
        language = tokens[0].lower()
        attr_tokens = tokens[1:]

    text = " ".join(attr_tokens).strip()
    if text.startswith("{") and text.endswith("}"):
        text = text[1:-1]

    attrs: dict = {}
    for token in text.split():
        _parse_token(token, attrs)
    return language, attrs


def make_block(
    info: str,
    content: str,
    line: int,
    source_file: str | None = None,
) -> CodeBlock:
    """Construct a :class:`CodeBlock` from a raw info string and body."""
    language, attrs = parse_info(info)
    return CodeBlock(
        language=language,
        content=content,
        line=line,
        info=info.strip(),
        attrs=attrs,
        source_file=source_file,
    )


def pair_outputs(blocks: list[CodeBlock], output_languages: set[str]) -> dict[int, str]:
    """Map a runnable block's index to the expected output of the next block.

    A block is paired with the *immediately following* block when that block's
    language is one of ``output_languages``. The paired block's content is the
    expected stdout for the runnable block.
    """
    pairs: dict[int, str] = {}
    for index, block in enumerate(blocks):
        if block.language in output_languages:
            continue
        nxt = blocks[index + 1] if index + 1 < len(blocks) else None
        if nxt is not None and nxt.language in output_languages:
            pairs[index] = nxt.content
    return pairs
