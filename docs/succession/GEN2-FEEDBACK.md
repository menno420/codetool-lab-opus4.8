# GEN2 BLUEPRINT / SEED FEEDBACK — for manager collection

> **Audience: the manager assembling the gen-2 blueprint and seed repos.** Concrete,
> lived-experience-backed suggestions from the gen-1 wind-down of `codetool-lab-opus4.8`
> (coordinator seat authoring, build seat's committed self-review as source). Each item says
> what to change in the seed/blueprint and cites the incident that earned it.
>
> **Reachability disclosure, first because it's meta:** this lane could NOT read the gen-2
> blueprint itself. The fleet-manager repo is outside this session's repo scope, and
> `substrate-kit` was checked directly — it contains no `docs/gen2-blueprint.md` and no
> `environments/` directory. So this feedback aligns with the seed-standard bullets as relayed
> in orders, not with the blueprint text. Which is itself the finding of item 4.

## 1. Seed repos ship `release.yml` + a walking-skeleton CI from day one

Gen-1 spent 2-3 worker rounds discovering that sessions cannot push tags (`error: RPC failed;
HTTP 403`), cannot reach api.github.com ("connect the Claude GitHub App"), and have no MCP
release tool — then built `.github/workflows/release.yml` (workflow_dispatch,
`contents: write`, build + `gh release create` with `GH_TOKEN=GITHUB_TOKEN`) which worked
first-try, twice (runs 29035224581, 29038899218). That workflow is ~60 lines and fully
generic. Put it in the seed; a green trivial-CI should exist before the first real PR so the
skeleton check (NEXT-BOOT.md §2) has something to run against.

## 2. State the classifier merge policy + merge authority in the instructions

The build session's exact experience: `Permission for this action was denied by the Claude
Code auto mode classifier.` — then a reframed retry flagged `[Auto-Mode Bypass] ... tunneling
a blocked action`, and a later merge flagged `[Merge Without Review] ...` because an earlier
"full permissions" grant was scoped to one PR. Meanwhile the coordinator's workers merged with
zero denials all day. Two sentences in the seed instructions fix this whole class: "Build
sessions cannot self-merge — the classifier will deny, and a retry reads as tunneling. Green
PRs are merged by <named seat> via `merge_pull_request`."

## 3. Ship a capability matrix per session type in the seed

The headline gen-1 finding: session capability asymmetry went unaudited until the owner's
wake-up order forced it — ~2h of owner-click latency (PRs green 15:07Z, merged 16:41Z) that
the coordinator seat could have absorbed at any moment. The seed should ship a table (session
type × {branch push, PR create, merge, workflow dispatch, tag push, ref delete, api.github.com,
cross-session messaging}) with known values pre-filled and "probe at boot" for the rest, plus
the probe procedure (NEXT-BOOT.md §5 has one to copy).

## 4. Don't reference docs a lane can't read

The wind-down order asked this lane to align with the gen-2 blueprint; the blueprint was
unreachable (fleet-manager repo out of scope; substrate-kit checked and lacking it — see
disclosure above). An instruction that points at an unreadable doc silently degrades into the
agent's best guess while *appearing* grounded. Rule for the blueprint: every doc an
instruction references must be committed in (or copied into) the repo that lane can read —
same principle as the protocol's local-copy note in `control/README.md`.

## 5. Setup scripts must follow the defensive contract

A sibling lane's setup script assumed cwd was the repo and ran a bare
`pip install -r requirements.txt`; sessions died AT PROVISION — one died 10 seconds after
spawn and went unnoticed ~2.8 hours because no failure event fires and dead sessions stay
"active". Contract (per substrate-kit's `docs/environment-setup-script.md`, implemented and
tested in this repo's `environments/setup.sh`): detect the repo dir, never assume cwd; guard
every install with `|| echo "[setup] WARNING: ... (continuing)"`; no bare requirements.txt
install; ALWAYS `exit 0`. A setup script's job is to improve the environment, never to be
able to kill the session.

## 6. Spawn-liveness rule: first heartbeat within 10 minutes, or respawn

Corollary of item 5, for coordinators: after any spawn, verify a first heartbeat within 10
minutes; silence = dead = respawn. This is the rule the coordinator seat derived from the
sibling-lane deaths (2.8h of undetected silence), and it costs one check per spawn. Put it in
the coordinator's instructions, not just in lore.

## 7. Keep one-writer-per-file — it produced zero conflicts across 19 PRs

The control/ protocol (manager owns `inbox.md`, Project owns `status.md`, append-only /
overwrite-own, forward-only git) ran a three-writer repo (manager, build, coordinator) for a
full project life with **zero merge conflicts in 19 PRs**. It is the cheapest coordination
mechanism gen-1 touched and the only one that never failed. Carry it into gen-2 unchanged;
extend it (one writer per file) to any new shared artifacts the blueprint adds — including
the succession docs themselves.

## Bonus observations (smaller, still worth collecting)

- **Channels die; git doesn't.** `send_message` was org-disabled mid-wind-down (`tool is not
  enabled for this organization`); the succession pack could be authored only because the
  build lane's retro was already committed. Blueprint phrasing: "commit lane knowledge the
  same session you gain it."
- **`enable_pr_auto_merge` misreports pending as failing** ("unstable status (required checks
  are failing)"). Until fixed platform-side, seed instructions should warn it.
- **Don't seed macos-13 CI cells** — GitHub's macOS-13 hosted runners no longer allocate;
  arm64 `macos-latest` has no CPython 3.9, so 3.9 coverage belongs on Ubuntu.
- **Latency pings need an ack deadline.** ORDER 004 (P0 latency ping, landed 17:53Z) was
  apparently never acked before wind-down — a ping order should state what the manager does on
  timeout, or it measures nothing.
