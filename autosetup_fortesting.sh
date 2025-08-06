#!/usr/bin/env bash
# Portable starter: sets up venv, installs MAS/requirements.txt once, then runs Python with PYTHONPATH=.
set -Eeuo pipefail

# --- config (overridable via env) ---
PYTHON_BIN="${PYTHON_BIN:-python3}"   # fallback to "python" if python3 missing
VENV_DIR="${VENV_DIR:-.venv}"
REQUIREMENTS_REL="MAS/requirements.txt"
DEFAULT_TARGET="MAS/test_imports.py"
# ------------------------------------

# Move to repo root (directory of this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Sanity checks
if [[ ! -f "$REQUIREMENTS_REL" ]]; then
  echo "Error: '$REQUIREMENTS_REL' not found relative to $(pwd)" >&2
  exit 1
fi

# Pick a creator Python
if command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  CREATOR_PY="$PYTHON_BIN"
elif command -v python >/dev/null 2>&1; then
  CREATOR_PY="python"
else
  echo "Error: no suitable Python found (tried $PYTHON_BIN, python)." >&2
  exit 1
fi

# Create venv if missing
if [[ ! -d "$VENV_DIR" ]]; then
  "$CREATOR_PY" -m venv "$VENV_DIR"
fi

# Find venv python (POSIX/macOS/Linux or Git Bash on Windows)
if [[ -x "$VENV_DIR/bin/python" ]]; then
  VENV_PY="$VENV_DIR/bin/python"
elif [[ -x "$VENV_DIR/Scripts/python.exe" ]]; then
  VENV_PY="$VENV_DIR/Scripts/python.exe"
else
  echo "Error: could not locate python inside venv '$VENV_DIR'." >&2
  exit 1
fi

# Upgrade pip and install requirements only when changed
STAMP="$VENV_DIR/.requirements.stamp"
"$VENV_PY" -m pip install --upgrade pip wheel >/dev/null

if [[ ! -f "$STAMP" || "$REQUIREMENTS_REL" -nt "$STAMP" || "${FORCE_REINSTALL:-0}" = "1" ]]; then
  echo "Installing dependencies from $REQUIREMENTS_REL ..."
  "$VENV_PY" -m pip install -r "$REQUIREMENTS_REL"
  touch "$STAMP"
fi

# Build command line
if [[ $# -eq 0 ]]; then
  TARGET="$DEFAULT_TARGET"
  if [[ ! -f "$TARGET" ]]; then
    echo "Error: default target '$TARGET' not found. Pass a script to run." >&2
    exit 1
  fi
  set -- "$TARGET"
fi

# Ensure repo root is on PYTHONPATH
export PYTHONPATH="$(pwd)${PYTHONPATH+:$PYTHONPATH}"

# Run inside venv
exec "$VENV_PY" "$@"
