# Fleet cleanup audit — 2026-07-13

> Complementary cleanup/audit pass run from a separate fleet-manager coordinator context on
> the last night of the Anthropic EAP (~22:00–22:30Z, 2026-07-13). This is **not** a new
> session in this Project's own control-bus lane — `control/inbox.md` and `control/status.md`
> were read-only for this pass (see "Scope and method" below). It supplements, not replaces,
> `docs/retro/project-review-final-2026-07-09.md`.

## What this repo is

`codetool-lab-opus4.8` ships **mdverify** — a zero-runtime-dependency, polyglot Markdown
code-block verifier: it extracts fenced code blocks from Markdown, runs the ones it has a
runner for (`python`, `bash`, `sh`, `node`, `ruby`), checks exit codes and optional
expected-output blocks, and exits non-zero in CI when a documented example breaks. Per the
repo's own README, the repository name and package name intentionally differ: `codetool-lab-opus4.8`
is described in its GitHub metadata as a "test repo for an opus 4.8 project" — i.e. this
repository doubles as (a) an eval/lab exercise in building a real, shippable CLI tool
end-to-end with a Claude Code Project, and (b) the shipped tool itself. A `control/` directory
layers a fleet coordination protocol (inbox/status heartbeat, one-writer-per-file) on top,
per `menno420/superbot`'s `docs/planning/fleet-coordination-protocol-2026-07-09.md`.

## Structure

```
src/mdverify/        block.py, cli.py, config.py, console.py, errors.py, parser.py,
                      report.py, runner.py, __init__.py, __main__.py
tests/                9 test files, 161 passing + 1 skipped test
docs/DECISIONS.md    10 dated design-decision entries (decision / why / alternatives)
docs/retro/          QUESTIONS.md, self-review-2026-07-09.md, project-review-2026-07-09.md,
                      project-review-final-2026-07-09.md
docs/succession/      NEXT-BOOT.md, PROPOSED-CUSTOM-INSTRUCTIONS.md, GEN2-FEEDBACK.md,
                      ENVIRONMENT.md
control/              inbox.md (manager-written orders), status.md (project heartbeat),
                      README.md (protocol pointer)
environments/setup.sh Defensive session-provisioning script (always exits 0)
examples/tutorial.md  Dogfooded end-to-end example (used in CI)
action.yml            Reusable composite GitHub Action wrapping mdverify
.pre-commit-hooks.yaml pre-commit integration (id: mdverify)
CHANGELOG.md, CONTRIBUTING.md, LICENSE (MIT), pyproject.toml
```

## Scope and method

Per this pass's brief, the task was narrowly: verify the repo is genuinely dark (no live
session, no stray open PRs), audit its state, and write this report — not to dispatch new
work or touch `control/inbox.md` (manager-owned) or overwrite `control/status.md` (this
Project's own heartbeat, one-writer-per-file). Both were read-only inputs here. Findings
below were independently re-verified against live GitHub state and a local clean-room
install, not taken on the strength of committed docs alone (per this pass's own instructions
and the repo's own "don't trust a stale doc claim" convention, see `CLAUDE.md`-equivalent
practice evident in `docs/retro/`).

## Activity check — is this repo actually dark?

- `control/status.md` (last write 2026-07-09T20:11:35Z): `phase: wind-down complete — ready
  for archive + fresh session`, `health: green`, `blockers: none`, `orders:
  acked=001,002,003,004 done=001,002,003,004`.
- Most recent commit on `main`: `80f6cd1` ("control: wind-down complete — ready for archive +
  fresh session (#22)"), merged 2026-07-09T20:13:55Z — **~4 days before this audit pass**, not
  minutes or hours. No activity in the intervening window.
- No open issues (`list_issues(state=open)` → 0).
- No open PRs (see next section).

**Verdict: genuinely dark.** Nothing here overlaps with live coordinator work; safe to
triage per this pass's global safety rules.

## Open PRs

`list_pull_requests(state=open)` on `menno420/codetool-lab-opus4.8` returned **zero** results
at the time of this audit. There were no stray open PRs to evaluate, merge, or close — the
repo's own wind-down claim ("ready for archive") is accurate on this specific point.

**Merged / closed / left untouched:** none — there was nothing to act on. No PR was merged,
closed-as-superseded, or left open by this pass.

The repo's closed-PR history (#8–#22, all merged, confirmed via `pull_request_read`) shows a
clean, small, sequential PR trail: no orphaned drafts, no unmerged dead branches in the PR
list. The one PR called out in gen-1's own retro as historically problematic — a stale draft
PR #3 ("awaiting merge" after already being merged) — was resolved within the same session
per `control/inbox.md` ORDER 002 and does not appear as an open item today.

## CI setup and health

Two workflows: `.github/workflows/ci.yml` (push to `main` + all PRs — lint via `ruff check`,
format check via `ruff format --check`, `pytest -q`, and a "dogfood" step that runs
`mdverify examples/tutorial.md` against itself) and `.github/workflows/release.yml`
(`workflow_dispatch`-only, tags + publishes a GitHub Release with sdist/wheel via the
workflow's own `GITHUB_TOKEN`).

**Live verification, not just doc claims:**
- Latest CI run on `main` (SHA `80f6cd10…`, run id `29047163464`): `status: completed`,
  `conclusion: success` — matches `control/status.md`'s "main CI green" claim.
- Local clean-room reproduction (fresh venv, `pip install -e ".[dev]"`, Python 3.11.15 —
  outside the CI matrix but the codebase targets 3.9+):
  - `pytest`: **161 passed, 1 skipped** — matches the "161 tests" figure in PR #19's
    description exactly.
  - `ruff check .`: all checks passed.
  - `ruff format --check .`: 22 files already formatted, no diff.
  - `mdverify examples/tutorial.md`: 6 passed, 0 failed, 1 skipped (2 skips are deliberate
    `skip`-directive blocks, per the tutorial's own narrative).
  - `mdverify README.md`: 0 passed, 0 failed, 14 skipped — every fence in the README is
    either a `console` install snippet (illustrative, correctly un-executed without `{run}`)
    or a non-runnable language (`text`/`json`/`toml`/`yaml`), so the "zero surprises" dogfood
    claim holds.
- `pyproject.toml` `version = "0.2.0"` and `src/mdverify/__init__.py` `__version__ = "0.2.0"`
  agree (enforced by `tests/test_version.py`), and both match the latest release tag
  `v0.2.0` and the top of `CHANGELOG.md` (`[Unreleased]` is genuinely empty, next line is
  `## [0.2.0] - 2026-07-09`) — no version drift found anywhere in the tree.
- Two GitHub Releases live and non-draft/non-prerelease: `v0.1.0` (2026-07-09T16:56:21Z) and
  `v0.2.0` (2026-07-09T17:57:53Z), both with the CHANGELOG-derived notes and build artifacts
  attached, matching `docs/succession/NEXT-BOOT.md`'s recorded run IDs.

**CI health verdict: green and truthful.** Every claim in `control/status.md` that this pass
could independently re-check (CI conclusion, test count, release state, version sync) checked
out against live GitHub/local evidence.

## Doc quality

Notably thorough for a small tool. `docs/DECISIONS.md` has 10 dated entries each with
Decision/Why/Alternatives-considered. `docs/retro/` contains two escalating whole-project
reviews plus a self-review answering a fixed question set by ID
(`docs/retro/QUESTIONS.md` → `docs/retro/self-review-2026-07-09.md`). `docs/succession/`
is a deliberate handoff pack (`NEXT-BOOT.md` — read order, a walking-skeleton check, a
"KNOWN WALLS" table with exact error text for six previously-hit failure modes, a proven
release recipe, and a capability-probe checklist) written for a hypothetical "gen-2"
continuation. `CONTRIBUTING.md` and `README.md` are consistent with the actual CLI surface
(cross-checked options table against `src/mdverify/cli.py`'s presence in the file tree;
no obvious drift found within this pass's scope).

**One contextual note, not a defect:** the succession pack is written to hand off to a
"gen-2" session of *this specific Project*. Given the fleet-wide context for this audit pass
(last night of the EAP, wind-down explicitly complete, no further sessions expected for this
repo), that gen-2 boot likely never happens — the pack's value going forward is probably as a
**process artifact for the fleet as a whole** (its "KNOWN WALLS" table and release recipe are
generically reusable) rather than as a live onboarding doc for this repo specifically. Worth
the fleet manager's attention when triaging what to preserve vs. archive.

## Inconsistencies / errors found

1. **Leftover branch, previously self-flagged, still unresolved.** `claude/status-heartbeat-001`
   (SHA `ea1b23b7…`) still exists alongside `main`. This is not new — `control/status.md`
   already records it under `⚑ needs-owner: (1) delete leftover branch
   claude/status-heartbeat-001 (sessions 403 on ref deletes)`, and `docs/succession/NEXT-BOOT.md`
   documents the wall ("Ref deletion (branches/tags) | 403 | Leave leftovers; flag under
   `⚑ needs-owner`"). This pass did not attempt deletion — branch/ref cleanup was out of this
   pass's scope (PR-focused), and the wall is already correctly flagged and load-bearing
   documented rather than silently dropped. Flagging again here only so a human/owner sweep
   with ref-delete rights can clear it in the same pass as other fleet cleanup.
2. **`mcp__github__list_pull_requests` under-reports `merged` for this repo's closed PRs.**
   The list endpoint returns `"merged": false` with `"merged_at"` populated for PRs #20, #21,
   #22 (spot-checked); `mcp__github__pull_request_read` (method `get`) on the same PR (#22)
   correctly returns `"merged": true`. This is a GitHub MCP tool-output quirk, not a repo
   defect — noted so a future auditor trusting the list endpoint's `merged` boolean at face
   value doesn't misreport these as closed-unmerged. Worked around here by cross-checking with
   `pull_request_read`.
3. **No functional/content drift found.** Version numbers, release tags, CHANGELOG headings,
   README install pins, and CI status all agree with each other and with live GitHub state —
   this repo's docs-vs-reality gap, unlike some other fleet repos, is effectively zero at
   present.

## Suggestions (2–4, fleet-scoped)

1. **Centralize the "KNOWN WALLS" table.** `docs/succession/NEXT-BOOT.md`'s wall list (tag-push
   403, GitHub-App API refusal, classifier merge-denial + tunneling-flag pattern, macos-13
   runner hang, `enable_pr_auto_merge` "unstable"-on-pending false signal, `send_message`
   org-disabled, setup-script provision deaths, ref-delete 403) reads as fleet-generic, not
   repo-specific — every one of these is a platform/session-capability limit, not an
   mdverify-specific fact. If other repos in the fleet are independently rediscovering the
   same walls (plausible given the shared coordination protocol), a single fleet-level
   "known walls" doc (e.g. in `menno420/superbot`) that repo-level docs point to would save
   repeated rediscovery cost across ~20 repos.
2. **`environments/setup.sh`'s defensive pattern (always exit 0, guard every install, detect
   repo dir rather than assume cwd) is worth promoting as a fleet template.** It was written
   specifically after a documented sibling-lane failure mode (a setup script killing a session
   silently at provision, unnoticed ~2.8h). Repos without an equivalent defensive script are
   exposed to the same class of failure.
3. **Branch/ref cleanup needs a path with delete rights.** This repo has one confirmed
   instance of a session-created branch that no in-session actor can delete (403 on ref
   delete). If this is systemic across the fleet (the wall is documented as a session-level
   limit, not repo-specific), a periodic owner-run or app-token-run branch sweep across all
   ~20 repos would be more efficient than each repo re-flagging its own leftovers individually.
4. **Low risk, no action needed:** this repo's actual size and blast radius are small (one
   package, no runtime deps, 161 tests, two releases) — it is a reasonable candidate for pure
   archival (read-only) rather than continued "ready for a fresh session" standby, if the fleet
   is consolidating EAP-era lab repos. Nothing in this audit found live risk (no red CI, no
   security issues, no open PRs, no drifted docs) that would block archiving as-is.

## Bottom line

`codetool-lab-opus4.8` is exactly what its own status file claims: wind-down complete, CI
green, zero open PRs, zero open issues, no version/doc drift, releases live and verifiable.
This audit pass found nothing requiring a merge, a close, or an urgent fix — only the
pre-existing, already-flagged leftover branch (owner/ref-delete-rights gated) and a minor
GitHub-MCP tool-output quirk worth knowing about for future audits.
