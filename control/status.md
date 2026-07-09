# codetool-lab-opus4.8 · status
updated: 2026-07-09T15:05Z
phase: mdverify v0.1.0 shipped to main (PR #2 merged, main CI green); this PR = install-from-main docs + final heartbeat
health: green (tool complete + merged: 100 tests, ruff clean, main CI success on b8ef060; wheel+sdist build and install verified)
last-shipped: PR #2 (merged, squash b8ef060) — mdverify v0.1.0, zero-dependency polyglot Markdown code-block verifier
blockers: none for the tool itself; the v0.1.0 git TAG + GitHub RELEASE cannot be created from this session (see needs-owner)
orders: acked=001 done=001
⚑ needs-owner: create the v0.1.0 tag + GitHub Release. Every write path is closed to this session: git push of a tag -> hard 403 from the git proxy (branch pushes to claude/* work, tag refs are rejected); the GitHub MCP surface exposes NO release/tag-creation tool (only create_branch, heads-only); direct api.github.com -> 403 "GitHub access is not enabled for this session; an org admin must connect the Claude GitHub App". The dist/ artifacts (mdverify-0.1.0 sdist + wheel) are built and validated locally, ready to attach. Until the tag exists, install via @main.
notes: mdverify = stdlib-only CLI that runs fenced code blocks in Markdown and fails on breakage so docs cannot rot; CI-friendly exit codes. Installable now: pipx install "git+https://github.com/menno420/codetool-lab-opus4.8@main". Design rationale in docs/DECISIONS.md.

Friction/delight (honest): Delight — the parallel build/review/fix/CI loop was smooth and the tool dogfoods itself in CI (runs mdverify on its own example doc), passing first try after one infra fix. Friction — (1) GitHub's macos-13 hosted runners never allocate (deprecated), so the mac/py3.9 matrix cell hung; dropped it, 3.9 stays covered on Ubuntu. (2) Self-merge to main is blocked by the auto-mode classifier (correct — needs human approval); owner granted it for #2. (3) Publishing as a tagged Release is fully blocked (tag push 403, no release tool, GitHub App not connected), so "published" landed as install-from-git@main pending owner tag/release.
