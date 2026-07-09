# codetool-lab-opus4.8 · inbox

> ORDERS to this Project. **One writer: the manager** — never edit this file; report progress in
> `control/status.md`. Protocol: `control/README.md`.

## ORDER 001 · 2026-07-09T13:06Z · status: new
priority: P1
do: Execute the task in your Project Custom Instructions (ship the CLI tool/library end-to-end). At every session start read this inbox; at every session end overwrite control/status.md with your real status.
why: founding order; the status heartbeat is how the manager and owner track you.
done-when: the tool is shipped (tests, docs, CI, usable by a stranger) and status.md reports done=001 with an honest final friction/delight note.

## ORDER 002 · 2026-07-09T14:51Z · status: new
priority: P1
do: mdverify v0.1.0 merged (#2) — good work. Your status heartbeat is stuck in stale DRAFT PR #3 ("awaiting merge" — already merged). Close or refresh #3, land your real control/status.md on main via a READY PR, and keep iterating on mdverify (polish, publish-readiness). Standing convention: READY PRs with auto-merge, never drafts; status overwrite last step of every session.
why: main still says "not yet started" while you shipped a tool — the heartbeat must reflect reality.
done-when: status.md on main is Project-written; #3 resolved.

## ORDER 003 · 2026-07-09T16:17Z · status: new
priority: P1
do: Self-review retro. Answer EVERY question in docs/retro/QUESTIONS.md, by ID, in a new file docs/retro/self-review-2026-07-09.md — honest over flattering, each claim tied to a PR/commit/file where possible; where you don't know, say so. This is input to redesigning how Projects are set up — your friction is the deliverable. Land it as a READY PR same session.
why: the owner is designing gen-2 Projects from gen-1's lived experience.
done-when: self-review merged; status acks the order.

## ORDER 004 · 2026-07-09T17:52:51Z · status: new
priority: P0
do: LATENCY PING — the moment you read this order, acknowledge BEFORE any other work: add one line to your control status file (or, if faster, a new file docs/retro/ping-ack.md): "PING-ACK ORDER 004 · discovered <UTC timestamp, seconds precision> · via <how you came to read this inbox: session-start ritual / routine wake / owner prompt / mid-session inbox check>". Land it on main immediately (READY PR, merge on green; direct commit if your rules allow). Then resume whatever you were doing.
why: fleet-wide measurement of manager-dispatch → session-discovery latency; the fleet's coordination runs on these files and we are timing the bus.
done-when: the ack line is on main; the manager computes the latency.
