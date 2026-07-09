# ENVIRONMENT — what a gen-2 session needs, and the tested setup script

## The setup script: `environments/setup.sh`

Defensive by contract (see GEN2-FEEDBACK.md item 5 — a sibling lane's non-defensive script
killed sessions at provision, one dying 10s after spawn and going unnoticed ~2.8h because no
failure event fires):

- **Detects the repo clone dir — never assumes cwd.** Prefers
  `/home/user/codetool-lab-opus4.8`, else the first directory under `/home/user` containing
  `.git`, else warns and continues.
- **Guarded installs only.** `python -m pip install -e ".[dev]"` from the detected repo dir;
  on failure it warns and falls back to `pip install pytest ruff build` — every install
  carries `|| echo "[setup] WARNING: ... (continuing)"`. There is no
  `pip install -r requirements.txt` anywhere (this repo has no requirements.txt; dependencies
  live in `pyproject.toml`).
- **Reports versions** of python, pip, ruff, and pytest (informational, each guarded).
- **ALWAYS exits 0.** A setup script must never be able to kill the session.

## Test evidence (run at wind-down, 2026-07-09, this container)

Executed twice as ordered, capturing exit codes:

| Run | cwd | Result | Exit code |
|-----|-----|--------|-----------|
| 1 | non-repo cwd (the session scratchpad dir) | repo detected at `/home/user/codetool-lab-opus4.8`; editable install with `[dev]` extras succeeded; versions reported | **0** |
| 2 | repo cwd (`/home/user/codetool-lab-opus4.8`) | same: detection, editable install, versions reported | **0** |

Reported versions in both runs: `Python 3.11.15`, `pip 24.0`, `ruff 0.15.8` (PATH-resolved),
`pytest 9.0.2` (PATH-resolved). Honest note: pip installed `ruff 0.12.12` (the pyproject pin
`>=0.4,<0.13`) and `pytest 9.1.1` into the interpreter's dist-packages, while the `ruff` /
`pytest` binaries first on PATH in this container are newer standalone installs — the script
reports what a session will actually invoke by bare name, which is the number that matters.
The degraded paths (no repo found, no python, install failure) warn and continue by
construction; they were not separately exercised in this container because a healthy repo and
python are present — stated rather than claimed.

## Environment variable NAMES required

**None beyond the platform's own GitHub/proxy plumbing.** This lane needed no custom secrets
or variables at any point in gen-1 — stated explicitly rather than inventing needs. The
platform itself provides (names only, do not set these by hand): `HTTPS_PROXY` (and the CA
bundle it implies) for outbound HTTPS, and the git credential/proxy plumbing that makes
`origin` pushable. Releases use the Actions-provided `GITHUB_TOKEN` inside
`.github/workflows/release.yml` — server-side only, never present in the session. If PyPI
publishing is ever added, that would introduce the first real secret (a PyPI token, owner-held;
see the roadmap in the final review).

## What should be preinstalled

- **python3.9+** (the project floor; the gen-1 container had 3.11)
- **pip**
- **git**
- *(optional)* **pipx** — only for exercising the README's recommended user-install path
- *(deliberately not required)* node/ruby — their runners are unit-tested; CI does not demand
  the interpreters, per docs/DECISIONS.md #9
