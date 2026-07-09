"""Tests for ``pyproject.toml`` / TOML configuration loading.

These are gated on ``tomllib`` being importable (Python 3.11+); on 3.9/3.10 the
whole module is skipped so the suite still passes there.
"""

from __future__ import annotations

import json

import pytest

from mdverify import config as config_module
from mdverify.config import load_config
from mdverify.errors import ConfigError

pytest.importorskip("tomllib")

PYPROJECT_MDVERIFY = """\
[tool.mdverify]
timeout = 5
output_languages = ["output", "text"]
ignore = ["**/vendor/**"]

[tool.mdverify.runners.python]
command = ["custom-python", "{file}"]
ext = ".py"

[tool.mdverify.runners.lua]
command = ["lua", "{file}"]
ext = ".lua"
aliases = ["luajit"]
"""


def test_pyproject_table_is_loaded(tmp_path, monkeypatch):
    (tmp_path / "pyproject.toml").write_text(PYPROJECT_MDVERIFY)
    monkeypatch.chdir(tmp_path)
    config = load_config()
    assert config.timeout == 5.0
    assert "text" in config.output_languages
    assert config.ignore == ["**/vendor/**"]
    assert config.resolve("python").command == ["custom-python", "{file}"]
    assert config.resolve("lua").language == "lua"
    assert config.resolve("luajit") is config.resolve("lua")
    # Defaults not overridden remain.
    assert config.resolve("bash") is not None


def test_json_wins_over_pyproject(tmp_path, monkeypatch):
    (tmp_path / "pyproject.toml").write_text(PYPROJECT_MDVERIFY)
    (tmp_path / ".mdverify.json").write_text(json.dumps({"timeout": 12}))
    monkeypatch.chdir(tmp_path)
    config = load_config()
    # JSON is the higher-precedence source; the pyproject timeout is ignored.
    assert config.timeout == 12.0
    assert config.resolve("python").command != ["custom-python", "{file}"]


def test_pyproject_without_table_falls_through_to_defaults(tmp_path, monkeypatch):
    (tmp_path / "pyproject.toml").write_text('[build-system]\nrequires = ["hatchling"]\n')
    monkeypatch.chdir(tmp_path)
    config = load_config()
    assert config.timeout == config_module.DEFAULT_TIMEOUT
    assert config.resolve("python") is not None


def test_explicit_toml_config_is_loaded(tmp_path):
    path = tmp_path / "pyproject.toml"
    path.write_text(PYPROJECT_MDVERIFY)
    config = load_config(str(path))
    assert config.timeout == 5.0
    assert config.resolve("python").command == ["custom-python", "{file}"]


def test_explicit_plain_toml_uses_document_root(tmp_path):
    path = tmp_path / "mdverify.toml"
    path.write_text('timeout = 7\noutput_languages = ["output", "result"]\n')
    config = load_config(str(path))
    assert config.timeout == 7.0
    assert "result" in config.output_languages


def test_malformed_toml_raises_config_error(tmp_path):
    path = tmp_path / "pyproject.toml"
    path.write_text("[tool.mdverify\ntimeout = ")
    with pytest.raises(ConfigError, match="invalid TOML"):
        load_config(str(path))


def test_bad_pyproject_table_type_raises(tmp_path):
    path = tmp_path / "pyproject.toml"
    path.write_text('[tool]\nmdverify = "nope"\n')
    with pytest.raises(ConfigError, match="tool.mdverify"):
        load_config(str(path))


def test_toml_config_needs_py311_when_tomllib_absent(tmp_path, monkeypatch):
    # Simulate Python 3.9/3.10 where tomllib is unavailable.
    monkeypatch.setattr(config_module, "tomllib", None)
    path = tmp_path / "pyproject.toml"
    path.write_text(PYPROJECT_MDVERIFY)
    with pytest.raises(ConfigError, match="requires Python 3.11"):
        load_config(str(path))


def test_pyproject_in_cwd_skipped_when_tomllib_absent(tmp_path, monkeypatch):
    # With tomllib unavailable, a pyproject in cwd is silently skipped (no crash).
    monkeypatch.setattr(config_module, "tomllib", None)
    (tmp_path / "pyproject.toml").write_text(PYPROJECT_MDVERIFY)
    monkeypatch.chdir(tmp_path)
    config = load_config()
    assert config.timeout == config_module.DEFAULT_TIMEOUT
    assert config.resolve("python") is not None
