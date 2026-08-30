# File Organization

This repository is a lightweight, GitHub-ready package for the AD vs control rMATS skipped-exon analysis.

## Included

`metadata/`

- `samples.tsv`: sample ID, group, and FASTQ path relative to the parent project root.
- `rmats_b1_AD.txt`: AD BAM list used as rMATS group 1.
- `rmats_b2_control.txt`: control BAM list used as rMATS group 2.

`scripts/`

- `00_check_inputs.sh`: checks conda tools, FASTQ gzip integrity, references, and writes a lightweight input manifest.
- `01_run_qc.sh`: runs FastQC and MultiQC.
- `02_prepare_reference.sh`: decompresses reference FASTA/GTF for STAR and rMATS.
- `03_build_star_index.sh`: builds STAR index with `--genomeSAsparseD`.
- `04_align_star.sh`: aligns FASTQ files and indexes sorted BAM files.
- `05_run_rmats.sh`: runs rMATS for AD vs control.
- `06_summarize_rmats_results.py`: summarizes all rMATS event classes.
- `07_extract_high_confidence_se.py`: extracts high-confidence skipped-exon events.
- `08_select_sashimi_events.py`: selects curated SE events for visualization.
- `09_run_selected_sashimi.sh`: creates selected sashimi plot PDFs.
- `run_all.sh`: orchestration script only.

`results/rmats_summary/`

- Compact summary outputs suitable for GitHub.
- Full rMATS output tables can be regenerated but are not all copied here.

`results/sashimi_selected/`

- Selected SE event file.
- Selected event summary table.
- Selected sashimi plot PDFs.

`data_manifest/`

- Raw input file manifest and result manifest.
- Large raw files are described here instead of copied into the repository.

## Not Included

The following are intentionally excluded from this repository because they are too large for ordinary GitHub use and are reproducible from the manifest and scripts:

- Raw FASTQ files.
- STAR genome index.
- STAR BAM files and BAM index files.
- Uncompressed reference FASTA/GTF files.
- Full rMATS output directory.

Keep those files in the parent analysis project or external storage.
