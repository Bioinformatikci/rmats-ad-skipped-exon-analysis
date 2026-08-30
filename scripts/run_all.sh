#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/../config/project_config.sh"

bash "$script_dir/00_check_inputs.sh"
bash "$script_dir/01_run_qc.sh"
bash "$script_dir/02_prepare_reference.sh"
bash "$script_dir/03_build_star_index.sh"
bash "$script_dir/04_align_star.sh"
bash "$script_dir/05_run_rmats.sh"
"$CONDA_BIN" run -n "$ENV_NAME" python "$script_dir/06_summarize_rmats_results.py"
"$CONDA_BIN" run -n "$ENV_NAME" python "$script_dir/07_extract_high_confidence_se.py"
"$CONDA_BIN" run -n "$ENV_NAME" python "$script_dir/08_select_sashimi_events.py"
bash "$script_dir/09_run_selected_sashimi.sh"

echo "Full workflow complete"
