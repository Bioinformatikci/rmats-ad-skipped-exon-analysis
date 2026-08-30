#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../config/project_config.sh"

mkdir -p "$PROJECT_METADATA_DIR" "$RMATS_OUT_DIR" "$RMATS_TMP_DIR"

cp "$REPO_METADATA_DIR/rmats_b1_AD.txt" "$PROJECT_METADATA_DIR/rmats_b1_AD.txt"
cp "$REPO_METADATA_DIR/rmats_b2_control.txt" "$PROJECT_METADATA_DIR/rmats_b2_control.txt"

cd "$PROJECT_ROOT"

"$CONDA_BIN" run -n "$ENV_NAME" rmats.py \
  --b1 "$PROJECT_METADATA_DIR/rmats_b1_AD.txt" \
  --b2 "$PROJECT_METADATA_DIR/rmats_b2_control.txt" \
  --gtf "$REFERENCE_GTF" \
  --od "$RMATS_OUT_DIR" \
  --tmp "$RMATS_TMP_DIR" \
  -t single \
  --readLength 75 \
  --variable-read-length \
  --libType fr-firststrand \
  --nthread "$THREADS" \
  --tstat "$THREADS" \
  --task both

echo "rMATS complete: $RMATS_OUT_DIR"
