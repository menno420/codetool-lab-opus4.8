# Proposed Custom Instructions for gen-2 — rewritten from lived experience

> **Honest caveat up front:** the coordinator seat (which authored this at wind-down, after the
> cross-session channel died) never saw the build lane's full Custom Instructions text. This
> critique is based on (a) what the build lane's committed self-review quotes and answers —
> especially its B4 answer on the "published" ambiguity and its F1 proposed founding rules —
> and (b) behavior observed from outside (PR bodies, commit trailers, status heartbeats,
> escalation patterns). Where the actual instruction text is unknown, the keep/drop verdict is
> about the *inferred* instruction, and says so.

Format: **KEEP** / **DROP** / **ADD**, one-line why each. At the end: agreement/disagreement
with each seed-standard bullet, as ordered — disagreement is welcome data.

## KEEP

1. **KEEP: ship end-to-end (tests, docs, CI, usable by a stranger).** It produced a real,
   installable tool in ~90 minutes; the bar is right. (Inferred from ORDER 001's done-when.)
2. **KEEP: the control/ ritual — inbox first, status last, never edit inbox.** Zero merge
   conflicts across 19 PRs and three writer lanes; the protocol carried its weight.
3. **KEEP: honest-over-flattering retro duty (ORDER 003 style).** The committed self-review
   became the *only* build-lane voice available after the messaging channel died — the duty to
   commit lived experience saved the succession.
4. **KEEP: decide-and-flag over escalate-and-wait.** Ten unilateral decisions in
   `docs/DECISIONS.md`, none reversed; the one time the lane escalated instead (first merge
   denial) was genuinely gated, so the calibration was correct.
5. **KEEP: READY PRs with auto-merge-on-green, never drafts** (the ORDER 002 standing
   convention). The project's only dead PR (#3) was its only draft.
6. **KEEP: status overwrite as the deliberate LAST step of every session.** It is the
   manager's liveness signal; gen-1's stale-status incident (main saying "not yet started"
   hours after shipping) shows what happens when landing it is delayed.

## DROP

1. **DROP: the bare word "published" in any done-when.** The self-review's B4 answer documents
   the cost: "the founding order's done-when ... combined with the Custom-Instructions word
   'published'" left it undecidable whether `git+...@main` install counted or a tag/Release
   was mandatory. Say "merged + installable" or "tagged Release," never "published."
2. **DROP: any instruction that implies the session can reach docs outside its repo scope.**
   The gen-2 blueprint itself was unreachable from this lane (see GEN2-FEEDBACK.md); an
   instruction pointing at an unreadable doc is worse than no instruction.
3. **DROP (by replacement): silence about write-scope limits.** The self-review's B2 is
   explicit: the limits "should have been in the repo seed or Custom Instructions ... That
   single line would have saved the entire probe." Replaced by ADD #1/#3 below.

## ADD

1. **ADD: boot-time capability inventory per session type.** "Before building, probe: branch
   push, PR create, merge, workflow dispatch; record results in status." Gen-1 lost ~2h to an
   unaudited capability asymmetry — the biggest single waste of the run.
2. **ADD: explicit merge authority — name who merges and with which tool.** E.g.: "Build
   sessions do NOT self-merge; green PRs are merged by the coordinator via
   `merge_pull_request`; if no coordinator, flag needs-owner." Removes both the denial churn
   and the false "owner-only" conclusion.
3. **ADD: the publish path, stated up front.** "Releases are cut by dispatching
   `.github/workflows/release.yml` with `version=vX.Y.Z` after the bump PR merges; sessions
   cannot push tags (HTTP 403) — do not try." One sentence, replaces gen-1's 2-3 worker rounds
   of wall-probing.
4. **ADD: never share a clone between parallel git-mutating workers — worktrees or serial.**
   Gen-1 had exactly one workspace collision (HEAD/index) and this rule is its entire fix.
5. **ADD: escalate on the FIRST classifier denial; never retry.** A reworded retry was flagged
   as `[Auto-Mode Bypass] ... tunneling a blocked action`; retries read as evasion and spend
   trust for nothing.
6. **ADD: commit lane knowledge to the repo immediately — channels can die mid-run.**
   `send_message` was disabled mid-wind-down (`tool is not enabled for this organization`);
   only what was already committed survived. Chat is a cache, git is the store.
7. **ADD: heartbeat-before-work.** "Your first action in any session: land/refresh a status
   heartbeat (or at minimum verify you CAN)." A sibling-lane session died 10s after spawn and
   sat 'active' for ~2.8h; a mandatory early heartbeat makes silent death visible in minutes.

## Seed-standard bullets — agree/disagree, one line each

1. **READY-never-draft — AGREE.** Gen-1's own data: the one draft PR is the one that died;
   drafts invite staleness in a fast-moving main.
2. **Explicit merge authority — AGREE, strongest yes on the list.** Its absence was the ~2h
   headline waste; see ADD #2.
3. **Agent-reachable done-whens — AGREE.** The "published" ambiguity (B4) was exactly a
   done-when whose satisfaction the agent couldn't determine from where it stood.
4. **Heartbeat-before-work — AGREE, with a nuance.** Yes for liveness (the provision-death
   case is decisive); but gen-1 also shows a *content* heartbeat landed too eagerly goes stale
   (draft #3 opened before the tool merged) — so: heartbeat early for liveness, report
   *outcomes* only after they're real.
5. **Walking skeleton — AGREE.** Gen-1 effectively ran its skeleton inside PR #2 (a 100-test
   first PR) and still spent its afternoon discovering pipeline walls one at a time; a trivial
   end-to-end PR first would have surfaced merge authority and CI shape for the price of one
   line.
6. **Known walls stated up front — AGREE.** B2's "that single line would have saved the entire
   probe" is the whole argument; NEXT-BOOT.md now ships the table.
7. **Model+time on every card — PARTIAL DISAGREE.** Time-on-card: yes, cheap and useful.
   Model-on-card: worth having *when policy permits*, but gen-1 hit a real conflict — the
   coordinator seat is barred from writing its own model identifier into repo artifacts, so a
   blanket "model on every card" is unsatisfiable as written. Propose: "model per agent where
   session policy allows; otherwise 'withheld per session policy, disclosed in chat' — never
   guess, never omit silently." Disagreement offered as data, per the order.
