#!/usr/bin/env python3
"""Build the pilot's flat datasets and metrics from frozen linter output."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULTS = {
    "readOnlyHint": False,
    "destructiveHint": True,
    "idempotentHint": False,
    "openWorldHint": True,
}
RULE_ANNOTATIONS = {
    "MCP001": "readOnlyHint",
    "MCP002": "destructiveHint",
    "MCP003": "idempotentHint",
    "MCP004": "openWorldHint",
}
FILE_TO_REPOSITORY = {
    "mark3labs_mcp-filesystem-server": "mark3labs/mcp-filesystem-server",
    "github_github-mcp-server": "github/github-mcp-server",
    "microsoft_playwright-mcp": "microsoft/playwright-mcp",
    "KnockOutEZ_wigolo": "KnockOutEZ/wigolo",
    "korotovsky_slack-mcp-server": "korotovsky/slack-mcp-server",
    "makenotion_notion-mcp-server": "makenotion/notion-mcp-server",
    "t8y2_dbx": "t8y2/dbx",
    "modelcontextprotocol_servers": "modelcontextprotocol/servers",
}


def text_bool(value: bool) -> str:
    return str(value).lower()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


repositories = {
    row["repository"]: row for row in read_csv(ROOT / "repositories.csv")
}
manual_rows = read_csv(ROOT / "manual_classifications.csv")
manual = {
    (row["repository"], row["tool"], row["rule_id"]): row
    for row in manual_rows
}

tools_by_repository: dict[str, list[dict[str, object]]] = {}
tool_rows: list[dict[str, object]] = []
for path in sorted((ROOT / "tools").glob("*.json")):
    repository = FILE_TO_REPOSITORY[path.stem]
    tools = json.loads(path.read_text(encoding="utf-8"))
    tools_by_repository[repository] = tools
    repo = repositories[repository]
    for tool in tools:
        annotations = tool["annotations"]
        effective = {
            hint: annotations.get(hint, default)
            for hint, default in DEFAULTS.items()
        }
        row: dict[str, object] = {
            "repository": repository,
            "repository_url": repo["repository_url"],
            "pinned_commit": repo["pinned_commit"],
            "source_server": tool.get("_source_server", ""),
            "tool": tool["name"],
            "description": tool["description"],
            "source": tool.get("_source", ""),
        }
        for hint in DEFAULTS:
            applicable = not (
                hint in ("destructiveHint", "idempotentHint")
                and effective["readOnlyHint"] is True
            )
            row[f"{hint}_explicit"] = text_bool(hint in annotations)
            row[f"{hint}_value"] = (
                text_bool(annotations[hint]) if hint in annotations else ""
            )
            row[f"{hint}_effective"] = text_bool(effective[hint])
            row[f"{hint}_applicable"] = text_bool(applicable)
        tool_rows.append(row)

tool_fields = [
    "repository",
    "repository_url",
    "pinned_commit",
    "source_server",
    "tool",
    "description",
    "source",
]
for annotation in DEFAULTS:
    tool_fields.extend(
        [
            f"{annotation}_explicit",
            f"{annotation}_value",
            f"{annotation}_effective",
            f"{annotation}_applicable",
        ]
    )
write_csv(ROOT / "tools.csv", tool_fields, tool_rows)


finding_rows: list[dict[str, object]] = []
semantic_keys: set[tuple[str, str, str]] = set()
findings_by_repository: dict[str, list[dict[str, object]]] = {}
for path in sorted((ROOT / "linter").glob("*.json")):
    repository = FILE_TO_REPOSITORY[path.stem]
    repo = repositories[repository]
    findings = json.loads(path.read_text(encoding="utf-8"))
    findings_by_repository[repository] = findings
    by_name = {tool["name"]: tool for tool in tools_by_repository[repository]}
    for finding in findings:
        tool = by_name[finding["tool"]]
        annotations = tool["annotations"]
        rule_id = finding["rule_id"]
        if rule_id == "MCP005":
            match = re.search(r"'([^']+)' was not explicitly", finding["message"])
            if match is None:
                raise AssertionError(f"cannot identify MCP005 annotation: {finding}")
            annotation = match.group(1)
            classification = "COVERAGE_INFO"
            reason = (
                f"{annotation} is omitted; its effective MCP default is "
                f"{text_bool(DEFAULTS[annotation])}. This is coverage information, "
                "not a vulnerability classification."
            )
            behavior_evidence = ""
        else:
            annotation = RULE_ANNOTATIONS[rule_id]
            key = (repository, finding["tool"], rule_id)
            semantic_keys.add(key)
            reviewed = manual[key]
            classification = reviewed["classification"]
            reason = reviewed["reason"]
            behavior_evidence = reviewed["behavior_evidence"]

        effective = annotations.get(annotation, DEFAULTS[annotation])
        finding_rows.append(
            {
                "repository": repository,
                "repository_url": repo["repository_url"],
                "tool": finding["tool"],
                "rule_id": rule_id,
                "severity": finding["severity"],
                "annotation": annotation,
                "annotation_value": (
                    text_bool(annotations[annotation])
                    if annotation in annotations
                    else "omitted"
                ),
                "annotation_explicit": text_bool(annotation in annotations),
                "effective_value": text_bool(effective),
                "evidence": finding["evidence"],
                "linter_message": finding["message"],
                "classification": classification,
                "reason": reason,
                "behavior_evidence": behavior_evidence,
            }
        )

if semantic_keys != set(manual):
    missing_reviews = semantic_keys - set(manual)
    extra_reviews = set(manual) - semantic_keys
    raise AssertionError(
        f"manual review mismatch; missing={missing_reviews}, extra={extra_reviews}"
    )

finding_fields = [
    "repository",
    "repository_url",
    "tool",
    "rule_id",
    "severity",
    "annotation",
    "annotation_value",
    "annotation_explicit",
    "effective_value",
    "evidence",
    "linter_message",
    "classification",
    "reason",
    "behavior_evidence",
]
write_csv(ROOT / "findings.csv", finding_fields, finding_rows)


stats_rows: list[dict[str, object]] = []
for repository, repo in repositories.items():
    analyzed = repo["extraction_status"] == "ANALYZED"
    tools = tools_by_repository.get(repository, [])
    findings = findings_by_repository.get(repository, [])
    classifications = Counter(
        row["classification"]
        for row in finding_rows
        if row["repository"] == repository and row["rule_id"] != "MCP005"
    )

    tools_with_annotations = 0
    tools_missing_annotations = 0
    tools_with_full_coverage = 0
    tools_with_no_annotations = 0
    applicable_slots = 0
    covered_slots = 0
    for tool in tools:
        annotations = tool["annotations"]
        effective_read_only = annotations.get("readOnlyHint", False)
        applicable = ["readOnlyHint", "openWorldHint"]
        if not effective_read_only:
            applicable.extend(["destructiveHint", "idempotentHint"])
        tools_with_annotations += bool(annotations)
        tools_with_no_annotations += not bool(annotations)
        missing = [hint for hint in applicable if hint not in annotations]
        tools_missing_annotations += bool(missing)
        tools_with_full_coverage += not missing
        applicable_slots += len(applicable)
        covered_slots += sum(hint in annotations for hint in applicable)

    stats_rows.append(
        {
            "repository": repository,
            "extraction_status": repo["extraction_status"],
            "tools_analyzed": len(tools) if analyzed else 0,
            "tools_with_annotations": tools_with_annotations,
            "tools_with_no_annotations": tools_with_no_annotations,
            "tools_missing_annotations": tools_missing_annotations,
            "tools_with_full_applicable_coverage": tools_with_full_coverage,
            "applicable_annotation_slots": applicable_slots,
            "explicitly_covered_applicable_slots": covered_slots,
            "warnings": sum(f["severity"] == "WARN" for f in findings),
            "high_findings": sum(f["severity"] == "HIGH" for f in findings),
            "coverage_items": sum(f["rule_id"] == "MCP005" for f in findings),
            "true_positives": classifications["TRUE_POSITIVE"],
            "likely_true_positives": classifications["LIKELY_TRUE_POSITIVE"],
            "false_positives": classifications["FALSE_POSITIVE"],
            "inconclusive": classifications["INCONCLUSIVE"],
        }
    )

stats_fields = [
    "repository",
    "extraction_status",
    "tools_analyzed",
    "tools_with_annotations",
    "tools_with_no_annotations",
    "tools_missing_annotations",
    "tools_with_full_applicable_coverage",
    "applicable_annotation_slots",
    "explicitly_covered_applicable_slots",
    "warnings",
    "high_findings",
    "coverage_items",
    "true_positives",
    "likely_true_positives",
    "false_positives",
    "inconclusive",
]
write_csv(ROOT / "repository_stats.csv", stats_fields, stats_rows)


totals = Counter()
for row in stats_rows:
    if row["extraction_status"] != "ANALYZED":
        continue
    for field in stats_fields[2:]:
        totals[field] += int(row[field])

decidable = (
    totals["true_positives"]
    + totals["likely_true_positives"]
    + totals["false_positives"]
)
false_positive_rate = (
    100 * totals["false_positives"] / decidable if decidable else None
)
repositories_with_confirmed_or_likely = sum(
    int(row["true_positives"]) + int(row["likely_true_positives"]) > 0
    for row in stats_rows
)
repositories_with_usable_annotations = sum(
    int(row["tools_with_annotations"]) > 0 for row in stats_rows
)

if (
    repositories_with_confirmed_or_likely >= 2
    and false_positive_rate is not None
    and false_positive_rate <= 30
):
    hypothesis_decision = "SUPPORTED"
elif repositories_with_confirmed_or_likely >= 1:
    hypothesis_decision = "PARTIALLY_SUPPORTED"
elif (
    repositories_with_usable_annotations >= 7
    and totals["tools_with_annotations"] >= 50
):
    hypothesis_decision = "NOT_SUPPORTED"
else:
    hypothesis_decision = "INCONCLUSIVE"

metrics = {
    "repositories_selected": len(repositories),
    "repositories_analyzed": sum(
        row["extraction_status"] == "ANALYZED" for row in stats_rows
    ),
    "inconclusive_repositories": sum(
        row["extraction_status"] != "ANALYZED" for row in stats_rows
    ),
    "repositories_with_usable_annotations": repositories_with_usable_annotations,
    "total_tools_analyzed": totals["tools_analyzed"],
    "tools_with_annotations": totals["tools_with_annotations"],
    "percentage_tools_with_annotations": round(
        100 * totals["tools_with_annotations"] / totals["tools_analyzed"], 2
    ),
    "tools_with_no_annotations": totals["tools_with_no_annotations"],
    "percentage_tools_with_no_annotations": round(
        100 * totals["tools_with_no_annotations"] / totals["tools_analyzed"], 2
    ),
    "tools_missing_at_least_one_applicable_annotation": totals[
        "tools_missing_annotations"
    ],
    "percentage_tools_missing_at_least_one_applicable_annotation": round(
        100 * totals["tools_missing_annotations"] / totals["tools_analyzed"], 2
    ),
    "tools_with_full_applicable_annotation_coverage": totals[
        "tools_with_full_applicable_coverage"
    ],
    "applicable_annotation_slots": totals["applicable_annotation_slots"],
    "explicitly_covered_applicable_slots": totals[
        "explicitly_covered_applicable_slots"
    ],
    "applicable_annotation_slot_coverage_percent": round(
        100
        * totals["explicitly_covered_applicable_slots"]
        / totals["applicable_annotation_slots"],
        2,
    ),
    "total_lint_findings_including_coverage": len(finding_rows),
    "semantic_review_candidates": totals["warnings"] + totals["high_findings"],
    "coverage_information_items": totals["coverage_items"],
    "high_findings": totals["high_findings"],
    "warning_findings": totals["warnings"],
    "true_positives": totals["true_positives"],
    "likely_true_positives": totals["likely_true_positives"],
    "false_positives": totals["false_positives"],
    "inconclusive_findings": totals["inconclusive"],
    "approximate_false_positive_rate_percent": (
        round(false_positive_rate, 2) if false_positive_rate is not None else None
    ),
    "hypothesis_decision": hypothesis_decision,
}
(ROOT / "metrics.json").write_text(
    json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
)

print(json.dumps(metrics, indent=2))
