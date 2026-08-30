#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../config/project_config.sh"

mkdir -p "$STAR_ALIGN_DIR"

align_one() {
  local sample="$1"
  local fastq="$2"
  local out_prefix="$STAR_ALIGN_DIR/${sample}."
  local tmp_dir="/tmp/troppo_rmats_star_${sample}_tmp"
  local bam="$STAR_ALIGN_DIR/${sample}.Aligned.sortedByCoord.out.bam"

  if [ ! -s "$bam" ]; then
    rm -rf "$tmp_dir"
    "$CONDA_BIN" run -n "$ENV_NAME" STAR \
      --runThreadN "$THREADS" \
      --genomeDir "$STAR_INDEX_DIR" \
      --readFilesIn "$fastq" \
      --readFilesCommand zcat \
      --outFileNamePrefix "$out_prefix" \
      --outTmpDir "$tmp_dir" \
      --outSAMtype BAM SortedByCoordinate \
      --outSAMstrandField intronMotif \
      --quantMode GeneCounts
    rm -rf "$tmp_dir"
  else
    echo "BAM exists, skipping alignment: $bam"
  fi

  if [ ! -s "${bam}.bai" ]; then
    "$CONDA_BIN" run -n "$ENV_NAME" samtools index -@ "$THREADS" "$bam"
  fi
}

tail -n +2 "$REPO_METADATA_DIR/samples.tsv" | while IFS=$'\t' read -r sample group fastq; do
  align_one "$sample" "$PROJECT_ROOT/$fastq"
done

echo "STAR alignment complete: $STAR_ALIGN_DIR"
