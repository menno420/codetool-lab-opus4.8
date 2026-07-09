# codetool-lab-opus4.8 · status
updated: 2026-07-09T17:30Z
phase: mdverify v0.1.0 shipped + iterated on main (PR #2/#4/#6 merged, main CI green); gen-1 self-review retro (ORDER 003)
health: green (main tip 162e84d: 102 tests pass, ruff + format clean, all 5 CI cells success; fresh-install smoke test passes; README + tutorial self-verify exit 0)
last-shipped: PR #6 (merged, 162e84d) — composite GitHub Action + pre-commit hook for adoption; PR #2 shipped mdverify v0.1.0
blockers: none for the tool; the v0.1.0 git TAG + GitHub RELEASE remain owner-only (see needs-owner)
orders: acked=001,002,003 done=001,002,003
⚑ needs-owner: create the v0.1.0 tag + GitHub Release — no write path from this session (git tag push -> 403; the GitHub MCP surface has no release/tag-creation tool; api.github.com -> 403 "connect the Claude GitHub App"). The dist/ sdist + wheel are built and validated locally, ready to attach. Until the tag exists, install via @main.
notes: ORDER 001 (ship the CLI) + ORDER 002 (land Project-written status, iterate) done. ORDER 003 (gen-1 self-review) answered in docs/retro/self-review-2026-07-09.md, landing via this READY PR. Install now: pipx install "git+https://github.com/menno420/codetool-lab-opus4.8@main". Roadmap in CHANGELOG; design rationale in docs/DECISIONS.md.

Friction/delight (honest): Delight — the tool dogfoods itself in CI and caught a real recursion bug in its own README; the parallel build/review/fix/CI loop was smooth; the adversarial review pass pre-commit caught the macos-13 CI bomb, an unpinned-ruff time-bomb, and a non-UTF-8 traceback before any hit CI. Friction — (1) deprecated macos-13 runners never allocate, so the mac/py3.9 cell hung (dropped it; 3.9 covered on Ubuntu); (2) self-merge to main is human-gated (correct, but adds latency; the owner clicked each PR); (3) the release wall (tag push 403 + no release tool + GitHub App not connected) meant "published" landed as install-from-git@main, with the tag/Release pending owner. Full retro: docs/retro/self-review-2026-07-09.md.
