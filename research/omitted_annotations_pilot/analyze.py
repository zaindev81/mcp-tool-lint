#!/usr/bin/env python3
"""Validate the locked audit and generate descriptive result artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


EXPECTED_SAMPLE_SHA256 = (
    "5789400ef5bf1ee47a75a42e818375cc20f83c418c8d7702da67b143c09e3399"
)
EXPECTED_CLASSIFICATIONS_SHA256 = (
    "a0ecf1db52df60b89c30789da524d8246a7912a83295e8aeb11ce17de30e8931"
)
LABELS = ("CORRECT", "CONSERVATIVE_IMPRECISE", "WRONG", "INCONCLUSIVE")
ANNOTATIONS = (
    "readOnlyHint",
    "destructiveHint",
    "idempotentHint",
    "openWorldHint",
)
SUPPORTIVE = {"CONSERVATIVE_IMPRECISE", "WRONG"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def pct(count: int, denominator: int) -> float:
    return round(100 * count / denominator, 4) if denominator else 0.0


def validate_and_join(
    sample_path: Path, classifications_path: Path
) -> list[dict[str, str]]:
    if digest(sample_path) != EXPECTED_SAMPLE_SHA256:
        raise ValueError("sample.csv does not match its frozen SHA-256")
    if digest(classifications_path) != EXPECTED_CLASSIFICATIONS_SHA256:
        raise ValueError("classifications.csv does not match its locked SHA-256")

    samples = read_csv(sample_path)
    classifications = read_csv(classifications_path)
    if len(samples) != 40 or len(classifications) != 40:
        raise ValueError("expected exactly 40 sample and classification rows")

    decisions = {row["sample_id"]: row for row in classifications}
    if len(decisions) != 40:
        raise ValueError("classification sample IDs are not unique")
    if set(decisions) != {row["sample_id"] for row in samples}:
        raise ValueError("sample and classification IDs differ")

    rows: list[dict[str, str]] = []
    for sample in samples:
        decision = decisions[sample["sample_id"]]
        label = decision["classification"]
        actual = decision["actual_value"]
        default = sample["effective_default"]
        if label not in LABELS:
            raise ValueError(f"unknown classification {label}")
        if label == "INCONCLUSIVE":
            if actual != "unknown" or not decision["inconclusive_reason"].strip():
                raise ValueError("inconclusive rows need unknown value and a reason")
        else:
            if actual not in {"true", "false"}:
                raise ValueError("conclusive rows need a boolean actual value")
            if label == "CORRECT" and actual != default:
                raise ValueError("CORRECT row conflicts with effective default")
            if label in SUPPORTIVE and actual == default:
                raise ValueError("supportive row does not oppose effective default")
        rows.append({**sample, **{k: v for k, v in decision.items() if k != "sample_id"}})

    if Counter(row["annotation_type"] for row in rows) != Counter(
        {annotation: 10 for annotation in ANNOTATIONS}
    ):
        raise ValueError("sample is not balanced 10-per-annotation")
    if len({row["field_unit_id"] for row in rows}) != 40:
        raise ValueError("field units are not unique")
    return rows


def group_statistics(
    rows: list[dict[str, str]], key: str, output_key: str
) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row[key]].append(row)

    output: list[dict[str, object]] = []
    for name in sorted(grouped):
        members = grouped[name]
        counts = Counter(row["classification"] for row in members)
        total = len(members)
        conclusive = total - counts["INCONCLUSIVE"]
        supportive = sum(counts[label] for label in SUPPORTIVE)
        record: dict[str, object] = {
            output_key: name,
            "sampled": total,
            "conclusive": conclusive,
        }
        for label in LABELS:
            stem = label.lower()
            record[f"{stem}_count"] = counts[label]
            record[f"{stem}_pct_all"] = pct(counts[label], total)
        record["supportive_count"] = supportive
        record["supportive_pct_all"] = pct(supportive, total)
        record["supportive_pct_conclusive"] = pct(supportive, conclusive)
        output.append(record)
    return output


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_metrics(rows: list[dict[str, str]]) -> dict[str, object]:
    counts = Counter(row["classification"] for row in rows)
    total = len(rows)
    conclusive = total - counts["INCONCLUSIVE"]
    supportive_rows = [row for row in rows if row["classification"] in SUPPORTIVE]
    supportive = len(supportive_rows)
    supportive_repositories = sorted({row["repository"] for row in supportive_rows})
    supportive_annotations = sorted({row["annotation_type"] for row in supportive_rows})

    evaluable = conclusive >= 32
    if not evaluable:
        decision = "INCONCLUSIVE"
    elif (
        supportive >= 8
        and supportive / conclusive >= 0.20
        and len(supportive_repositories) >= 3
        and len(supportive_annotations) >= 2
    ):
        decision = "SUPPORTED"
    elif supportive >= 4 and supportive / conclusive >= 0.10:
        decision = "PARTIALLY_SUPPORTED"
    else:
        decision = "NOT_SUPPORTED"

    return {
        "experiment": "omitted-annotations-v1",
        "sample_size": total,
        "conclusive_count": conclusive,
        "evaluable": evaluable,
        "classification_metrics_all_sampled": {
            label: {"count": counts[label], "percentage": pct(counts[label], total)}
            for label in LABELS
        },
        "classification_metrics_conclusive_only": {
            label: {
                "count": 0 if label == "INCONCLUSIVE" else counts[label],
                "percentage": 0.0
                if label == "INCONCLUSIVE"
                else pct(counts[label], conclusive),
            }
            for label in LABELS
        },
        "supportive": {
            "definition": "CONSERVATIVE_IMPRECISE + WRONG",
            "count": supportive,
            "percentage_all_sampled": pct(supportive, total),
            "percentage_conclusive": pct(supportive, conclusive),
            "repository_count": len(supportive_repositories),
            "repositories": supportive_repositories,
            "annotation_type_count": len(supportive_annotations),
            "annotation_types": supportive_annotations,
        },
        "decision": decision,
        "recommended_next_action": "pivot toward annotation coverage/quality tooling",
        "scope_note": "Descriptive 40-case pilot; no population-level inference.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=Path, required=True)
    parser.add_argument("--classifications", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    rows = validate_and_join(args.sample, args.classifications)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "audit.csv", rows)
    write_csv(
        args.output_dir / "repository_statistics.csv",
        group_statistics(rows, "repository", "repository"),
    )
    annotation_stats = group_statistics(rows, "annotation_type", "annotation_type")
    annotation_order = {name: index for index, name in enumerate(ANNOTATIONS)}
    annotation_stats.sort(key=lambda row: annotation_order[str(row["annotation_type"])])
    write_csv(args.output_dir / "annotation_statistics.csv", annotation_stats)
    metrics = build_metrics(rows)
    (args.output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
