"""Command-line interface for mcp-annotation-audit."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from .audit import INTERPRETATION, audit_tools, report_to_dict
from .models import ANNOTATION_DEFAULTS, MCP_SCHEMA_VERSION, AuditReport, Coverage
from .parser import ToolInputError, load_tools


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mcp-annotation-audit",
        description=(
            "Report explicit MCP Tool annotation coverage, effective defaults, "
            "and applicable fields for manual review."
        ),
    )
    parser.add_argument(
        "input", type=Path, help="JSON file containing MCP Tool definitions"
    )
    parser.add_argument(
        "--json", action="store_true", help="emit the audit report as JSON"
    )
    return parser


def _format_coverage(coverage: Coverage) -> str:
    percentage = (
        "n/a"
        if coverage.coverage_percent is None
        else f"{coverage.coverage_percent:.1f}%"
    )
    return (
        f"{coverage.explicit_applicable_fields}/"
        f"{coverage.applicable_fields} ({percentage})"
    )


def _print_human(report: AuditReport) -> None:
    summary = report.summary
    print("MCP Tool annotation audit")
    print(f"MCP schema: {MCP_SCHEMA_VERSION}")
    print(f"Tools: {summary.tools}")
    print(f"Applicable annotation coverage: {_format_coverage(summary.coverage)}")
    print(
        "Tools with manual review fields: "
        f"{summary.tools_with_manual_review_fields}"
    )
    print(f"Note: {INTERPRETATION}")

    print("\nCoverage by annotation:")
    for hint in ANNOTATION_DEFAULTS:
        print(f"  {hint}: {_format_coverage(report.annotation_coverage[hint])}")

    for tool in report.tools:
        print(f"\n{tool.name}")
        print(f"  Applicable coverage: {_format_coverage(tool.coverage)}")
        for hint, status in tool.annotations.items():
            value = str(status.value).lower()
            source = "explicit" if status.explicit else "MCP default"
            if not status.applicable:
                context = "not applicable while effective readOnlyHint=true"
            elif status.manual_review:
                context = "applicable; manual review field"
            else:
                context = "applicable"
            print(f"  {hint}: {value} ({source}; {context})")

        fields = ", ".join(tool.manual_review_fields) or "none"
        print(f"  Manual review fields: {fields}")


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return its process exit code."""

    args = _argument_parser().parse_args(argv)
    try:
        tools = load_tools(args.input)
    except ToolInputError as exc:
        print(f"mcp-annotation-audit: error: {exc}", file=sys.stderr)
        return 2

    report = audit_tools(tools)
    if args.json:
        print(json.dumps(report_to_dict(report), indent=2, ensure_ascii=False))
    else:
        _print_human(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
