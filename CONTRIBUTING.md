# Contributing to mdverify

Thanks for your interest in improving `mdverify`. It's a small, focused,
dependency-free tool, and the goal is to keep it that way.

## Development setup

```bash
git clone https://github.com/menno420/codetool-lab-opus4.8
cd codetool-lab-opus4.8
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## The checks

Everything CI runs, you can run locally:

```bash
ruff check .          # lint
ruff format --check . # formatting
pytest -q             # tests
mdverify examples/tutorial.md   # dogfood: the docs must still pass
```

Please make sure all four are green before opening a pull request. Run
`ruff format .` to auto-format.

## Guiding principles

- **Standard library only** for the runtime package (`src/mdverify`). New
  runtime dependencies will not be accepted. `pytest` and `ruff` are the only
  dev dependencies.
- **Small, single-purpose functions** with clear names and real error messages.
- **Python 3.9+** compatibility. Use `from __future__ import annotations` and
  avoid 3.10+-only runtime constructs.
- Every behaviour change comes with a test.

## Adding a runner

Built-in runners live in `src/mdverify/config.py` in `_DEFAULT_SPECS`. Each
entry is `(names, command, ext)`:

- `names` — the canonical language name first, then aliases.
- `command` — an argv template; `{file}` is replaced with the temp file path
  (appended if the placeholder is absent).
- `ext` — the temp-file extension.

Add a test in `tests/test_config.py` (resolution/aliases) and, if the
interpreter is guaranteed on CI runners, an execution test. Do **not** add tests
that require `node` or `ruby` to be installed — those are optional.

Users can also add runners without touching the code, via `.mdverify.json`.

## Code style

- Formatting and linting are enforced by `ruff` (config in `pyproject.toml`).
- Keep public API changes reflected in `src/mdverify/__init__.py` and the README.
- Update `CHANGELOG.md` under `## [Unreleased]`.

## Pull request process

1. Create a feature branch off `main`.
2. Make your change with tests and docs.
3. Ensure lint, format, tests, and the dogfood run all pass.
4. Open a PR describing the change and its motivation.
5. Once CI is green and the PR is approved, it is **squash-merged**.

## Commit conventions

Use short, imperative subject lines, ideally
[Conventional Commits](https://www.conventionalcommits.org/) style:

```text
feat: add deno runner
fix: handle unterminated tilde fences
docs: clarify output-assertion normalisation
test: cover --require-runner exit code
```
