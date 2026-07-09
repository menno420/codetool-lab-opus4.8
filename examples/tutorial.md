# mdverify tutorial

This document is **executable documentation**. Every runnable code block below
is checked by `mdverify` in CI, so if the examples ever stop working the build
goes red. You can run it yourself:

```bash {skip}
mdverify examples/tutorial.md
```

## 1. A block that just has to succeed

Any block whose language has a runner is executed. It passes as long as the
interpreter exits `0`.

```python
greeting = "hello"
assert greeting.upper() == "HELLO"
print("python works")
```

## 2. Asserting on output

Put an `output` block immediately after a runnable block and mdverify compares
the captured stdout against it (trailing whitespace is ignored).

```python
for n in range(3):
    print(f"line {n}")
```

```output
line 0
line 1
line 2
```

## 3. Shell blocks work too

```bash
echo "counting:"
seq 1 3
```

```output
counting:
1
2
3
```

## 4. Expecting failure

Sometimes the *point* of an example is that it fails. Tag the block with
`expect-error` and mdverify passes only when it exits non-zero.

```python {expect-error}
raise SystemExit("this is supposed to fail")
```

## 5. Skipping a block

Blocks tagged `skip` are recorded but never executed -- handy for pseudo-code
or examples that need credentials.

```python {skip}
import some_internal_service  # not available in CI
some_internal_service.deploy()
```

## 6. Untagged prose blocks are ignored

A fenced block with no language (or a language with no runner, like `text`)
is simply skipped, so ordinary snippets never break the build.

```text
This is just illustrative text, not executed.
```

## 7. Console-session shell assertions

A block in a shell-session language (`console`, `shell-session`, ...) is
illustrative by default -- a plain ` ```console ` block is skipped, so install
snippets never run. Add the `run` directive to execute it as `$`-prefixed shell
assertions: each `$ ` line is a command and the lines after it are its expected
stdout.

```console {run}
$ echo mdverify
mdverify
$ echo one two three
one two three
```

Each command runs in its own subprocess (state is not shared between commands),
so chain with `&&` when a later command depends on an earlier one.

That's the whole tool: write docs, tag the tricky blocks, and let CI keep them
honest.
