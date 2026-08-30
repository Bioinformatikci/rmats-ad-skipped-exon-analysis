#!/usr/bin/env python3
"""Select predefined skipped-exon events and prepare rMATS2Sashimiplot inputs."""

import csv
import os
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
PROJECT_ROOT = Path(os.environ.get("PROJECT_ROOT", REPO_ROOT.parent))
RMATS_SE = Path(os.environ.get("RMATS_SE_FILE", PROJECT_ROOT / "results" / "rmats" / "out" / "SE.MATS.JCEC.txt"))
CONFIG = Path(os.environ.get("SASHIMI_EVENT_CONFIG", REPO_ROOT / "config" / "selected_sashimi_events.tsv"))
OUT_DIR = Path(os.environ.get("SASHIMI_SELECTED_DIR", REPO_ROOT / "results" / "sashimi_selected"))


def read_requested_events():
    with CONFIG.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return [(row["geneSymbol"], row["exonStart_0base"], row["exonEnd"]) for row in reader]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    requested = read_requested_events()

    with RMATS_SE.open(newline="") as handle:
        rows = list(csv.reader(handle, delimiter="\t"))
    header = rows[0]
    body = rows[1:]

    selected = []
    for key in requested:
        matches = [row for row in body if (row[2], row[5], row[6]) == key]
        if not matches:
            raise SystemExit(f"Missing selected SE event: {key}")
        selected.append(min(matches, key=lambda row: float(row[19])))

    event_file = OUT_DIR / "selected_SE_events_for_sashimi.txt"
    with event_file.open("w", newline="") as handle:
        csv.writer(handle, delimiter="\t", lineterminator="\n").writerows([header] + selected)

    summary_file = OUT_DIR / "selected_SE_events_summary.tsv"
    with summary_file.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow([
            "rank", "ID", "geneSymbol", "GeneID", "chr", "strand",
            "exonStart_0base", "exonEnd", "PValue", "FDR",
            "IncLevelDifference", "IncLevel1_AD", "IncLevel2_control",
        ])
        for rank, row in enumerate(selected, start=1):
            writer.writerow([rank, row[0], row[2], row[1], row[3], row[4], row[5], row[6], row[18], row[19], row[22], row[20], row[21]])

    print(event_file)
    print(summary_file)


if __name__ == "__main__":
    main()
