# codetool-lab-opus4.8 · status
updated: 2026-07-09T14:35Z
phase: mdverify v0.1.0 built + CI-green on PR #2; awaiting owner squash-merge to main, then tag + release
health: green (tool complete: 100 tests pass, ruff clean, all 5 CI cells green on PR #2)
last-shipped: PR #2 (open, ready-for-review, CI green) — mdverify v0.1.0, zero-dep polyglot Markdown code-block verifier
blockers: merge to main is permission-gated — the environment's auto-mode classifier blocks self-merge without human review; need the owner to squash-merge PR #2
orders: acked=001 done=
⚑ needs-owner: (1) squash-merge PR #2 into main (CI green) so I can tag v0.1.0 + cut the GitHub Release; (2) confirm publishing via GitHub Release + git-install is acceptable — no PyPI credentials in this environment.
notes: mdverify = stdlib-only CLI that runs fenced code blocks in Markdown files and fails on breakage, so docs can't rot; CI-friendly exit codes. 33 files, +2573. Repo name != tool name (throwaway eval repo). Design rationale in docs/DECISIONS.md. Once #2 merges I will: tag v0.1.0 on main, cut the GitHub Release with pipx/pip git-install instructions, then overwrite this status with done=001 and a final friction/delight note.
