#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../config/project_config.sh"

mkdir -p "$STAR_INDEX_DIR"

if [ -s "$STAR_INDEX_DIR/SA" ] && [ -s "$STAR_INDEX_DIR/Genome" ]; then
  echo "STAR index already exists: $STAR_INDEX_DIR"
  exit 0
fi

"$CONDA_BIN" run -n "$ENV_NAME" STAR \
  --runMode genomeGenerate \
  --runThreadN "$THREADS" \
  --genomeDir "$STAR_INDEX_DIR" \
  --genomeFastaFiles "$REFERENCE_FASTA" \
  --sjdbGTFfile "$REFERENCE_GTF" \
  --sjdbOverhang 74 \
  --genomeSAsparseD "$GENOME_SA_SPARSE_D"

echo "STAR index complete: $STAR_INDEX_DIR"
