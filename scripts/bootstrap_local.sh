#!/usr/bin/env bash
# Bootstrap a local TraceLeak checkout for lightweight validation.
#
# This script intentionally runs only lightweight repository checks.
# It does not run OpenSSL instrumentation, heavy trace generation, or NN training.
#
# Usage:
#   bash scripts/bootstrap_local.sh
#   bash scripts/bootstrap_local.sh --dir ~/work/TraceLeak
#   bash scripts/bootstrap_local.sh --skip-tests
#   TRACELEAK_REPO_URL=https://github.com/Unjuno/TraceLeak.git bash scripts/bootstrap_local.sh

set -Eeuo pipefail

REPO_URL="${TRACELEAK_REPO_URL:-https://github.com/Unjuno/TraceLeak.git}"
TARGET_DIR="${TRACELEAK_DIR:-TraceLeak}"
SKIP_TESTS=0
PYTHON_BIN="${PYTHON:-python3}"

usage() {
  cat <<'EOF'
Usage: bootstrap_local.sh [options]

Options:
  --dir PATH       Clone or update TraceLeak at PATH. Default: ./TraceLeak
  --repo URL       Git repository URL. Default: https://github.com/Unjuno/TraceLeak.git
  --python BIN     Python interpreter. Default: python3 or $PYTHON
  --skip-tests     Install dependencies but do not run pytest.
  -h, --help       Show this help.

Environment:
  TRACELEAK_REPO_URL   Override repository URL.
  TRACELEAK_DIR        Override target directory.
  PYTHON               Override Python interpreter.

This script performs only lightweight local validation:
  clone/pull -> create venv -> pip install -e '.[dev]' -> pytest

It does not run heavy OpenSSL tracing, NN training, or large experiments.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dir)
      TARGET_DIR="$2"
      shift 2
      ;;
    --repo)
      REPO_URL="$2"
      shift 2
      ;;
    --python)
      PYTHON_BIN="$2"
      shift 2
      ;;
    --skip-tests)
      SKIP_TESTS=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "error: required command not found: $1" >&2
    exit 1
  fi
}

need_cmd git
need_cmd "$PYTHON_BIN"

if [[ -d "$TARGET_DIR/.git" ]]; then
  echo "[TraceLeak] updating existing checkout: $TARGET_DIR"
  git -C "$TARGET_DIR" pull --ff-only
elif [[ -e "$TARGET_DIR" ]]; then
  echo "error: target exists but is not a git checkout: $TARGET_DIR" >&2
  exit 1
else
  echo "[TraceLeak] cloning $REPO_URL -> $TARGET_DIR"
  git clone "$REPO_URL" "$TARGET_DIR"
fi

cd "$TARGET_DIR"

if [[ ! -f "pyproject.toml" ]]; then
  echo "error: pyproject.toml not found. Are you in the TraceLeak repository?" >&2
  exit 1
fi

echo "[TraceLeak] creating virtual environment"
"$PYTHON_BIN" -m venv .venv

# shellcheck disable=SC1091
source .venv/bin/activate

echo "[TraceLeak] upgrading pip"
python -m pip install --upgrade pip

echo "[TraceLeak] installing package with dev extras"
python -m pip install -e ".[dev]"

if [[ "$SKIP_TESTS" -eq 0 ]]; then
  echo "[TraceLeak] running lightweight tests"
  pytest
else
  echo "[TraceLeak] skipping tests"
fi

cat <<'EOF'

[TraceLeak] local bootstrap complete.

Next lightweight commands:
  source .venv/bin/activate
  pytest

Heavy/local-only work, intentionally not run by this script:
  - OpenSSL instrumentation builds
  - raw trace generation
  - NN training
  - large experiment runs
EOF
