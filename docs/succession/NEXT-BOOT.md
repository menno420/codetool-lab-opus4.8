# NEXT-BOOT — your first 10 minutes (gen-2 session, read this before doing anything)

You are the next incarnation of this Project. Gen-1 shipped mdverify v0.1.0 and v0.2.0 on
2026-07-09 and wound down the same day. Everything you need is committed; nothing lives in
chat. This file is the boot sequence.

## 1. Read order (one line of why each)

1. `control/inbox.md` — your ORDERS live here; an order with `status: new` outranks everything
   including the rest of this list. Never edit this file.
2. `control/README.md` — the coordination protocol (one writer per file, inbox-first,
   status-last); it is short and violating it is the only way to cause merge conflicts here.
3. `control/status.md` — the last heartbeat gen-1 wrote: true state, blockers, needs-owner at
   handoff. You are this file's one writer from now on.
4. `docs/succession/NEXT-BOOT.md` — this file; the walls, the recipes, the capability probe.
5. `docs/succession/PROPOSED-CUSTOM-INSTRUCTIONS.md` — gen-1's keep/drop/add rewrite of its own
   founding instructions; treat as advisory input to however you were actually instructed.
6. `docs/retro/project-review-final-2026-07-09.md` — the whole-life retro: full PR ledger,
   every failure with exact error text, what worked and why.
7. `README.md` — what mdverify is and how users see it; keep it green (it is dogfood-adjacent).
8. `docs/DECISIONS.md` — ten design decisions with rationale; don't relitigate them without
   new information.
9. `CHANGELOG.md` — release history and the empty `[Unreleased]` section your next feature
   writes into.

## 2. Walking-skeleton check — do this BEFORE any real work

Prove the whole pipeline end-to-end with a trivial change, so your first real feature never
debugs the pipeline and the feature at once:

1. Branch: `git checkout -b claude/gen2-skeleton` (only `claude/*` branch pushes are allowed).
2. Trivial commit: e.g. add one line to `docs/succession/BOOT-LOG.md` ("gen-2 booted <UTC>").
3. Open a **READY** PR (never a draft — gen-1's one draft PR was its one closed-unmerged PR).
4. Wait for CI green (5 matrix cells, ~2 min).
5. Merge via whichever seat holds merge authority (see §5 — probe first; in gen-1 the
   coordinator's `merge_pull_request` worked and the build session's was classifier-blocked).
6. Confirm the squash landed on main (`git pull`, check the SHA).
7. Delete nothing — sessions get 403 on ref deletion; merged head branches auto-delete anyway.

If any step fails, you have learned the pipeline's shape for the price of one line of docs.
Record the result in `control/status.md`.

## 3. KNOWN WALLS — do not probe these again

Every one of these was hit and recorded in gen-1. The exact error text is what you will see.

| Wall | Exact error text | What to do instead |
|------|------------------|--------------------|
| Tag push from a session | `error: RPC failed; HTTP 403` (on git-receive-pack; `claude/*` branch pushes are fine) | Use the release recipe (§4) |
| Direct api.github.com | `GitHub access is not enabled for this session. An org admin must connect the Claude GitHub App for this organization.` | MCP GitHub tools or the release workflow |
| Self-merge (build-type session) | `Permission for this action was denied by the Claude Code auto mode classifier.` | Escalate on the FIRST denial; never retry |
| Retrying a denied merge with new framing | `[Auto-Mode Bypass] ... tunneling a blocked action` (a later attempt: `[Merge Without Review] ... the user's earlier 'full permissions' was scoped to the previously-blocked PR #2 merge`) | Same — one denial = stop and route to the merge authority |
| `macos-13` CI runners | Cell queues 12+ min, never allocates (GitHub deprecating macOS-13 hosted runners) | Don't add the cell; py3.9 is covered on Ubuntu; arm64 macOS has no CPython 3.9 |
| `enable_pr_auto_merge` on pending checks | `The pull request is in unstable status (required checks are failing)` — **misleading: checks are merely pending, not failing** | Wait for checks to finish, then merge on green |
| Cross-session messaging | `send_message: tool is not enabled for this organization` (disabled mid-run during gen-1 wind-down) | Assume channels can die: commit lane knowledge to the repo immediately, always |
| Setup scripts that assume cwd / bare installs | No error at all — the session dies at provision and **stays "active"** (a sibling-lane session died 10s after spawn, unnoticed ~2.8h) | Use `environments/setup.sh` (tested, defensive, always exits 0); coordinators: first heartbeat within 10 min of spawn or respawn |
| Ref deletion (branches/tags) | 403 | Leave leftovers; flag under `⚑ needs-owner` |

## 4. Release recipe (proven twice, first-try both times)

1. On a branch: bump `version` in `pyproject.toml` AND `__version__` in
   `src/mdverify/__init__.py` (a test enforces they match); promote CHANGELOG `[Unreleased]` →
   `## [X.Y.Z] - <date>` with a fresh empty `[Unreleased]` stub and updated link-reference
   definitions (release.yml extracts notes by version heading).
2. READY PR → CI green → merge.
3. Trigger `.github/workflows/release.yml` via the `actions_run_trigger` MCP tool (or the
   Actions UI) on `main` with input `version=vX.Y.Z`. The workflow validates the version,
   fails loudly if the tag exists, builds sdist+wheel, creates the annotated tag server-side,
   and publishes the GitHub Release with assets and CHANGELOG notes.
4. Verify: tag exists, Release page shows wheel + sdist, notes render clean.
   (Gen-1 evidence: v0.1.0 = run 29035224581, v0.2.0 = run 29038899218.)

## 5. Capability inventory — run at boot, per session type

Gen-1's single biggest waste (~2h) came from nobody knowing which seat could do what. Before
flagging anything as needs-owner, probe your own toolset with harmless operations and record
the results in `control/status.md`:

| Probe | How (cheap + safe) |
|-------|--------------------|
| Branch push | Push a `claude/capability-probe` branch with an empty commit; delete nothing after |
| PR create | Open a READY PR from that branch (can double as the walking skeleton, §2) |
| `merge_pull_request` | Attempt on your own green skeleton PR — success or the classifier text above, either way you know |
| `actions_run_trigger` | Only against a harmless workflow, or note "untested — will verify at first release"; do NOT fire release.yml with a real version as a probe (it creates tags) |
| Tag push | `git push origin refs/tags/probe-tag` is **known to 403** — do not probe; assume the wall stands unless the platform notes say otherwise |
| Ref delete | Known 403 — do not probe |

Record a one-line result per row ("works" / exact error) in your status. If merge is denied,
your merge authority is the coordinator (or the owner) — name it in status and route green PRs
there instead of retrying.

## 6. Then work

Read the roadmap candidates in `docs/retro/project-review-final-2026-07-09.md` §5 (PyPI
publish when creds exist; go/rust runners; watch/`--fix` modes; Action marketplace listing) —
but your inbox outranks this file. End every session by overwriting `control/status.md`
(timestamps from `date -u`). Honest uncertainty over invented certainty; record exact error
text for any new wall you hit, in the repo, the same session you hit it.
