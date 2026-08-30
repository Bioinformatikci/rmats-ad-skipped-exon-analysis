#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$REPO_ROOT/.." && pwd)}"

CONDA_BIN="${CONDA_BIN:-conda}"
ENV_NAME="${ENV_NAME:-troppo_rmats_project}"
THREADS="${THREADS:-6}"
GENOME_SA_SPARSE_D="${GENOME_SA_SPARSE_D:-2}"

DATA_DIR="${DATA_DIR:-$PROJECT_ROOT/datam}"
RESULTS_DIR="${RESULTS_DIR:-$PROJECT_ROOT/results}"
PROJECT_METADATA_DIR="${PROJECT_METADATA_DIR:-$PROJECT_ROOT/metadata}"

REPO_METADATA_DIR="$REPO_ROOT/metadata"
REPO_RESULTS_DIR="$REPO_ROOT/results"
REPO_LOG_DIR="$REPO_ROOT/logs"

REFERENCE_FASTA_GZ="$DATA_DIR/GRCh38.primary_assembly.genome.fa.gz"
REFERENCE_GTF_GZ="$DATA_DIR/gencode.v44.primary_assembly.annotation.gtf.gz"
REFERENCE_FASTA="$RESULTS_DIR/reference/GRCh38.primary_assembly.genome.fa"
REFERENCE_GTF="$RESULTS_DIR/reference/gencode.v44.primary_assembly.annotation.gtf"
STAR_INDEX_DIR="$RESULTS_DIR/star_index"
STAR_ALIGN_DIR="$RESULTS_DIR/star_align"
RMATS_OUT_DIR="$RESULTS_DIR/rmats/out"
RMATS_TMP_DIR="$RESULTS_DIR/rmats/tmp"
RMATS_SUMMARY_DIR="$RESULTS_DIR/rmats/summary"
