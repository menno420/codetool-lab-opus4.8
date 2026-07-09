# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Roadmap / ideas under consideration:

- **Session state-sharing** between blocks in a file (opt-in), so a later block
  can build on variables defined earlier.
- **`console`-style shell assertions**: `$`-prefixed commands with inline
  expected output in a single block.
- **`[tool.mdverify]` in `pyproject.toml`** as an alternative config source on
  Python 3.11+ (via `tomllib`), keeping JSON as the portable default.

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

[Unreleased]: https://github.com/menno420/codetool-lab-opus4.8/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/menno420/codetool-lab-opus4.8/releases/tag/v0.1.0
