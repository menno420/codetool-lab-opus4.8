"""Runner registry and JSON configuration loading.

Configuration is JSON (``.mdverify.json``) rather than TOML so that mdverify
works on Python 3.9, which has no ``tomllib`` in the standard library.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .errors import ConfigError

CONFIG_FILENAME = ".mdverify.json"
DEFAULT_TIMEOUT = 30.0


@dataclass
class Runner:
    """How to execute a block of a given language.

    ``command`` is an argv template; the string ``{file}`` is replaced with the
    path of the temporary file holding the block body. When no ``{file}``
    placeholder is present the temp path is appended as the final argument.
    """

    language: str
    command: list[str]
    ext: str


# (canonical name + aliases, command template, temp-file extension)
_DEFAULT_SPECS = [
    (["python", "py", "python3"], [sys.executable, "{file}"], ".py"),
    (["bash"], ["bash", "{file}"], ".sh"),
    (["sh", "shell"], ["sh", "{file}"], ".sh"),
    (["node", "js", "javascript"], ["node", "{file}"], ".js"),
    (["ruby", "rb"], ["ruby", "{file}"], ".rb"),
]


@dataclass
class Config:
    """Resolved configuration used throughout a run."""

    runners: dict[str, Runner] = field(default_factory=dict)
    output_languages: set[str] = field(default_factory=lambda: {"output"})
    timeout: float = DEFAULT_TIMEOUT
    ignore: list[str] = field(default_factory=list)

    def resolve(self, language: str) -> Runner | None:
        """Return the runner for ``language`` (by name or alias) or ``None``."""
        if not language:
            return None
        return self.runners.get(language.lower())

    def register(self, names: list[str], command: list[str], ext: str) -> None:
        """Register a runner under a canonical name and any aliases."""
        canonical = names[0]
        runner = Runner(language=canonical, command=list(command), ext=ext)
        for name in names:
            self.runners[name.lower()] = runner


def default_config() -> Config:
    """Build a :class:`Config` populated with the built-in runners."""
    config = Config()
    for names, command, ext in _DEFAULT_SPECS:
        config.register(names, command, ext)
    return config


def _read_json(path: Path) -> dict:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:  # pragma: no cover - unlikely
        raise ConfigError(f"could not read config file {path}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ConfigError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"config root in {path} must be a JSON object")
    return data


def _apply_runners(config: Config, runners: object, path: Path) -> None:
    if not isinstance(runners, dict):
        raise ConfigError(f"'runners' in {path} must be an object")
    for lang, spec in runners.items():
        if not isinstance(spec, dict):
            raise ConfigError(f"runner '{lang}' in {path} must be an object")
        command = spec.get("command")
        if not isinstance(command, list) or not command:
            raise ConfigError(f"runner '{lang}' in {path} needs a non-empty 'command' list")
        if not all(isinstance(part, str) for part in command):
            raise ConfigError(f"runner '{lang}' command in {path} must be a list of strings")
        ext = spec.get("ext", ".txt")
        if not isinstance(ext, str):
            raise ConfigError(f"runner '{lang}' 'ext' in {path} must be a string")
        aliases = spec.get("aliases", [])
        if not isinstance(aliases, list) or not all(isinstance(a, str) for a in aliases):
            raise ConfigError(f"runner '{lang}' 'aliases' in {path} must be a list of strings")
        config.register([lang, *aliases], command, ext)


def _apply(config: Config, data: dict, path: Path) -> None:
    if "runners" in data:
        _apply_runners(config, data["runners"], path)

    if "output_languages" in data:
        langs = data["output_languages"]
        if not isinstance(langs, list) or not all(isinstance(x, str) for x in langs):
            raise ConfigError(f"'output_languages' in {path} must be a list of strings")
        config.output_languages = {x.lower() for x in langs}

    if "timeout" in data:
        timeout = data["timeout"]
        if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or timeout <= 0:
            raise ConfigError(f"'timeout' in {path} must be a positive number")
        config.timeout = float(timeout)

    if "ignore" in data:
        ignore = data["ignore"]
        if not isinstance(ignore, list) or not all(isinstance(x, str) for x in ignore):
            raise ConfigError(f"'ignore' in {path} must be a list of strings")
        config.ignore = list(ignore)


def load_config(config_path: str | None = None, start_dir: str | None = None) -> Config:
    """Load configuration, layering ``.mdverify.json`` over the defaults.

    When ``config_path`` is given it must exist. Otherwise ``.mdverify.json`` is
    looked for in ``start_dir`` (defaulting to the current directory); it is
    optional.
    """
    config = default_config()

    if config_path is not None:
        path = Path(config_path)
        if not path.is_file():
            raise ConfigError(f"config file not found: {config_path}")
    else:
        base = Path(start_dir) if start_dir else Path.cwd()
        path = base / CONFIG_FILENAME
        if not path.is_file():
            return config

    _apply(config, _read_json(path), path)
    return config
