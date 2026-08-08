"""Compute explicit coverage, MCP defaults, applicability, and review fields."""

from __future__ import annotations

from collections.abc import Iterable

from .models import (
    ANNOTATION_DEFAULTS,
    CONDITIONALLY_APPLICABLE_HINTS,
    MCP_SCHEMA_VERSION,
    REPORT_SCHEMA_VERSION,
    AnnotationAudit,
    AnnotationSource,
    AuditReport,
    AuditSummary,
    Coverage,
    ToolAudit,
    ToolDefinition,
)


REVIEW_BASIS = "omitted_applicable_annotations"
INTERPRETATION = (
    "Manual review fields are omitted applicable annotations; they are not "
    "detected errors or vulnerabilities."
)


def _coverage(explicit: int, applicable: int) -> Coverage:
    percentage = round(100 * explicit / applicable, 1) if applicable else None
    return Coverage(
        applicable_fields=applicable,
        explicit_applicable_fields=explicit,
        coverage_percent=percentage,
    )


def _audit_tool(tool: ToolDefinition) -> ToolAudit:
    effective = tool.effective_annotations
    annotations: dict[str, AnnotationAudit] = {}

    for hint in ANNOTATION_DEFAULTS:
        source: AnnotationSource = (
            "explicit" if hint in tool.annotations else "mcp_default"
        )
        applicable = not (
            effective["readOnlyHint"]
            and hint in CONDITIONALLY_APPLICABLE_HINTS
        )
        annotations[hint] = AnnotationAudit(
            value=effective[hint],
            source=source,
            applicable=applicable,
        )

    applicable_count = sum(item.applicable for item in annotations.values())
    explicit_count = sum(
        item.applicable and item.explicit for item in annotations.values()
    )
    review_fields = tuple(
        hint for hint, item in annotations.items() if item.manual_review
    )
    return ToolAudit(
        name=tool.name,
        coverage=_coverage(explicit_count, applicable_count),
        annotations=annotations,
        manual_review_fields=review_fields,
    )


def audit_tools(tools: Iterable[ToolDefinition]) -> AuditReport:
    """Audit tools without consulting descriptions or implementation behavior."""

    tool_definitions = tuple(tools)
    tool_audits = tuple(_audit_tool(tool) for tool in tool_definitions)

    annotation_coverage: dict[str, Coverage] = {}
    for hint in ANNOTATION_DEFAULTS:
        statuses = tuple(tool.annotations[hint] for tool in tool_audits)
        applicable = sum(item.applicable for item in statuses)
        explicit = sum(item.applicable and item.explicit for item in statuses)
        annotation_coverage[hint] = _coverage(explicit, applicable)

    applicable_total = sum(
        tool.coverage.applicable_fields for tool in tool_audits
    )
    explicit_total = sum(
        tool.coverage.explicit_applicable_fields for tool in tool_audits
    )
    with_any_explicit = sum(bool(tool.annotations) for tool in tool_definitions)
    with_review = sum(bool(tool.manual_review_fields) for tool in tool_audits)
    summary = AuditSummary(
        tools=len(tool_audits),
        tools_with_any_explicit_annotations=with_any_explicit,
        tools_with_no_explicit_annotations=len(tool_audits) - with_any_explicit,
        tools_with_full_applicable_coverage=len(tool_audits) - with_review,
        tools_with_manual_review_fields=with_review,
        coverage=_coverage(explicit_total, applicable_total),
    )
    return AuditReport(
        summary=summary,
        annotation_coverage=annotation_coverage,
        tools=tool_audits,
    )


def _coverage_dict(coverage: Coverage) -> dict[str, int | float | None]:
    return {
        "applicable_fields": coverage.applicable_fields,
        "explicit_applicable_fields": coverage.explicit_applicable_fields,
        "coverage_percent": coverage.coverage_percent,
    }


def report_to_dict(report: AuditReport) -> dict[str, object]:
    """Serialize an audit report to the stable JSON-compatible schema."""

    summary = report.summary
    return {
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "mcp_schema_version": MCP_SCHEMA_VERSION,
        "review_basis": REVIEW_BASIS,
        "interpretation": INTERPRETATION,
        "summary": {
            "tools": summary.tools,
            "tools_with_any_explicit_annotations": (
                summary.tools_with_any_explicit_annotations
            ),
            "tools_with_no_explicit_annotations": (
                summary.tools_with_no_explicit_annotations
            ),
            "tools_with_full_applicable_coverage": (
                summary.tools_with_full_applicable_coverage
            ),
            "tools_with_manual_review_fields": (
                summary.tools_with_manual_review_fields
            ),
            **_coverage_dict(summary.coverage),
        },
        "annotation_coverage": {
            hint: {
                "mcp_default": default,
                **_coverage_dict(report.annotation_coverage[hint]),
            }
            for hint, default in ANNOTATION_DEFAULTS.items()
        },
        "tools": [
            {
                "name": tool.name,
                "coverage": _coverage_dict(tool.coverage),
                "manual_review": {
                    "suggested": bool(tool.manual_review_fields),
                    "basis": REVIEW_BASIS,
                    "fields": list(tool.manual_review_fields),
                },
                "annotations": {
                    hint: {
                        "value": status.value,
                        "source": status.source,
                        "explicit": status.explicit,
                        "applicable": status.applicable,
                        "manual_review": status.manual_review,
                    }
                    for hint, status in tool.annotations.items()
                },
            }
            for tool in report.tools
        ],
    }
