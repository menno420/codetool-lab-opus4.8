"""Guard against version drift between the package and pyproject.toml."""

from __future__ import annotations

import re
from pathlib import Path

import mdverify

PYPROJECT = Path(__file__).parent.parent / "pyproject.toml"


def _pyproject_version() -> str:
    text = PYPROJECT.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    assert match, "version not found in pyproject.toml"
    return match.group(1)


def test_version_matches_pyproject():
    assert mdverify.__version__ == _pyproject_version()


def test_version_is_semver_ish():
    assert re.match(r"^\d+\.\d+\.\d+", mdverify.__version__)
