# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-07-09

### Added

- Reusable composite **GitHub Action** (`action.yml`) that installs and runs
  mdverify, with `paths`, `args`, and `python-version` inputs.
- **pre-commit hook** (`.pre-commit-hooks.yaml`, `id: mdverify`) that runs the
  code blocks in changed Markdown files, for easy CI/pre-commit adoption.
- **`[tool.mdverify]` in `pyproject.toml`** as an additional config source on
  Python 3.11+ (read with the standard-library `tomllib`), using the same schema
  as `.mdverify.json`. `.mdverify.json` remains the portable default; on Python
  3.9/3.10 pyproject config is silently skipped and no TOML dependency is added.
- **Opt-in `console`-style shell assertions.** A console-session block
  (`console`, `shell-session`, `shellsession`, `sh-session`) marked with the new
  `run` (alias `exec`) directive is executed as `$`-prefixed shell assertions:
  each `$ ` command runs (a `> ` line continues a multi-line command) and its
  stdout is checked against the following lines, failing on a non-zero exit or an
  output mismatch (unified diff). Console blocks **without** `run` remain
  illustrative and skipped, so existing snippets never execute. Commands run in
  independent subprocesses (state is not shared). Adds `console_languages` and
  `console_shell` config keys (JSON and `pyproject.toml`).
- **Session state-sharing** between blocks via a `session=NAME` directive. Blocks
  in one file that share a session name are concatenated in document order and
  run **once** as a single script, so later blocks see earlier blocks' variables,
  imports, and shell state; the session passes iff the combined run exits `0` and
  is reported as one result anchored at the first member (with the session name
  and member count). All members must be one language (mixing is a clear error);
  `skip` excludes a member (all-skipped → skipped); output assertions and
  `expect-error` do not combine with sessions in v1. Blocks without `session=`
  are unchanged. `--list` shows each session as a grouped unit.

## [0.1.0] - 2026-07-09

### Added

- Fenced code block parser supporting backtick and tilde fences, fences longer
  than three characters, indented fences with dedenting, and graceful handling
  of unterminated fences.
- Info-string / directive parsing: `skip` (aliases `no-run`, `mdverify-skip`),
  `expect-error`, and `timeout=<seconds>`, with unknown tokens ignored.
- Per-language runner registry with built-ins for `python`, `bash`, `sh`,
  `node`, and `ruby`, including aliases.
- Output assertions via a paired `output` block, with unified-diff reporting on
  mismatch.
- `.mdverify.json` configuration: custom runners, output languages, timeout, and
  ignore globs.
- CLI with file/directory/glob discovery, `--lang`, `--timeout`, `--fail-fast`,
  `--require-runner`, `--ignore`, and `pretty` / `plain` / `json` output.
- CI-friendly exit codes (0 pass, 1 failure, 2 usage/config error).
- Zero runtime dependencies — standard library only, Python 3.9+.

[Unreleased]: https://github.com/menno420/codetool-lab-opus4.8/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/menno420/codetool-lab-opus4.8/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/menno420/codetool-lab-opus4.8/releases/tag/v0.1.0
