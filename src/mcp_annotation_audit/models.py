"""Data models and MCP annotation constants used by the audit."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


MCP_SCHEMA_VERSION = "2025-11-25"
REPORT_SCHEMA_VERSION = 1

ANNOTATION_DEFAULTS: dict[str, bool] = {
    "readOnlyHint": False,
    "destructiveHint": True,
    "idempotentHint": False,
    "openWorldHint": True,
}
SUPPORTED_HINTS = tuple(ANNOTATION_DEFAULTS)
CONDITIONALLY_APPLICABLE_HINTS = frozenset(
    {"destructiveHint", "idempotentHint"}
)

AnnotationSource = Literal["explicit", "mcp_default"]


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    """The Tool fields needed by the audit; annotations are explicit values only."""

    name: str
    annotations: dict[str, bool] = field(default_factory=dict)

    @property
    def effective_annotations(self) -> dict[str, bool]:
        """Overlay explicit values on the MCP defaults."""

        return {
            hint: self.annotations.get(hint, default)
            for hint, default in ANNOTATION_DEFAULTS.items()
        }


@dataclass(frozen=True, slots=True)
class AnnotationAudit:
    """One annotation's effective value, provenance, and applicability."""

    value: bool
    source: AnnotationSource
    applicable: bool

    @property
    def explicit(self) -> bool:
        return self.source == "explicit"

    @property
    def manual_review(self) -> bool:
        """Omitted applicable fields are candidates for human review only."""

        return self.applicable and not self.explicit


@dataclass(frozen=True, slots=True)
class Coverage:
    """Applicable annotation coverage for a scope in the report."""

    applicable_fields: int
    explicit_applicable_fields: int
    coverage_percent: float | None


@dataclass(frozen=True, slots=True)
class ToolAudit:
    """Coverage and review information for one Tool."""

    name: str
    coverage: Coverage
    annotations: dict[str, AnnotationAudit]
    manual_review_fields: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AuditSummary:
    """Aggregate Tool and applicable-field counts."""

    tools: int
    tools_with_any_explicit_annotations: int
    tools_with_no_explicit_annotations: int
    tools_with_full_applicable_coverage: int
    tools_with_manual_review_fields: int
    coverage: Coverage


@dataclass(frozen=True, slots=True)
class AuditReport:
    """Complete deterministic annotation audit report."""

    summary: AuditSummary
    annotation_coverage: dict[str, Coverage]
    tools: tuple[ToolAudit, ...]
