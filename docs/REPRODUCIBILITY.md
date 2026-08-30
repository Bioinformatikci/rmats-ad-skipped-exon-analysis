# Reproducibility Notes

## Expected Environment

The original analysis was run in a project-specific conda environment on a local WSL-based RNA-seq workstation.

Key tools:

- Python 3.10.21
- rMATS 4.4.0
- rmats2sashimiplot 4.0.0
- STAR 2.7.10b
- samtools 1.24
- FastQC 0.12.1
- MultiQC 1.35

Use `environment/tool_versions.txt` and `environment/conda_env_export.yml` for the captured environment state.

## Path Model

This repository is intended to sit inside the parent project folder:

```text
rmats/
  datam/
  metadata/
  results/
  rmats-ad-skipped-exon-analysis/
```

By default, scripts treat the parent folder as `PROJECT_ROOT`. If the repository is cloned elsewhere, set:

```bash
export PROJECT_ROOT=/path/to/rmats_project
```

## Data Availability

Large files are not copied into the repository. Recreate the project directory using `data_manifest/input_files_manifest.tsv` and `metadata/samples.tsv`.

For exact local verification, compare file sizes and checksums in `data_manifest/input_files_sha256.tsv`.

## Running Selected Steps

To regenerate only summaries after rMATS has finished:

```bash
conda run -n troppo_rmats_project python scripts/06_summarize_rmats_results.py
conda run -n troppo_rmats_project python scripts/07_extract_high_confidence_se.py
```

To regenerate selected sashimi plots after BAM and rMATS outputs exist:

```bash
conda run -n troppo_rmats_project python scripts/08_select_sashimi_events.py
bash scripts/09_run_selected_sashimi.sh
```

## Scientific Caution

The dataset has three biological samples per group. Use FDR, delta PSI, read support, and biological plausibility together. Do not interpret low FDR alone as proof of a disease mechanism.
