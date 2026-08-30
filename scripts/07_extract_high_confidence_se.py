#!/usr/bin/env python3
"""Extract high-confidence skipped-exon events using FDR, p-value, PSI, and count filters."""

import csv
import os
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
PROJECT_ROOT = Path(os.environ.get("PROJECT_ROOT", REPO_ROOT.parent))
RMATS_OUT = Path(os.environ.get("RMATS_OUT_DIR", PROJECT_ROOT / "results" / "rmats" / "out"))
SUMMARY_OUT = Path(os.environ.get("RMATS_SUMMARY_DIR", PROJECT_ROOT / "results" / "rmats" / "summary"))
REPO_SUMMARY_DIR = REPO_ROOT / "results" / "rmats_summary"

FDR_CUTOFF = float(os.environ.get("FDR_CUTOFF", "0.05"))
PVALUE_CUTOFF = float(os.environ.get("PVALUE_CUTOFF", "0.001"))
DELTA_PSI_CUTOFF = float(os.environ.get("DELTA_PSI_CUTOFF", "0.10"))
TOTAL_COUNT_CUTOFF = int(os.environ.get("TOTAL_COUNT_CUTOFF", "50"))


def parse_float(value):
    try:
        return float(value)
    except ValueError:
        return None


def sum_counts(value):
    total = 0
    for part in value.split(","):
        try:
            total += int(part)
        except ValueError:
            pass
    return total


def clean(value):
    return value.strip().strip('"')


def read_se_events():
    for mode in ("JC", "JCEC"):
        path = RMATS_OUT / f"SE.MATS.{mode}.txt"
        with path.open(newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            for row in reader:
                fdr = parse_float(row["FDR"])
                pvalue = parse_float(row["PValue"])
                delta = parse_float(row["IncLevelDifference"])
                if fdr is None or pvalue is None or delta is None:
                    continue

                total_count = (
                    sum_counts(row["IJC_SAMPLE_1"])
                    + sum_counts(row["SJC_SAMPLE_1"])
                    + sum_counts(row["IJC_SAMPLE_2"])
                    + sum_counts(row["SJC_SAMPLE_2"])
                )

                if (
                    fdr < FDR_CUTOFF
                    and pvalue < PVALUE_CUTOFF
                    and abs(delta) >= DELTA_PSI_CUTOFF
                    and total_count >= TOTAL_COUNT_CUTOFF
                ):
                    yield {
                        "mode": mode,
                        "geneSymbol": clean(row["geneSymbol"]),
                        "GeneID": clean(row["GeneID"]),
                        "exon": f"{row['chr']}:{row['exonStart_0base']}-{row['exonEnd']}({row['strand']})",
                        "PValue": pvalue,
                        "FDR": fdr,
                        "deltaPSI_AD_minus_control": delta,
                        "direction": "AD_higher_inclusion" if delta > 0 else "control_higher_inclusion",
                        "total_count": total_count,
                        "AD_IJC": row["IJC_SAMPLE_1"],
                        "AD_SJC": row["SJC_SAMPLE_1"],
                        "control_IJC": row["IJC_SAMPLE_2"],
                        "control_SJC": row["SJC_SAMPLE_2"],
                        "AD_PSI": row["IncLevel1"],
                        "control_PSI": row["IncLevel2"],
                    }


def write_table(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main():
    SUMMARY_OUT.mkdir(parents=True, exist_ok=True)
    REPO_SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

    rows = sorted(
        read_se_events(),
        key=lambda row: (row["FDR"], row["PValue"], -row["total_count"], -abs(row["deltaPSI_AD_minus_control"])),
    )

    event_fields = [
        "rank", "mode", "geneSymbol", "GeneID", "exon", "PValue", "FDR",
        "deltaPSI_AD_minus_control", "direction", "total_count",
        "AD_IJC", "AD_SJC", "control_IJC", "control_SJC", "AD_PSI", "control_PSI",
    ]
    ranked_events = [{**row, "rank": rank} for rank, row in enumerate(rows, start=1)]
    write_table(SUMMARY_OUT / "SE_high_confidence_lowFDR_lowP_highCount.tsv", event_fields, ranked_events)
    write_table(REPO_SUMMARY_DIR / "SE_high_confidence_lowFDR_lowP_highCount.tsv", event_fields, ranked_events)

    event_count_by_gene = {}
    best_by_gene = {}
    for row in rows:
        key = (row["mode"], row["geneSymbol"])
        event_count_by_gene[key] = event_count_by_gene.get(key, 0) + 1
        best_by_gene.setdefault(key, row)

    gene_rows = []
    for key, row in best_by_gene.items():
        gene_rows.append({**row, "n_significant_SE_events_for_gene": event_count_by_gene[key]})
    gene_rows.sort(key=lambda row: (row["FDR"], -row["total_count"]))

    gene_fields = [
        "rank", "mode", "geneSymbol", "GeneID", "n_significant_SE_events_for_gene",
        "exon", "PValue", "FDR", "deltaPSI_AD_minus_control",
        "direction", "total_count", "AD_PSI", "control_PSI",
    ]
    best_ranked = [{**row, "rank": rank} for rank, row in enumerate(gene_rows, start=1)]
    write_table(SUMMARY_OUT / "SE_high_confidence_genes_best_event.tsv", gene_fields, best_ranked)
    write_table(REPO_SUMMARY_DIR / "SE_high_confidence_genes_best_event.tsv", gene_fields, best_ranked)

    count_ranked = [
        {**row, "rank": rank}
        for rank, row in enumerate(sorted(gene_rows, key=lambda row: (-row["total_count"], row["FDR"])), start=1)
    ]
    write_table(SUMMARY_OUT / "SE_high_confidence_genes_highest_count.tsv", gene_fields, count_ranked)
    write_table(REPO_SUMMARY_DIR / "SE_high_confidence_genes_highest_count.tsv", gene_fields, count_ranked)

    print(f"events\t{len(rows)}")
    print(f"genes\t{len(gene_rows)}")


if __name__ == "__main__":
    main()
