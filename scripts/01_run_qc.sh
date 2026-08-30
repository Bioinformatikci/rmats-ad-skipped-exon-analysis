#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../config/project_config.sh"

mkdir -p "$RESULTS_DIR/qc/fastqc" "$RESULTS_DIR/qc/multiqc" "$REPO_LOG_DIR"

mapfile -t fastqs < <(tail -n +2 "$REPO_METADATA_DIR/samples.tsv" | awk -v root="$PROJECT_ROOT" -F '\t' '{print root "/" $3}')

if [ "$(find "$RESULTS_DIR/qc/fastqc" -maxdepth 1 -name '*_fastqc.zip' | wc -l)" -lt 6 ]; then
  "$CONDA_BIN" run -n "$ENV_NAME" fastqc -t "$THREADS" -o "$RESULTS_DIR/qc/fastqc" "${fastqs[@]}"
else
  echo "FastQC outputs exist; skipping"
fi

if [ ! -s "$RESULTS_DIR/qc/multiqc/multiqc_report.html" ]; then
  "$CONDA_BIN" run -n "$ENV_NAME" multiqc -o "$RESULTS_DIR/qc/multiqc" "$RESULTS_DIR/qc/fastqc"
else
  echo "MultiQC report exists; skipping"
fi

echo "QC complete: $RESULTS_DIR/qc"
