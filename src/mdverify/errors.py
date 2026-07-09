"""Exception types for mdverify."""

from __future__ import annotations


class MdverifyError(Exception):
    """Base class for all mdverify errors."""


class ConfigError(MdverifyError):
    """Raised when a configuration file is missing, malformed, or invalid."""


class UsageError(MdverifyError):
    """Raised for command-line usage problems (e.g. a path that does not exist)."""
