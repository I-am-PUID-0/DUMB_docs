#!/usr/bin/env bash
set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"
export POETRY_VIRTUALENVS_CREATE=true
export POETRY_VIRTUALENVS_IN_PROJECT=true

if ! command -v poetry >/dev/null 2>&1; then
    python -m pip install --user poetry
fi

poetry install --no-interaction --no-root
