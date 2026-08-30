#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../config/project_config.sh"

mkdir -p "$RESULTS_DIR/reference"

if [ ! -s "$REFERENCE_FASTA" ]; then
  gzip -dc "$REFERENCE_FASTA_GZ" > "$REFERENCE_FASTA"
fi

if [ ! -s "$REFERENCE_GTF" ]; then
  gzip -dc "$REFERENCE_GTF_GZ" > "$REFERENCE_GTF"
fi

echo "Reference files ready: $RESULTS_DIR/reference"
