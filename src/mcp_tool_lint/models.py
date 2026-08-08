"""Small data models shared by the parser, rules, and CLI."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


SUPPORTED_HINTS = (
    "readOnlyHint",
    "destructiveHint",
    "idempotentHint",
    "openWorldHint",
)

Severity = Literal["HIGH", "WARN", "INFO"]


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    """The subset of an MCP Tool definition needed by the linter."""

    name: str
    description: str = ""
    annotations: dict[str, bool] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Finding:
    """A single suspicious or missing annotation reported by a rule."""

    tool: str
    rule_id: str
    severity: Severity
    message: str
    evidence: str
