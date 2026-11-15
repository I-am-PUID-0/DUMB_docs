#!/usr/bin/env bash
set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"
poetry run python scripts/build_docs.py
printf '%s\n' 'Serving both channels. Run poetry run python scripts/build_docs.py to refresh after edits.'
exec poetry run python -m http.server 8000 --bind 0.0.0.0 --directory site
