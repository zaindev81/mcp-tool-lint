"""Small data models shared by the parser, rules, and CLI."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


ANNOTATION_DEFAULTS: dict[str, bool] = {
    "readOnlyHint": False,
    "destructiveHint": True,
    "idempotentHint": False,
    "openWorldHint": True,
}
SUPPORTED_HINTS = tuple(ANNOTATION_DEFAULTS)

Severity = Literal["HIGH", "WARN", "INFO"]


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    """Tool fields used by the linter; annotations contains explicit values only."""

    name: str
    description: str = ""
    annotations: dict[str, bool] = field(default_factory=dict)

    @property
    def effective_annotations(self) -> dict[str, bool]:
        """Return explicit annotation values overlaid on the MCP defaults."""

        return {
            hint: self.annotations.get(hint, default)
            for hint, default in ANNOTATION_DEFAULTS.items()
        }


@dataclass(frozen=True, slots=True)
class Finding:
    """A single review candidate or annotation coverage item."""

    tool: str
    rule_id: str
    severity: Severity
    message: str
    evidence: str
