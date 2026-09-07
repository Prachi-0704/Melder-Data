#!/bin/zsh

set -e
setopt null_glob

USECASES_DIR="$(cd -- "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$USECASES_DIR/.." && pwd)"
MELDER_BIN="$REPO_ROOT/target/release/meld"

usage() {
  echo "Usage: $0 <usecase-folder-name|all>"
  echo
  echo "Examples:"
  echo "  $0 uc_001_company_entity_resolution"
  echo "  $0 uc_002_normalized_exact_match"
  echo "  $0 all"
  exit 1
}

if [[ $# -ne 1 ]]; then
  usage
fi

TARGET="$1"

if [[ ! -x "$MELDER_BIN" ]]; then
  echo "Melder binary not found: $MELDER_BIN"
  echo "Build it first with: cargo build --release"
  exit 1
fi

run_case() {
  local case_name="$1"
  local case_dir="$USECASES_DIR/$case_name"
  local config_file="$case_dir/config.yaml"

  if [[ ! -d "$case_dir" ]]; then
    echo "Use case folder not found: $case_dir"
    return 1
  fi

  if [[ ! -f "$config_file" ]]; then
    echo "Config file not found in $case_dir"
    return 1
  fi

  local runs_dir="$case_dir/runs"
  mkdir -p "$runs_dir" "$case_dir/cache"

  local last_run=0
  for d in "$runs_dir"/*; do
    [[ -d "$d" ]] || continue
    local name="${d##*/}"
    if [[ "$name" =~ ^run_([0-9]+)$ ]]; then
      local run_num="${match[1]}"
      if (( run_num > last_run )); then
        last_run=$run_num
      fi
    fi
  done

  local next_run=$((last_run + 1))
  local run_dir="$runs_dir/run_$(printf '%03d' "$next_run")"
  mkdir -p "$run_dir"

  # Create a temporary per-run config that overrides output paths so
  # results and crossmap files are written into this run's directory.
  # The temp config is removed after the run to avoid persistent per-run
  # files in the repository.
    local tmp_config
    tmp_config="$(mktemp -t melder_config.XXXXXX)"
    perl -0777 -pe 's|path: .*?/runs/crossmap.csv|path: '"$run_dir"'/crossmap.csv|g; s|csv_dir_path: .*|csv_dir_path: '"$run_dir"'|g' "$config_file" > "$tmp_config"

  echo "Starting Melder run for $case_name (config: $config_file, using run config: $tmp_config)"
  "$MELDER_BIN" validate --config "$tmp_config"
  "$MELDER_BIN" run --config "$tmp_config"
  echo "Run completed: $run_dir"
  rm -f "$tmp_config"
}

if [[ "$TARGET" == "all" ]]; then
  for d in "$USECASES_DIR"/*; do
    [[ -d "$d" ]] || continue
    [[ -f "$d/config.yaml" ]] || continue
    run_case "${d##*/}"
  done
else
  run_case "$TARGET"
fi
