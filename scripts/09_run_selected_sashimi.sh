#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../config/project_config.sh"

selected_dir="$REPO_ROOT/results/sashimi_selected"
plot_dir="$selected_dir/plots"

test -s "$selected_dir/selected_SE_events_for_sashimi.txt"
rm -rf "$plot_dir"
mkdir -p "$plot_dir"

cd "$PROJECT_ROOT"

"$CONDA_BIN" run -n "$ENV_NAME" rmats2sashimiplot \
  --event-type SE \
  -e "$selected_dir/selected_SE_events_for_sashimi.txt" \
  --b1 "$REPO_METADATA_DIR/rmats_b1_AD.txt" \
  --b2 "$REPO_METADATA_DIR/rmats_b2_control.txt" \
  --l1 AD \
  --l2 control \
  --exon_s 1 \
  --intron_s 5 \
  --fig-width 10 \
  --fig-height 8 \
  --min-counts 5 \
  -o "$plot_dir" 2>&1 | tee "$selected_dir/rmats2sashimiplot.log"

find "$plot_dir/Sashimi_plot" -type f -name "*.pdf" -exec cp {} "$selected_dir/" \;

echo "Selected sashimi plots complete: $selected_dir"
