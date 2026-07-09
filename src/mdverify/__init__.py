"""mdverify -- a zero-dependency, polyglot Markdown code-block verifier."""

from __future__ import annotations

__version__ = "0.1.0"

from .block import CodeBlock, parse_info
from .cli import main
from .config import Config, Runner, load_config
from .errors import ConfigError, MdverifyError, UsageError
from .parser import parse_blocks
from .runner import BlockResult, Status, run_block, run_file

__all__ = [
    "__version__",
    "CodeBlock",
    "parse_info",
    "parse_blocks",
    "Config",
    "Runner",
    "load_config",
    "BlockResult",
    "Status",
    "run_block",
    "run_file",
    "ConfigError",
    "MdverifyError",
    "UsageError",
    "main",
]
