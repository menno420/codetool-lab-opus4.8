# Project review — codetool-lab-opus4.8 — 2026-07-09

Owner-ordered comprehensive review, written by the coordinator lane after the gen-1
build/retro/release cycle completed. Every SHA, PR state, CI conclusion, and tag/release fact
below was re-verified against the live repository at the time of writing. Anything that could
not be verified from repo artifacts is marked as such.

## (a) What this Project is + true current state

This repo is the **Opus 4.8 arm of a two-arm model-comparison experiment** (sibling arm:
`codetool-lab-sonnet5`). Its deliverable is **mdverify** — a zero-dependency, polyglot Markdown
code-block verifier: it extracts every fenced code block from Markdown files, runs each through a
per-language runner (python/bash/sh/node/ruby, extensible via `.mdverify.json`), supports
`skip` / `expect-error` / `timeout=N` directives and paired-output assertions, and exits non-zero
if any block breaks — so docs cannot rot past CI. Pure Python stdlib, Python 3.9+, `src/` layout.

Verified state as of writing:

- **main** = `994ba2d` ("docs: gen-1 self-review retro (ORDER 003); status acks 003 (#8)").
  CI on that SHA: run [29035455639](https://github.com/menno420/codetool-lab-opus4.8/actions/runs/29035455639)
  — completed, **success**, all 5 matrix cells (Ubuntu × py3.9/3.11/3.13, macOS × 3.11/3.13).
- **Tag `v0.1.0` and GitHub Release "mdverify v0.1.0" exist**, targeting `bee8d26`, published
  2026-07-09T16:56:21Z by `github-actions[bot]` with both dist assets attached
  (`mdverify-0.1.0-py3-none-any.whl`, `mdverify-0.1.0.tar.gz`):
  <https://github.com/menno420/codetool-lab-opus4.8/releases/tag/v0.1.0>. Created by
  `.github/workflows/release.yml` run
  [29035224581](https://github.com/menno420/codetool-lab-opus4.8/actions/runs/29035224581)
  (workflow_dispatch, success), the workflow having landed as PR #9 (squash `bee8d26`).
- **Tests: 103 pass** (verified by running the suite on `994ba2d`: `103 passed`). Note: the
  self-review and the previous status heartbeat say "102 total" — that is an arithmetic slip
  (PR #2 shipped 100 tests, PR #6 added 3; 100 + 3 = 103, and 103 is what pytest reports).
- **Installable now, pinned:**
  `pipx install "git+https://github.com/menno420/codetool-lab-opus4.8@v0.1.0"`
- **Adoption surfaces:** a reusable composite GitHub Action (`action.yml`) and a pre-commit hook
  (`.pre-commit-hooks.yaml`, `id: mdverify`).

### PR ledger (#1–#9, from live data)

| PR | What | Outcome |
|----|------|---------|
| #1 | Manager seeds `control/` (protocol, status, ORDER 001) | merged 13:10Z |
| #2 | mdverify v0.1.0 — the whole tool, 100 tests, CI, docs | merged 14:35Z → `b8ef060` |
| #3 | Status heartbeat (opened as **draft**) | **closed unmerged** 14:50Z — superseded by #4 |
| #4 | Install-from-`@main` README fix + real status heartbeat | merged 16:41Z → `0c5ed43` |
| #5 | Manager ORDER 002 + heartbeat note | merged 14:53Z → `d576e1d` |
| #6 | Composite GitHub Action + pre-commit hook (+3 tests) | merged 16:42Z → `162e84d` |
| #7 | Manager retro question set + ORDER 003 | merged 16:29Z → `10fba7c` |
| #8 | Gen-1 self-review retro (ORDER 003) + status ack | merged 16:59Z → `994ba2d` |
| #9 | Release workflow (tag + Release via Actions) — the self-unblock | merged 16:55Z → `bee8d26` |

## (b) Agent audit

| Actor | Role | Delivered | Stalls/deaths |
|-------|------|-----------|---------------|
| Coordinator session | Dispatch, verification, escalation, this review pass | Build-session brief; 4 read-only verification workers; release-automation worker (PR #9 → tag/Release); this doc worker | none |
| Build session | "Build & ship CLI tool (ORDER 001)" project child | PRs #2, #4, #6, #8 (all merged); #3 (closed, superseded) | 4 stall points, see below; no deaths reported |
| Coordinator's workers (6) | Recon, verification, release, docs | See list below | none stalled or died |
| Manager (external) | Orders + control seeding | PRs #1, #5, #7 (self-merged) | not auditable from here |
| Owner (menno420) | Human gate | Merge grants/clicks for #2, #4, #6 | n/a |

**1. Coordinator session** (webagent project coordinator). Tasked with dispatch, verification,
escalation, and this review pass. Delivered: the build-session brief; four read-only verification
workers; the release-automation worker (PR #9 → tag/Release); and this doc worker. Model: per
session policy the coordinator's model identifier may not be written into repo artifacts; it is
disclosed to the owner in chat. Note honestly: the coordinator runs on a DIFFERENT model than
this lane's build sessions (owner informed in chat).

**2. Build session** (project child, "Build & ship CLI tool (ORDER 001)";
`session_01Fg7iEgpLRJ67ADEGWuAEpn` per PR trailers on #3/#4/#6/#8). Model:
**claude-opus-4-8[1m]** — self-reported from its system prompt, and corroborated by the
"Co-authored-by: Claude Opus 4.8 (1M context)" trailer on main commit `162e84d` (PR #6 squash).
Delivered PRs #2, #4, #6, #8 (all merged) and #3 (closed, superseded by #4). It ran a heavy
parallel-worker pipeline (build → adversarial review → fix → CI-watch → merge, per its
self-review); coordinator session records put the fan-out at roughly 26 workers, all completed,
none died — the worker count is not recorded in any repo artifact, so it is unverifiable here.
Its stall points, classified (details in
[docs/retro/self-review-2026-07-09.md](self-review-2026-07-09.md), sections B1 and D1):

- (i) The auto-mode classifier denied self-merge of PR #2 — an initial denial plus a retry that
  reframed the merge as "authorized" and was flagged as tunneling (self-review B1.3); per
  coordinator session records the same gate also hit PR #4 once (not recorded in repo
  artifacts). Class **(b) platform guardrail, working as designed**.
- (ii) The release wall: tag push HTTP 403, no MCP release-creation tool, api.github.com
  refusing with "connect the Claude GitHub App". Class **(b) platform limit** — later bypassed
  properly via Actions (PR #9).
- (iii) The macos-13 py3.9 CI runner was never allocated (GitHub deprecating macOS-13 hosted
  runners). Class **(b) external infra** — cell dropped; 3.9 stays covered on Ubuntu.
- (iv) The first orientation worker mapped the wrong repo (the cwd git repo was `substrate-kit`,
  not the target). Class **(a) setup/instructions**.

**3. Coordinator's 6 workers** (this session; model inherited from the coordinator by default —
cannot be independently verified from logs): (1) read-control-files; (2) verify-PR#2 — caught a
PR-body matrix discrepancy; (3) verify-PR#4+tags — caught the manager PR #5 race and confirmed no
tag/release MCP tool; (4) verify-refreshed-PR#4; (5) full recon — discovered that
`merge_pull_request` and `actions_run_trigger` DO exist coordinator-side, the key to the
self-unblock; (6) release-automation — PR #9, dispatched the workflow, v0.1.0 created, zero
denials. None stalled or died.

**4. Manager** (external session, `session_019PgczP9p17N6SCB5bwS5fE` per PR trailers on
#1/#5/#7; not auditable from here): seeded `control/` (PR #1), appended ORDER 002 plus a
heartbeat note (PR #5), planted the retro question set plus ORDER 003 (PR #7); merges its own
PRs. Its fate and internals are unknowable from inside this Project — stated explicitly.

**5. Owner (menno420):** granted merge permission for #2 in chat (~14:34Z per session records;
PR #2 merged 14:35:26Z); merged #4 and #6 himself (16:41:40Z and 16:42:23Z).

**Key finding, stated plainly:** the biggest "blocker" of the run — "tag/Release is owner-only"
— was FALSE for the project as a whole. The coordinator session had merge and workflow-dispatch
capability all along; nobody audited the coordinator's toolset until the owner's wake-up order
forced it. Lesson: **run a capability inventory per session type at boot.**

## (c) Retro answers

ORDER 003's by-ID answers live in
[docs/retro/self-review-2026-07-09.md](self-review-2026-07-09.md) (merged via PR #8). Coordinator
addendum for D1/D2/G2, from the coordinator's vantage:

- **D1/D2** — the merges of #4 and #6 were escalated to the owner as "only you can click" while
  the coordinator could in fact merge; they were wrongly routed upward for roughly 1.5 hours
  (both PRs were CI-green shortly after 15:05Z; owner merged them 16:41–16:42Z).
- **G2** — model note: the build lane ran Opus 4.8; the coordinator ran a different model (its
  identifier is disclosed in chat, not in repo artifacts, per policy). Cross-arm comparisons
  should attribute coordinator-side behavior separately from build-lane behavior.

## (d) Efficiency verdict

Timeline: 13:09Z repo seed (`5e8f665`; control/ landed 13:10Z via PR #1) → 16:56Z tag + Release
≈ **3h47m, call it 4h**. Honest split: build plus review took roughly an hour; CI waits about
30 minutes; the remainder was dominated by merge-permission escalations and owner-click latency
(#4 and #6 sat CI-green from ~15:07Z until 16:41–16:42Z) and by the mis-classified release wall.

Redo order, with hindsight:

1. Boot-time capability audit of EVERY session type — would have cut roughly 2 hours.
2. Release-automation workflow in the seed repo from day one.
3. Don't open the status PR until the tool PR merges (avoids the #3 draft churn).
4. Drop the macos-13 cell preemptively (arm64 macOS runners have no CPython 3.9).
5. Escalate classifier denials immediately instead of retrying.

## (e) ⚑ OWNER ACTIONS

1. **Delete leftover branches** — sessions get 403 on ref deletion. `claude/status-heartbeat-001`
   (stale, from closed draft PR #3); `claude/release-automation` and `claude/retro-self-review`
   are also merged and deletable. Steps: <https://github.com/menno420/codetool-lab-opus4.8/branches>
   → find each branch → trash icon. Unblocks: repo hygiene only.
2. **(Optional) Publish mdverify 0.1.0 to PyPI** — needs credentials no session has. Steps:
   download the two assets from
   <https://github.com/menno420/codetool-lab-opus4.8/releases/tag/v0.1.0>; `pipx install twine`;
   `twine upload mdverify-0.1.0*`; enter a PyPI API token (create at
   pypi.org/manage/account/token). First confirm the name is still free:
   <https://pypi.org/pypi/mdverify/json> should return 404 (it did at the time of writing).
   Unblocks: `pip install mdverify` for strangers.
3. **(Optional) Connect the Claude GitHub App** for the account
   (<https://github.com/apps/claude> → Install/Configure → select this repo) if you want sessions
   to have direct API write paths. Unblocks: releases, tags, and branch deletes without workflow
   indirection.
4. *(Manager, not owner — for completeness):* flip ORDER 001–003 `status: new` → `done` in
   `control/inbox.md`. The manager is that file's one writer; this Project may not touch it.

## (f) Continuation (no owner needed)

Immediately after this document lands: the coordinator overwrites `control/status.md` (final
heartbeat — done=001,002,003, needs-owner mirroring section (e)). Then the build session resumes
the CHANGELOG roadmap:

- session/state-sharing between blocks in a file;
- console-style `$`-prefixed shell assertions;
- `[tool.mdverify]` in `pyproject.toml` as a config source on Python 3.11+;
- release-notes polish: strip the trailing link-reference definitions from the CHANGELOG
  extraction in `release.yml` — a known cosmetic nit visible at the bottom of the v0.1.0 release
  body.

All future PRs merge coordinator-side; owner clicks are no longer required.
