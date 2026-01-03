#!/usr/bin/env bash
set -e

pip install --upgrade pip
pip install poetry

poetry config virtualenvs.create false
poetry install --no-interaction --no-root