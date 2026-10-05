# Findings Summary

## Analysis

The analysis compared three AD samples against three control samples using STAR-aligned RNA-seq reads and rMATS.

Main rMATS settings:

- Event classes: SE, A5SS, A3SS, MXE, RI
- Counting modes summarized: JC and JCEC
- Primary high-confidence focus: skipped exon (SE)
- Library type: `fr-firststrand`
- Read type: single-end

## Event Counts

From `results/rmats_summary/filtered_event_counts.tsv`, events were filtered using:

- `FDR < 0.05`
- `abs(delta PSI) >= 0.10`

High-confidence SE extraction additionally used:

- `PValue < 0.001`
- total junction count `>= 50`

Current high-confidence SE set:

- 785 SE events
- 442 distinct genes by GeneID; 669 gene-by-counting-mode records across JC and JCEC

## Selected Sashimi Events

The selected visual examples are:

- PFKP: AD higher inclusion, metabolism/GEM-relevant.
- RBM3: AD higher inclusion, neurodegeneration and synaptic-protection relevance.
- MARK3: AD higher inclusion, tau/microtubule biology relevance.
- AMPH: AD higher inclusion, synaptic vesicle/endocytosis relevance.
- PBRM1: control higher inclusion, exploratory lower-count event.

The selected event file preserves the original rMATS column structure, including the duplicate `ID` column. This is important because `rmats2sashimiplot` expects the original rMATS layout.

## Interpretation Limits

This is a small exploratory dataset. The results are suitable for hypothesis generation, visualization, and prioritization, but not as standalone evidence of disease-specific splicing biomarkers.

Recommended follow-up:

- Validate selected events in an independent cohort.
- Map event exons to transcripts/protein domains.
- Check whether events cause coding changes, NMD, UTR changes, or isoform switching.
- For GEM/iMAT integration, prioritize genes with a metabolic reaction link, especially PFKP.
