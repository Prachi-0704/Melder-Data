#!/bin/zsh

set -e

SCRIPT_DIR="$(cd -- "$(dirname "$0")" && pwd)"
exec "$SCRIPT_DIR/../run_usecase.sh" "$(basename "$SCRIPT_DIR")"
