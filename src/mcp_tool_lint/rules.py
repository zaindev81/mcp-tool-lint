"""Deterministic heuristic rules for MCP Tool annotations."""

from __future__ import annotations

import re
from collections.abc import Iterable

from .models import Finding, SUPPORTED_HINTS, ToolDefinition


STATE_CHANGING_WORDS = (
    "create",
    "update",
    "write",
    "delete",
    "remove",
    "drop",
    "send",
    "execute",
    "modify",
    "insert",
    "upload",
    "destroy",
    "terminate",
    "revoke",
    "reset",
    "append",
    "increment",
    "purchase",
    "pay",
    "transfer",
)
DESTRUCTIVE_WORDS = (
    "delete",
    "remove",
    "drop",
    "destroy",
    "terminate",
    "revoke",
    "reset",
)
NON_IDEMPOTENT_WORDS = (
    "send",
    "create",
    "append",
    "increment",
    "purchase",
    "pay",
    "transfer",
)
OPEN_WORLD_WORDS = (
    "web",
    "http",
    "fetch",
    "search",
    "email",
    "slack",
    "github",
    "api",
    "request",
    "download",
)

_ALPHANUMERIC = re.compile(r"[A-Za-z0-9]+")
_ACRONYM_BOUNDARY = re.compile(r"([A-Z]+)([A-Z][a-z])")
_CAMEL_BOUNDARY = re.compile(r"([a-z0-9])([A-Z])")


def _tokens(text: str) -> set[str]:
    """Return whole and camel-split ASCII tokens for deterministic matching."""

    whole_tokens = {match.casefold() for match in _ALPHANUMERIC.findall(text)}
    split_text = _ACRONYM_BOUNDARY.sub(r"\1 \2", text)
    split_text = _CAMEL_BOUNDARY.sub(r"\1 \2", split_text)
    split_tokens = {match.casefold() for match in _ALPHANUMERIC.findall(split_text)}
    return whole_tokens | split_tokens


def _tool_tokens(tool: ToolDefinition) -> set[str]:
    return _tokens(f"{tool.name} {tool.description}")


def _first_match(tokens: set[str], words: Iterable[str]) -> str | None:
    return next((word for word in words if word in tokens), None)


def _check_readonly(tool: ToolDefinition, tokens: set[str]) -> Finding | None:
    if tool.annotations.get("readOnlyHint") is not True:
        return None
    evidence = _first_match(tokens, STATE_CHANGING_WORDS)
    if evidence is None:
        return None
    return Finding(
        tool=tool.name,
        rule_id="MCP001",
        severity="HIGH",
        message="Tool is marked read-only but appears to modify state.",
        evidence=evidence,
    )


def _check_destructive(tool: ToolDefinition, tokens: set[str]) -> Finding | None:
    if tool.annotations.get("destructiveHint") is not False:
        return None
    evidence = _first_match(tokens, DESTRUCTIVE_WORDS)
    if evidence is None:
        return None
    return Finding(
        tool=tool.name,
        rule_id="MCP002",
        severity="HIGH",
        message="Tool is marked non-destructive but appears destructive.",
        evidence=evidence,
    )


def _check_idempotent(tool: ToolDefinition, tokens: set[str]) -> Finding | None:
    if tool.annotations.get("idempotentHint") is not True:
        return None
    evidence = _first_match(tokens, NON_IDEMPOTENT_WORDS)
    if evidence is None:
        return None
    return Finding(
        tool=tool.name,
        rule_id="MCP003",
        severity="WARN",
        message="Tool is marked idempotent but may not be idempotent.",
        evidence=evidence,
    )


def _check_open_world(tool: ToolDefinition, tokens: set[str]) -> Finding | None:
    if tool.annotations.get("openWorldHint") is not False:
        return None
    evidence = _first_match(tokens, OPEN_WORLD_WORDS)
    if evidence is None:
        return None
    return Finding(
        tool=tool.name,
        rule_id="MCP004",
        severity="WARN",
        message="Tool is marked closed-world but appears to interact with an external system.",
        evidence=evidence,
    )


def lint_tool(tool: ToolDefinition) -> list[Finding]:
    """Run all rules against one tool in stable rule order."""

    tokens = _tool_tokens(tool)
    findings = [
        finding
        for check in (
            _check_readonly,
            _check_destructive,
            _check_idempotent,
            _check_open_world,
        )
        if (finding := check(tool, tokens)) is not None
    ]

    for hint in SUPPORTED_HINTS:
        if hint not in tool.annotations:
            findings.append(
                Finding(
                    tool=tool.name,
                    rule_id="MCP005",
                    severity="INFO",
                    message=f"Annotation '{hint}' is missing.",
                    evidence=hint,
                )
            )

    return findings


def lint_tools(tools: Iterable[ToolDefinition]) -> list[Finding]:
    """Run all rules against tools while preserving their input order."""

    return [finding for tool in tools for finding in lint_tool(tool)]
