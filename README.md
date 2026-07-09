# mdverify

**Keep the code in your docs from rotting.** `mdverify` extracts fenced code
blocks from Markdown files, runs the runnable ones through per-language runners,
and fails your build when an example stops working.

[![CI](https://github.com/menno420/codetool-lab-opus4.8/actions/workflows/ci.yml/badge.svg)](https://github.com/menno420/codetool-lab-opus4.8/actions/workflows/ci.yml)

> **Note on names:** the tool is `mdverify`; it lives in the throwaway eval repo
> `menno420/codetool-lab-opus4.8`. That is why the install URLs below point at a
> repo with a different name.

---

## The problem

Documentation lies. A README shows a snippet, someone renames a flag six months
later, and now the very first thing a new user copy-pastes is broken. Unit tests
don't cover your docs, and keeping examples in sync by hand never lasts.

`mdverify` treats your Markdown as a test suite:

- It finds every fenced code block.
- It runs the ones it has a runner for (`python`, `bash`, `node`, ...).
- It checks the exit code, and — if you provide one — the expected output.
- It returns a CI-friendly exit code so a broken example turns the build red.

It is **polyglot** (not just Python) and **Markdown-native** (no REPL
transcripts), with **zero runtime dependencies** — pure standard library.

## Install

`mdverify` is a single, zero-dependency Python package (3.9+). Install it straight from
this repository with [pipx](https://pipx.pypa.io) (recommended — isolated) or pip:

```console
$ pipx install "git+https://github.com/menno420/codetool-lab-opus4.8@v0.1.0"
# or
$ pip install "git+https://github.com/menno420/codetool-lab-opus4.8@v0.1.0"
```

To track the latest development version instead, swap `@v0.1.0` for `@main`.

From source (for development):

```console
$ git clone https://github.com/menno420/codetool-lab-opus4.8
$ cd codetool-lab-opus4.8
$ pip install -e ".[dev]"
```

> The tool is named **`mdverify`**; the repository (`codetool-lab-opus4.8`) is a throwaway
> capability-evaluation repo, which is why the two names differ.

## Quickstart

```console
# check a single file
$ mdverify README.md

# check a whole directory tree (all *.md / *.markdown)
$ mdverify docs/

# check the current directory (the default)
$ mdverify
```

Example output:

```text
docs/guide.md
  PASS  docs/guide.md:12  python
  PASS  docs/guide.md:31  bash
  SKIP  docs/guide.md:48  text
2 passed, 0 failed, 1 skipped in 0.14s (1 file)
```

## Directives

Add directives to a block's info string to control how it is run. Both bare and
brace-wrapped forms work:

    ```python skip
    ```python {expect-error timeout=5}

| Directive           | Effect                                                              |
| ------------------- | ------------------------------------------------------------------- |
| `skip` / `no-run`   | Record the block but never execute it (reported as `SKIP`).         |
| `expect-error`      | The block **must** exit non-zero; it passes on failure, fails on 0. |
| `timeout=<seconds>` | Override the per-block timeout.                                      |

A block marked `expect-error` is judged purely on its (non-zero) exit code: any
following `output` block is **not** compared, since a block that is expected to
fail has no meaningful stdout to assert.

Unknown info-string tokens (`title="…"`, Pandoc `{.line-numbers}`, etc.) are
ignored, so mdverify coexists with whatever your renderer already uses.

### Output assertions

Put a block whose language is `output` **immediately after** a runnable block
and mdverify compares the captured stdout to it. Trailing whitespace per line
and a single surrounding newline are ignored.

    ```python
    for n in range(3):
        print(n)
    ```

    ```output
    0
    1
    2
    ```

On a mismatch you get a unified diff:

```text
  FAIL  guide.md:5  python
    reason: output did not match the expected block
    exit code: 0
    diff (expected vs actual):
      --- expected
      +++ actual
      @@ -1,3 +1,3 @@
       0
      -1
      +9
       2
```

## Configuration

Configuration is optional. It lives in `.mdverify.json` in the directory you run
from (or pass an explicit path with `-c/--config`). JSON is the portable default
so mdverify works on Python 3.9, which has no `tomllib`.

```json
{
  "runners": {
    "python": { "command": ["python3", "{file}"], "ext": ".py" },
    "deno": { "command": ["deno", "run", "{file}"], "ext": ".ts", "aliases": ["ts"] }
  },
  "output_languages": ["output", "text"],
  "timeout": 30,
  "ignore": ["**/node_modules/**", "CHANGELOG.md"]
}
```

- **`runners`** — map a language to a command template and temp-file extension.
  `{file}` is replaced with the temporary file holding the block; if omitted,
  the path is appended as the final argument. User runners merge over the
  built-ins.
- **`output_languages`** — languages treated as expected-output blocks.
- **`timeout`** — default per-block timeout in seconds.
- **`ignore`** — glob patterns to skip during discovery.

### `pyproject.toml` (Python 3.11+)

On **Python 3.11 or newer** (where the standard-library `tomllib` is available)
you can instead keep the same settings in a `[tool.mdverify]` table in
`pyproject.toml`, so all your tool config lives in one file. The schema is
identical to the JSON above:

```toml
[tool.mdverify]
output_languages = ["output", "text"]
timeout = 30
ignore = ["**/node_modules/**", "CHANGELOG.md"]

[tool.mdverify.runners.python]
command = ["python3", "{file}"]
ext = ".py"

[tool.mdverify.runners.deno]
command = ["deno", "run", "{file}"]
ext = ".ts"
aliases = ["ts"]
```

On Python 3.9/3.10 there is no `tomllib`, so `pyproject.toml` config is silently
ignored and `.mdverify.json` remains the portable default (the runtime stays
zero-dependency — no TOML library is ever installed).

### Config source precedence

Exactly **one** source is used — whichever is found first. Sources are **not**
merged with one another (only over the built-in defaults), keeping resolution
simple and predictable:

1. `-c/--config PATH` — an explicit file. The extension decides the parser:
   `.json` → JSON, `.toml` → `tomllib` (a `pyproject.toml` reads its
   `[tool.mdverify]` table). Pointing `--config` at a `.toml` file on Python
   3.9/3.10 is an error, since `tomllib` is unavailable there.
2. `./.mdverify.json` in the current directory.
3. `./pyproject.toml`'s `[tool.mdverify]` table (Python 3.11+ only, and only
   when that table is present).
4. The built-in defaults.

If both `.mdverify.json` and a `pyproject.toml [tool.mdverify]` table exist, the
JSON file wins.

### Built-in runners

| Language | Aliases            | Command                   | Extension |
| -------- | ------------------ | ------------------------- | --------- |
| python   | `py`, `python3`    | `<current python> {file}` | `.py`     |
| bash     | —                  | `bash {file}`             | `.sh`     |
| sh       | `shell`            | `sh {file}`               | `.sh`     |
| node     | `js`, `javascript` | `node {file}`             | `.js`     |
| ruby     | `rb`               | `ruby {file}`             | `.rb`     |

The `python` runner invokes the **current** interpreter (`sys.executable`), not
a bare `python` on `PATH`, so blocks run under the same Python that mdverify
itself is running on. Override it in `.mdverify.json` if you need a different
one.

A language with no runner is **skipped** by default (so `text`, `json`,
`mermaid`, etc. never break the build). Pass `--require-runner` to turn those
into failures.

## CLI options

| Option                         | Description                                                 |
| ------------------------------ | ----------------------------------------------------------- |
| `PATH...`                      | Files, directories, or globs (default: current directory).  |
| `-c, --config PATH`            | Path to a config file (`.mdverify.json`, or `.toml` on 3.11+). |
| `--ignore GLOB`                | Ignore matching paths (repeatable).                         |
| `--lang LANG`                  | Only run blocks in this language (repeatable).              |
| `--timeout SECONDS`            | Per-block timeout (default: 30).                            |
| `--fail-fast`                  | Stop at the first failing block.                            |
| `--require-runner`             | Treat "no runner" as a failure instead of a skip.           |
| `--format {pretty,plain,json}` | Output format (default: `pretty`).                          |
| `--no-color`                   | Disable ANSI colour (also respects `NO_COLOR`).             |
| `-v, --verbose`                | Show stdout/stderr of passing blocks too.                   |
| `-q, --quiet`                  | Only print failures and the summary.                        |
| `--list`                       | List discovered blocks without running them.                |
| `--version`                    | Print the version.                                          |
| `-h, --help`                   | Show help.                                                  |

## Exit codes

| Code | Meaning                                            |
| ---- | -------------------------------------------------- |
| `0`  | Everything passed (or nothing runnable was found). |
| `1`  | One or more blocks failed or errored.              |
| `2`  | Usage or configuration error.                      |

## Continuous integration

Add a step to your workflow so broken examples fail the build:

```yaml
- name: Verify documentation
  run: |
    pip install "git+https://github.com/menno420/codetool-lab-opus4.8@v0.1.0"
    mdverify README.md docs/
```

## Use it in CI & pre-commit

Two drop-in integrations let you adopt mdverify in a few lines.

### GitHub Action

A reusable composite Action installs mdverify and runs it for you. Point `uses`
at the repo and pass the paths you want checked:

```yaml
# .github/workflows/docs.yml
- uses: menno420/codetool-lab-opus4.8@v0.1.0   # or @main for latest
  with:
    paths: "README.md docs/"
```

Inputs: `paths` (files/dirs to check, default `.`), `args` (extra CLI flags,
e.g. `--format json --fail-fast`), and `python-version` (default `3.x`).

### pre-commit hook

Run mdverify on changed Markdown before every commit via
[pre-commit](https://pre-commit.com):

```yaml
# .pre-commit-config.yaml
- repo: https://github.com/menno420/codetool-lab-opus4.8
  rev: main    # pin to a tag once released
  hooks:
    - id: mdverify
```

## How it compares

- **`doctest`** is Python-only and REPL-transcript-shaped (`>>>` prompts).
  `mdverify` runs plain, copy-pasteable blocks in any language.
- **`pytest-markdown` / `mktestdocs`** are pytest plugins tied to the Python
  ecosystem. `mdverify` is a standalone, dependency-free CLI you can drop into
  any repo — Go, Rust, JS docs included — with one `pip install`.

It intentionally does **not** try to be a full CommonMark renderer; it only
understands fenced code blocks, which is all it needs.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). In short: fork, `pip install -e ".[dev]"`,
make sure `ruff check .` and `pytest` are green, open a PR.

## License

[MIT](LICENSE) © 2026 Menno van Hattum
