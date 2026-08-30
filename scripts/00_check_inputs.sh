#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../config/project_config.sh"

echo "Checking conda env and key tools"
"$CONDA_BIN" run -n "$ENV_NAME" python --version
"$CONDA_BIN" run -n "$ENV_NAME" rmats.py --version
"$CONDA_BIN" run -n "$ENV_NAME" STAR --version
"$CONDA_BIN" run -n "$ENV_NAME" samtools --version | head -1

echo "Checking FASTQ files"
tail -n +2 "$REPO_METADATA_DIR/samples.tsv" | while IFS=$'\t' read -r sample group fastq; do
  path="$PROJECT_ROOT/$fastq"
  test -s "$path"
  gzip -t "$path"
  printf "OK %s %s\n" "$group" "$sample"
done

echo "Checking reference files"
test -s "$REFERENCE_FASTA_GZ"
test -s "$REFERENCE_GTF_GZ"
gzip -t "$REFERENCE_FASTA_GZ"
gzip -t "$REFERENCE_GTF_GZ"

echo "Input check complete"
