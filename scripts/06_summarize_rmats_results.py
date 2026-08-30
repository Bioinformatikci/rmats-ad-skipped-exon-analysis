#!/usr/bin/env python3
"""Summarize rMATS event tables and export compact filtered result tables."""

import csv
import os
from collections import Counter, defaultdict
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
PROJECT_ROOT = Path(os.environ.get("PROJECT_ROOT", REPO_ROOT.parent))
RMATS_OUT = Path(os.environ.get("RMATS_OUT_DIR", PROJECT_ROOT / "results" / "rmats" / "out"))
SUMMARY_DIR = Path(os.environ.get("RMATS_SUMMARY_DIR", PROJECT_ROOT / "results" / "rmats" / "summary"))
REPO_SUMMARY_DIR = REPO_ROOT / "results" / "rmats_summary"

EVENT_TYPES = ["SE", "A5SS", "A3SS", "MXE", "RI"]
MODES = ["JC", "JCEC"]
FDR_CUTOFF = float(os.environ.get("FDR_CUTOFF", "0.05"))
DELTA_CUTOFF = float(os.environ.get("DELTA_PSI_CUTOFF", "0.10"))


def parse_float(value):
    if value in {"", "NA", "nan"}:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def clean(value):
    return value.strip().strip('"')


def event_coordinates(event_type, row):
    chrom = row.get("chr", "")
    strand = row.get("strand", "")
    if event_type == "SE":
        return f"{chrom}:{row['exonStart_0base']}-{row['exonEnd']}({strand})"
    if event_type in {"A5SS", "A3SS"}:
        return f"{chrom}:{row['longExonStart_0base']}-{row['longExonEnd']}|{row['shortES']}-{row['shortEE']}({strand})"
    if event_type == "MXE":
        return f"{chrom}:{row['1stExonStart_0base']}-{row['1stExonEnd']}|{row['2ndExonStart_0base']}-{row['2ndExonEnd']}({strand})"
    if event_type == "RI":
        return f"{chrom}:{row['riExonStart_0base']}-{row['riExonEnd']}({strand})"
    return f"{chrom}({strand})"


def direction(delta):
    if delta is None:
        return "NA"
    return "AD_higher_inclusion" if delta > 0 else "control_higher_inclusion"


def read_events(event_type, mode):
    path = RMATS_OUT / f"{event_type}.MATS.{mode}.txt"
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            fdr = parse_float(row.get("FDR", ""))
            delta = parse_float(row.get("IncLevelDifference", ""))
            if fdr is None or delta is None:
                continue
            row["_FDR"] = fdr
            row["_delta"] = delta
            yield row


def write_table(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    REPO_SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

    overview_rows = []
    top_rows = []
    global_rows = []
    gene_counter = defaultdict(Counter)

    for event_type in EVENT_TYPES:
        for mode in MODES:
            rows = list(read_events(event_type, mode))
            significant = [
                row for row in rows
                if row["_FDR"] < FDR_CUTOFF and abs(row["_delta"]) >= DELTA_CUTOFF
            ]
            overview_rows.append({
                "event_type": event_type,
                "counting_mode": mode,
                "total_tested": len(rows),
                "significant_fdr_lt_0_05_abs_delta_ge_0_10": len(significant),
                "AD_higher_inclusion": sum(1 for row in significant if row["_delta"] > 0),
                "control_higher_inclusion": sum(1 for row in significant if row["_delta"] < 0),
            })

            if rows:
                filtered_fields = [name for name in rows[0].keys() if not name.startswith("_")]
                filtered_rows = [
                    {key: row.get(key, "") for key in filtered_fields}
                    for row in sorted(significant, key=lambda item: (item["_FDR"], -abs(item["_delta"])))
                ]
                write_table(
                    SUMMARY_DIR / f"{event_type}.MATS.{mode}.filtered_FDR0.05_delta0.10.tsv",
                    filtered_fields,
                    filtered_rows,
                )
                write_table(
                    REPO_SUMMARY_DIR / f"{event_type}.MATS.{mode}.filtered_FDR0.05_delta0.10.tsv",
                    filtered_fields,
                    filtered_rows,
                )

            for row in significant:
                gene = clean(row.get("geneSymbol", ""))
                if gene:
                    gene_counter[(mode, gene)][event_type] += 1

            for rank, row in enumerate(
                sorted(significant, key=lambda item: (item["_FDR"], -abs(item["_delta"])))[:20],
                start=1,
            ):
                event_row = {
                    "rank": rank,
                    "event_type": event_type,
                    "counting_mode": mode,
                    "geneSymbol": clean(row.get("geneSymbol", "")),
                    "GeneID": clean(row.get("GeneID", "")),
                    "coordinates": event_coordinates(event_type, row),
                    "FDR": row.get("FDR", ""),
                    "PValue": row.get("PValue", ""),
                    "IncLevelDifference": row.get("IncLevelDifference", ""),
                    "direction": direction(row["_delta"]),
                    "IncLevel_AD": row.get("IncLevel1", ""),
                    "IncLevel_control": row.get("IncLevel2", ""),
                    "IJC_AD": row.get("IJC_SAMPLE_1", ""),
                    "SJC_AD": row.get("SJC_SAMPLE_1", ""),
                    "IJC_control": row.get("IJC_SAMPLE_2", ""),
                    "SJC_control": row.get("SJC_SAMPLE_2", ""),
                }
                top_rows.append(event_row)
                global_rows.append({**event_row, "_FDR": row["_FDR"], "_delta_abs": abs(row["_delta"])})

    common_fields = [
        "rank", "event_type", "counting_mode", "geneSymbol", "GeneID", "coordinates",
        "FDR", "PValue", "IncLevelDifference", "direction", "IncLevel_AD",
        "IncLevel_control", "IJC_AD", "SJC_AD", "IJC_control", "SJC_control",
    ]
    overview_fields = [
        "event_type", "counting_mode", "total_tested",
        "significant_fdr_lt_0_05_abs_delta_ge_0_10",
        "AD_higher_inclusion", "control_higher_inclusion",
    ]

    write_table(SUMMARY_DIR / "filtered_event_counts.tsv", overview_fields, overview_rows)
    write_table(REPO_SUMMARY_DIR / "filtered_event_counts.tsv", overview_fields, overview_rows)
    write_table(SUMMARY_DIR / "top_events_by_FDR.tsv", common_fields, top_rows)
    write_table(
        SUMMARY_DIR / "top_events_global_by_FDR.tsv",
        common_fields,
        [{**{k: row.get(k, "") for k in common_fields}, "rank": rank}
         for rank, row in enumerate(sorted(global_rows, key=lambda item: (item["_FDR"], -item["_delta_abs"]))[:100], 1)],
    )
    write_table(
        REPO_SUMMARY_DIR / "top_events_global_by_FDR.tsv",
        common_fields,
        [{**{k: row.get(k, "") for k in common_fields}, "rank": rank}
         for rank, row in enumerate(sorted(global_rows, key=lambda item: (item["_FDR"], -item["_delta_abs"]))[:100], 1)],
    )

    gene_rows = []
    for (mode, gene), counts in gene_counter.items():
        gene_rows.append({
            "counting_mode": mode,
            "geneSymbol": gene,
            "total_significant_events": sum(counts.values()),
            "SE": counts["SE"],
            "A5SS": counts["A5SS"],
            "A3SS": counts["A3SS"],
            "MXE": counts["MXE"],
            "RI": counts["RI"],
        })

    gene_fields = ["counting_mode", "geneSymbol", "total_significant_events", "SE", "A5SS", "A3SS", "MXE", "RI"]
    gene_rows.sort(key=lambda item: (item["counting_mode"], -item["total_significant_events"], item["geneSymbol"]))
    write_table(SUMMARY_DIR / "top_genes_by_significant_events.tsv", gene_fields, gene_rows)
    write_table(REPO_SUMMARY_DIR / "top_genes_by_significant_events.tsv", gene_fields, gene_rows)


if __name__ == "__main__":
    main()
