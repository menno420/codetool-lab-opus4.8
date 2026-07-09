# Design decisions

A log of the significant decisions behind `mdverify` and the reasoning at the
time. Each entry records the **Decision**, **Why**, and **Alternatives
considered**.

## 1. Python + standard library only

- **Decision:** Implement the runtime package with the Python standard library
  and no third-party runtime dependencies. `pytest` and `ruff` are dev-only.
- **Why:** A doc-linting tool is infrastructure — it should install instantly,
  never drag a dependency tree into someone's CI, and never itself be a source
  of supply-chain risk or version conflicts. `subprocess`, `argparse`,
  `tempfile`, `difflib`, and `json` cover everything the tool needs.
- **Alternatives considered:** `click`/`typer` for the CLI (nicer ergonomics but
  a dependency and a heavier install); `rich` for output (colour is a handful of
  ANSI codes we can emit directly).

## 2. Name: `mdverify`

- **Decision:** Call the tool `mdverify`.
- **Why:** It says exactly what it does (verify Markdown), is short, and reads
  well as a CLI command. Checked as free on PyPI and clean as a GitHub project
  name at the time of writing.
- **Alternatives considered:** `doctestmd`, `mdcheck`, `mdrun` — either taken,
  ambiguous (`mdcheck` reads like a linter), or misleading (`mdrun` implies it
  runs the whole document as a program).

## 3. JSON config, with `pyproject.toml` as a 3.11+ opt-in

- **Decision:** `.mdverify.json` (parsed with `json`) is the portable default
  config. Additionally, on Python 3.11+, a `[tool.mdverify]` table in
  `pyproject.toml` is accepted, parsed with the standard-library `tomllib`.
- **Why:** The support floor is Python 3.9, which has no `tomllib` (added in
  3.11). Making TOML the *only* format would force either a 3.11 floor or a
  `tomli` dependency — the latter breaks decision #1. So `json` remains the
  always-available default, adequate for the small schema and working on 3.9+.
  The `pyproject.toml` support is a pure convenience layered on top: it reuses
  the exact same schema and validation path (parse TOML → same dict → same
  validator), needs no third-party dependency (`tomllib` is stdlib on 3.11+),
  and is **silently skipped** on 3.9/3.10 where `tomllib` is absent — so the
  original rationale (3.9 support without a dependency) still holds fully.
- **Precedence (updated):** exactly one source is used and sources are never
  merged: `--config` file → `./.mdverify.json` → `./pyproject.toml
  [tool.mdverify]` (3.11+ only) → built-in defaults. If both a JSON file and a
  pyproject table exist, the JSON file wins.
- **Alternatives considered:** Making TOML the sole format (breaks 3.9 or the
  zero-dependency rule); a `tomli` backport dependency for 3.9/3.10 (rejected —
  decision #1); merging across sources (rejected — less predictable than
  first-source-wins).

## 4. Independent-block execution model (v0.1.0)

- **Decision:** Each runnable block executes in its own fresh subprocess with no
  shared state between blocks.
- **Why:** It is simple, predictable, and language-agnostic — a block is a
  self-contained temp file handed to an interpreter. Shared state across blocks
  requires a persistent session per language (a REPL or a serialised namespace),
  which is complex, language-specific, and easy to get subtly wrong.
- **Alternatives considered:** Concatenating all blocks of a language into one
  program (couples unrelated examples and scrambles line numbers); a persistent
  per-language session (deferred — tracked as a roadmap item).

## 5. Skip unknown languages by default

- **Decision:** A block whose language has no configured runner is **skipped**,
  not failed, unless `--require-runner` is passed.
- **Why:** Real docs are full of non-executable fences — `text`, `json`, `yaml`,
  `mermaid`, `diff`. Failing on those would make the tool unusable out of the
  box and punish perfectly good documentation. Opt-in strictness
  (`--require-runner`) serves teams that want every fence accounted for.
- **Alternatives considered:** Fail by default (too noisy); require an explicit
  allowlist of languages (more configuration for the common case).

## 6. Output assertions via a paired `output` block

- **Decision:** Expected stdout is expressed as a block whose language is
  `output`, placed immediately after the runnable block. Comparison strips
  trailing whitespace per line and one surrounding newline.
- **Why:** It is Markdown-native and renders as an ordinary code block, so the
  docs still read naturally. Tying it to document order avoids inventing a
  cross-reference syntax. The normalisation absorbs the whitespace differences
  that otherwise make output assertions maddeningly brittle. A block marked
  `expect-error` is exempt: it is judged only on its non-zero exit code, so any
  following `output` block is not compared (an example expected to fail has no
  meaningful stdout to assert).
- **Alternatives considered:** Inline `# =>`-style expected-output comments
  (language-specific, clutters the code); doctest-style interleaved transcripts
  (not copy-pasteable, Python-flavoured).

## 7. Console-session assertions are opt-in via a `run` directive

- **Decision:** A console-session block (`console`, `shell-session`, ...) is
  treated exactly as before — illustrative and **skipped** — unless it also
  carries a `run` (alias `exec`) directive, in which case it is executed as
  `$`-prefixed shell assertions. Each `$ ` command runs in its **own**
  subprocess (state is not shared across commands within a block).
- **Why:** ` ```console ` fences are overwhelmingly used for *illustrative*
  transcripts — install snippets (`$ pipx install ...`), REPL sessions, output
  no one intends to re-run. Auto-executing every console block would run this
  repo's own README install commands and break countless existing docs, making
  the feature impossible to adopt. Gating execution behind an explicit `run`
  opt-in preserves 100% backward compatibility (`mdverify README.md` stays
  green) while giving authors a way to *assert* on a session when they mean to.
  Per-command independent execution mirrors decision #4 (the independent-block
  model): it is simple, predictable, and language-agnostic. Shared state across
  commands needs a persistent shell session, which is a separate, more complex
  feature (tracked as a roadmap item); authors who need it today chain commands
  with `&&`.
- **Alternatives considered:** Auto-running all console blocks (rejected —
  breaks illustrative snippets and backward compat); a separate `console-run`
  language instead of a directive (rejected — a directive composes with the
  existing `skip`/`timeout` machinery and keeps the language token honest to what
  renderers highlight); sharing a shell process across commands in a block
  (deferred to the session-sharing feature — see decision #4).

## 8. CI matrix: 2 OS × 3 Python versions

- **Decision:** Test on `ubuntu-latest` and `macos-latest` across Python 3.9,
  3.11, and 3.13.
- **Why:** Covers the oldest supported version, a mid version, and the newest,
  on the two Unix-like platforms the tool's subprocess model targets. Execution
  tests rely only on `python3` and `bash`, which both runners provide; `node`
  and `ruby` are deliberately not required.
- **macOS 3.9 exception:** `macos-latest` is now arm64, and `actions/setup-python`
  publishes no arm64 CPython 3.9 build, so that combination is **excluded**.
  Python 3.9 is covered on `ubuntu-latest`; macOS coverage is 3.11 and 3.13. A
  `macos-13` (Intel) cell for 3.9 was dropped because GitHub's macOS-13 hosted
  runners are being deprecated and fail to allocate, leaving CI perpetually
  pending. `fail-fast: false` keeps one leg's failure from cancelling the rest of
  the matrix.
- **Alternatives considered:** Adding Windows (the built-in `bash`/`sh` runners
  assume a POSIX shell, so it would need conditional test skips — deferred);
  testing every minor version (slower for little added signal).

## 9. Publishing via GitHub Release + git install

- **Decision:** Distribute from the Git repository (`pip`/`pipx install
  "git+https://…@v0.1.0"`) rather than PyPI for v0.1.0.
- **Why:** No PyPI credentials are available in this environment, and a tagged
  GitHub release is a fully working, verifiable install path. The build backend
  is `hatchling`, so publishing to PyPI later is a single `hatch publish` away
  with no packaging changes.
- **Alternatives considered:** Publishing to PyPI now (blocked on credentials —
  **flagged**); a Homebrew formula or standalone binary (overkill for a
  stdlib-only Python CLI).
