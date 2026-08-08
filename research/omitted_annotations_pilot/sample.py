#!/usr/bin/env python3
"""Generate the pre-registered omitted-annotation field sample."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


SEED = "mcp-tool-lint-omitted-annotations-pilot-2026-08-08-v1"
ANNOTATIONS = (
    "readOnlyHint",
    "destructiveHint",
    "idempotentHint",
    "openWorldHint",
)
DEFAULTS = {
    "readOnlyHint": "false",
    "destructiveHint": "true",
    "idempotentHint": "false",
    "openWorldHint": "true",
}
EXPECTED_INPUT_SHA256 = (
    "d93e30f120fe36c24ff80ed661845005330bd392bf581afc31357a67b21e6a20"
)


def compact_json(values: list[str]) -> str:
    return json.dumps(values, ensure_ascii=False, separators=(",", ":"))


def tool_key(row: dict[str, str]) -> str:
    return compact_json(
        [
            row["repository"],
            row["pinned_commit"],
            row["source_server"],
            row["tool"],
        ]
    )


def field_unit_id(row: dict[str, str], annotation: str) -> str:
    return compact_json(
        [
            row["repository"],
            row["pinned_commit"],
            row["source_server"],
            row["tool"],
            annotation,
        ]
    )


def rank(label: str) -> str:
    return hashlib.sha256(f"{SEED}\0{label}".encode()).hexdigest()


def ranked_units(rows: list[dict[str, str]], annotation: str) -> list[dict[str, str]]:
    return sorted(
        rows,
        key=lambda row: (
            rank(field_unit_id(row, annotation)),
            field_unit_id(row, annotation),
        ),
    )


def generate(input_path: Path) -> list[dict[str, str]]:
    digest = hashlib.sha256(input_path.read_bytes()).hexdigest()
    if digest != EXPECTED_INPUT_SHA256:
        raise ValueError(
            f"input hash mismatch: expected {EXPECTED_INPUT_SHA256}, got {digest}"
        )

    with input_path.open(newline="", encoding="utf-8") as handle:
        inventory = list(csv.DictReader(handle))

    selected: list[tuple[dict[str, str], str]] = []
    selected_tools: set[str] = set()

    for annotation in ANNOTATIONS:
        candidates = [
            row
            for row in inventory
            if row[f"{annotation}_explicit"] == "false"
            and row[f"{annotation}_applicable"] == "true"
            and tool_key(row) not in selected_tools
        ]
        by_repository: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in candidates:
            by_repository[row["repository"]].append(row)

        repositories = sorted(
            by_repository,
            key=lambda repository: (
                rank(f"repo\0{annotation}\0{repository}"),
                repository,
            ),
        )
        stratum: list[dict[str, str]] = []
        stratum_ids: set[str] = set()

        for repository in repositories:
            if len(stratum) == 10:
                break
            row = ranked_units(by_repository[repository], annotation)[0]
            stratum.append(row)
            stratum_ids.add(field_unit_id(row, annotation))

        if len(stratum) < 10:
            remainder = [
                row
                for row in candidates
                if field_unit_id(row, annotation) not in stratum_ids
            ]
            for row in ranked_units(remainder, annotation):
                if len(stratum) == 10:
                    break
                if tool_key(row) in selected_tools:
                    continue
                stratum.append(row)
                stratum_ids.add(field_unit_id(row, annotation))

        if len(stratum) != 10:
            raise ValueError(f"could select only {len(stratum)} rows for {annotation}")
        for row in stratum:
            selected.append((row, annotation))
            selected_tools.add(tool_key(row))

    if len(selected) != 40:
        raise AssertionError(f"expected 40 selections, got {len(selected)}")
    if len(selected_tools) != 40:
        raise AssertionError("sample does not contain 40 distinct tools")

    annotation_counts = Counter(annotation for _, annotation in selected)
    if annotation_counts != Counter({annotation: 10 for annotation in ANNOTATIONS}):
        raise AssertionError(f"unexpected annotation counts: {annotation_counts}")
    if any(not row["source"].strip() for row, _ in selected):
        raise AssertionError("sample contains an empty source pointer")

    output: list[dict[str, str]] = []
    for index, (row, annotation) in enumerate(selected, start=1):
        unit_id = field_unit_id(row, annotation)
        output.append(
            {
                "sample_id": f"S{index:03d}",
                "selection_order": str(index),
                "annotation_type": annotation,
                "effective_default": DEFAULTS[annotation],
                "repository": row["repository"],
                "repository_url": row["repository_url"],
                "pinned_commit": row["pinned_commit"],
                "source_server": row["source_server"],
                "tool": row["tool"],
                "source": row["source"],
                "field_unit_id": unit_id,
                "random_rank": rank(unit_id),
            }
        )
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = generate(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
