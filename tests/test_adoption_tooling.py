"""Structural tests for the CI/pre-commit adoption tooling.

These verify the shape of `action.yml` and `.pre-commit-hooks.yaml` at the
repo root without requiring a YAML parser, so the suite passes on a
stdlib-only install. A separate test opts into `pyyaml` when it is available.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
ACTION = REPO_ROOT / "action.yml"
PRE_COMMIT_HOOKS = REPO_ROOT / ".pre-commit-hooks.yaml"


def test_action_yml_exists_and_is_composite():
    assert ACTION.is_file()
    text = ACTION.read_text(encoding="utf-8")
    assert text.strip()
    assert "using: composite" in text
    assert "github.action_path" in text
    assert "mdverify" in text
    assert "inputs:" in text
    assert "paths:" in text
    assert "args:" in text


def test_pre_commit_hooks_yaml_exists_and_declares_mdverify():
    assert PRE_COMMIT_HOOKS.is_file()
    text = PRE_COMMIT_HOOKS.read_text(encoding="utf-8")
    assert text.strip()
    assert "id: mdverify" in text
    assert "entry: mdverify" in text
    assert "language: python" in text
    assert "types:" in text
    assert "markdown" in text


def test_yaml_structure_when_pyyaml_available():
    yaml = pytest.importorskip("yaml")

    action = yaml.safe_load(ACTION.read_text(encoding="utf-8"))
    assert action["runs"]["using"] == "composite"
    assert {"paths", "args"} <= set(action["inputs"])

    hooks = yaml.safe_load(PRE_COMMIT_HOOKS.read_text(encoding="utf-8"))
    assert isinstance(hooks, list) and hooks
    hook = hooks[0]
    assert hook["id"] == "mdverify"
    assert hook["entry"] == "mdverify"
    assert hook["language"] == "python"
    assert "markdown" in hook["types"]
