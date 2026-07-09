#!/usr/bin/env bash
# environments/setup.sh — defensive session setup for codetool-lab-opus4.8 (mdverify).
#
# Contract (see docs/succession/ENVIRONMENT.md and docs/succession/GEN2-FEEDBACK.md item 5):
#   - NEVER assume cwd is the repo: detect the clone explicitly.
#   - Guard EVERY install; a failed install is a warning, never a fatal error.
#   - No bare `pip install -r requirements.txt` (this repo has none; deps come from pyproject).
#   - ALWAYS exit 0 — a setup script must never be able to kill the session.
#     (A sibling-lane script that violated these killed sessions at provision, one dying 10s
#     after spawn and going unnoticed ~2.8h. This script is the fix, tested both from a
#     non-repo cwd and from the repo cwd.)

echo "[setup] starting: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# --- 1. Detect the repo clone directory (never assume cwd) -----------------
REPO_DIR=""
if [ -d /home/user/codetool-lab-opus4.8/.git ]; then
    REPO_DIR=/home/user/codetool-lab-opus4.8
else
    for d in /home/user/*/; do
        if [ -d "${d}.git" ]; then
            REPO_DIR="${d%/}"
            break
        fi
    done
fi

if [ -n "$REPO_DIR" ]; then
    echo "[setup] repo detected: $REPO_DIR"
else
    echo "[setup] WARNING: no git repo found under /home/user (continuing without repo install)"
fi

# --- 2. Pick a Python ------------------------------------------------------
PYTHON="$(command -v python3 || command -v python || true)"
if [ -z "$PYTHON" ]; then
    echo "[setup] WARNING: no python3/python on PATH (continuing; installs will be skipped)"
fi

# --- 3. Install the project in editable mode with dev extras (guarded) -----
INSTALLED_PROJECT=0
if [ -n "$REPO_DIR" ] && [ -n "$PYTHON" ] && [ -f "$REPO_DIR/pyproject.toml" ]; then
    if (cd "$REPO_DIR" && "$PYTHON" -m pip install -e ".[dev]"); then
        INSTALLED_PROJECT=1
        echo "[setup] installed project editable with [dev] extras"
    else
        echo "[setup] WARNING: 'pip install -e .[dev]' failed (continuing; trying bare tools fallback)"
    fi
else
    echo "[setup] WARNING: skipping editable install (missing repo, python, or pyproject.toml) (continuing)"
fi

# --- 4. Fallback: bare dev tools so tests/lint/build can still run ---------
if [ "$INSTALLED_PROJECT" -ne 1 ] && [ -n "$PYTHON" ]; then
    "$PYTHON" -m pip install pytest ruff build \
        || echo "[setup] WARNING: fallback 'pip install pytest ruff build' failed (continuing)"
fi

# --- 5. Report versions (informational; each guarded) ----------------------
if [ -n "$PYTHON" ]; then
    "$PYTHON" --version 2>&1 | sed 's/^/[setup] python: /' || echo "[setup] WARNING: python --version failed (continuing)"
    "$PYTHON" -m pip --version 2>&1 | sed 's/^/[setup] pip: /' || echo "[setup] WARNING: pip --version failed (continuing)"
fi
if command -v ruff >/dev/null 2>&1; then
    echo "[setup] ruff: $(ruff --version 2>&1)"
else
    echo "[setup] WARNING: ruff not on PATH after install (continuing)"
fi
if command -v pytest >/dev/null 2>&1; then
    echo "[setup] pytest: $(pytest --version 2>&1 | head -n1)"
else
    echo "[setup] WARNING: pytest not on PATH after install (continuing)"
fi

echo "[setup] done: $(date -u +%Y-%m-%dT%H:%M:%SZ) (setup never fails the session)"
exit 0
