"""Tests for the runner registry and config loading."""

from __future__ import annotations

import json
import sys

import pytest

from mdverify.config import default_config, load_config
from mdverify.errors import ConfigError


def test_default_python_runner():
    config = default_config()
    runner = config.resolve("python")
    assert runner is not None
    assert runner.command == [sys.executable, "{file}"]
    assert runner.ext == ".py"


def test_python_aliases_resolve():
    config = default_config()
    assert config.resolve("py") is config.resolve("python")
    assert config.resolve("python3") is config.resolve("python")


def test_js_alias_resolves_to_node():
    config = default_config()
    assert config.resolve("js").language == "node"
    assert config.resolve("javascript").language == "node"


def test_unknown_language_has_no_runner():
    assert default_config().resolve("elvish") is None


def test_resolve_is_case_insensitive():
    assert default_config().resolve("Python") is not None


def test_default_output_language():
    assert "output" in default_config().output_languages


def test_load_missing_config_returns_defaults(tmp_path):
    config = load_config(start_dir=str(tmp_path))
    assert config.resolve("python") is not None


def test_load_valid_config(tmp_path):
    (tmp_path / ".mdverify.json").write_text(
        json.dumps(
            {
                "timeout": 5,
                "output_languages": ["output", "text"],
                "ignore": ["**/vendor/**"],
            }
        )
    )
    config = load_config(start_dir=str(tmp_path))
    assert config.timeout == 5.0
    assert "text" in config.output_languages
    assert config.ignore == ["**/vendor/**"]


def test_user_runner_merges_over_defaults(tmp_path):
    (tmp_path / ".mdverify.json").write_text(
        json.dumps(
            {
                "runners": {
                    "python": {"command": ["custom-python", "{file}"], "ext": ".py"},
                    "lua": {"command": ["lua", "{file}"], "ext": ".lua", "aliases": ["luajit"]},
                }
            }
        )
    )
    config = load_config(str(tmp_path / ".mdverify.json"))
    assert config.resolve("python").command == ["custom-python", "{file}"]
    assert config.resolve("lua").language == "lua"
    assert config.resolve("luajit") is config.resolve("lua")
    # Defaults not overridden remain.
    assert config.resolve("bash") is not None


def test_malformed_json_raises_config_error(tmp_path):
    path = tmp_path / ".mdverify.json"
    path.write_text("{not valid json")
    with pytest.raises(ConfigError, match="invalid JSON"):
        load_config(str(path))


def test_missing_explicit_config_raises(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        load_config(str(tmp_path / "nope.json"))


def test_bad_runner_schema_raises(tmp_path):
    path = tmp_path / ".mdverify.json"
    path.write_text(json.dumps({"runners": {"x": {"ext": ".x"}}}))
    with pytest.raises(ConfigError, match="command"):
        load_config(str(path))


def test_bad_timeout_raises(tmp_path):
    path = tmp_path / ".mdverify.json"
    path.write_text(json.dumps({"timeout": -1}))
    with pytest.raises(ConfigError, match="timeout"):
        load_config(str(path))


def test_non_object_root_raises(tmp_path):
    path = tmp_path / ".mdverify.json"
    path.write_text("[1, 2, 3]")
    with pytest.raises(ConfigError, match="object"):
        load_config(str(path))
