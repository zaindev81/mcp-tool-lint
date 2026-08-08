"""Command-line interface for mcp-tool-lint."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path

from .models import Finding, ToolDefinition
from .parser import ToolInputError, load_tools
from .rules import lint_tool


_STATUS_MARKERS = {
    "HIGH": ("✗", "x"),
    "WARN": ("△", "!"),
    "INFO": ("ⓘ", "i"),
    "OK": ("✓", "+"),
}


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mcp-tool-lint",
        description="Report suspicious or missing MCP Tool annotations.",
    )
    parser.add_argument("input", type=Path, help="JSON file containing MCP Tool definitions")
    parser.add_argument("--json", action="store_true", help="emit findings as JSON")
    return parser


def _marker(findings: list[Finding]) -> str:
    severities = {finding.severity for finding in findings}
    if "HIGH" in severities:
        status = "HIGH"
    elif "WARN" in severities:
        status = "WARN"
    elif "INFO" in severities:
        status = "INFO"
    else:
        status = "OK"

    unicode_marker, ascii_marker = _STATUS_MARKERS[status]
    encoding = getattr(sys.stdout, "encoding", None)
    if encoding is None:
        return unicode_marker
    try:
        unicode_marker.encode(encoding)
    except (LookupError, UnicodeEncodeError):
        return ascii_marker
    return unicode_marker


def _print_human(results: list[tuple[ToolDefinition, list[Finding]]]) -> None:
    for index, (tool, findings) in enumerate(results):
        if index:
            print()
        print(f"{_marker(findings)} {tool.name}")
        if not findings:
            print("  OK")
            continue
        for finding in findings:
            print(
                f"  {finding.severity} [{finding.rule_id}]: {finding.message} "
                f"(evidence: {finding.evidence})"
            )


def _print_json(findings: list[Finding]) -> None:
    print(json.dumps([asdict(finding) for finding in findings], indent=2, ensure_ascii=False))


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return its process exit code."""

    args = _argument_parser().parse_args(argv)
    try:
        tools = load_tools(args.input)
    except ToolInputError as exc:
        print(f"mcp-tool-lint: error: {exc}", file=sys.stderr)
        return 2

    results = [(tool, lint_tool(tool)) for tool in tools]
    findings = [finding for _, tool_findings in results for finding in tool_findings]

    if args.json:
        _print_json(findings)
    else:
        _print_human(results)

    return 1 if any(finding.severity == "HIGH" for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
