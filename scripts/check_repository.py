#!/usr/bin/env python3
"""Validate committed tabular results without running the RNA-seq workflow."""

import csv
from collections import Counter
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "results" / "rmats_summary"


def read_tsv(path, required_columns=()):
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader, None)
        if (not header or len(set(header)) != len(header)
                or any(not name for name in header)
                or not set(required_columns) <= set(header)):
            raise ValueError(f"Invalid header: {path}")
        rows = []
        for line_number, values in enumerate(reader, start=2):
            if not values or all(not value.strip() for value in values):
                raise ValueError(f"Blank row: {path}:{line_number}")
            if len(values) != len(header):
                raise ValueError(f"Wrong column count: {path}:{line_number}")
            rows.append(dict(zip(header, values)))
        return rows


def nonnegative_int(value, label):
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"Invalid integer for {label}: {value}") from exc
    if parsed < 0:
        raise ValueError(f"Negative integer for {label}: {value}")
    return parsed


def bounded_float(value, label, minimum, maximum):
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError(f"Invalid number for {label}: {value}") from exc
    if not math.isfinite(parsed) or not minimum <= parsed <= maximum:
        raise ValueError(f"Out-of-range number for {label}: {value}")
    return parsed


for table in ROOT.rglob("*.tsv"):
    read_tsv(table)

samples = read_tsv(ROOT / "metadata" / "samples.tsv", ("sample", "group", "fastq"))
if not samples or any(not all(row[column].strip() for column in ("sample", "group", "fastq")) for row in samples):
    raise ValueError("Sample table must have nonempty sample, group, and fastq values")
if Counter(row["group"] for row in samples) != {"AD": 3, "control": 3}:
    raise ValueError("Expected three AD and three control sample records")
if len({row["sample"] for row in samples}) != len(samples):
    raise ValueError("Duplicate sample ID")

counts = read_tsv(SUMMARY / "filtered_event_counts.tsv")
expected_pairs = {(event, mode) for event in ("SE", "A5SS", "A3SS", "MXE", "RI") for mode in ("JC", "JCEC")}
pairs = {(row["event_type"], row["counting_mode"]) for row in counts}
if len(counts) != len(expected_pairs) or pairs != expected_pairs:
    raise ValueError("Expected one summary row for each event type and counting mode")

for row in counts:
    event, mode = row["event_type"], row["counting_mode"]
    events = read_tsv(SUMMARY / f"{event}.MATS.{mode}.filtered_FDR0.05_delta0.10.tsv")
    tested = nonnegative_int(row["total_tested"], f"{event}/{mode} total_tested")
    significant = nonnegative_int(row["significant_fdr_lt_0_05_abs_delta_ge_0_10"], f"{event}/{mode} significant")
    ad_count = nonnegative_int(row["AD_higher_inclusion"], f"{event}/{mode} AD count")
    control_count = nonnegative_int(row["control_higher_inclusion"], f"{event}/{mode} control count")
    if tested < significant or ad_count + control_count != significant:
        raise ValueError(f"Invalid summary counts for {event}/{mode}")
    directions = Counter(
        "AD" if bounded_float(item["IncLevelDifference"], "delta PSI", -1, 1) > 0 else "control"
        for item in events
    )
    if len(events) != significant or directions != {
        "AD": ad_count,
        "control": control_count,
    }:
        raise ValueError(f"Summary counts disagree with {event}/{mode} table")
    if any(bounded_float(item["FDR"], "FDR", 0, 1) >= 0.05
           or abs(bounded_float(item["IncLevelDifference"], "delta PSI", -1, 1)) < 0.10
           for item in events):
        raise ValueError(f"Filtered thresholds disagree with {event}/{mode} table")

high_confidence = read_tsv(SUMMARY / "SE_high_confidence_lowFDR_lowP_highCount.tsv")
for row in high_confidence:
    delta = bounded_float(row["deltaPSI_AD_minus_control"], "high-confidence delta PSI", -1, 1)
    if (bounded_float(row["FDR"], "high-confidence FDR", 0, 1) >= 0.05
            or bounded_float(row["PValue"], "high-confidence PValue", 0, 1) >= 0.001
            or abs(delta) < 0.10 or nonnegative_int(row["total_count"], "total_count") < 50):
        raise ValueError(f"High-confidence threshold violation at rank {row['rank']}")
    expected_direction = "AD_higher_inclusion" if delta > 0 else "control_higher_inclusion"
    if row["direction"] != expected_direction:
        raise ValueError(f"High-confidence direction violation at rank {row['rank']}")

gene_ids = {row["GeneID"] for row in high_confidence}
gene_mode_keys = {(row["mode"], row["geneSymbol"]) for row in high_confidence}
if len(high_confidence) != 785 or len(gene_ids) != 442 or len(gene_mode_keys) != 669:
    raise ValueError("High-confidence event and gene counts disagree with the documented results")
for filename in ("SE_high_confidence_genes_best_event.tsv", "SE_high_confidence_genes_highest_count.tsv"):
    gene_rows = read_tsv(SUMMARY / filename)
    keys = [(row["mode"], row["geneSymbol"]) for row in gene_rows]
    if len(keys) != len(gene_mode_keys) or set(keys) != gene_mode_keys:
        raise ValueError(f"Gene-by-mode records disagree with high-confidence events: {filename}")

print(
    f"Validated {len(samples)} samples, {len(counts)} event summaries, "
    f"{len(high_confidence)} high-confidence events, {len(gene_ids)} distinct genes, "
    f"and {len(gene_mode_keys)} gene-by-mode records."
)
