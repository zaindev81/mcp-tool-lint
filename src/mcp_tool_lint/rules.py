"""Deterministic heuristic rules for MCP Tool annotations."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable

from .models import ANNOTATION_DEFAULTS, Finding, ToolDefinition


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
    "archive",
    "overwrite",
    "truncate",
    "toggle",
)
DESTRUCTIVE_WORDS = (
    "delete",
    "remove",
    "drop",
    "destroy",
    "terminate",
    "revoke",
    "reset",
    "archive",
    "overwrite",
    "truncate",
)
NON_IDEMPOTENT_WORDS = (
    "send",
    "create",
    "append",
    "increment",
    "purchase",
    "pay",
    "transfer",
    "toggle",
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
    "remote",
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


def _is_word_form(token: str, word: str) -> bool:
    """Match a few common inflections without introducing a stemmer."""

    if token in (word, f"{word}s", f"{word}es"):
        return True
    if word.endswith("e"):
        return token in (f"{word}d", f"{word[:-1]}ing")
    if word.endswith("y") and len(word) > 1:
        return token in (f"{word[:-1]}ies", f"{word[:-1]}ied", f"{word}ing")
    return token in (f"{word}ed", f"{word}ing")


def _first_match(tokens: set[str], words: Iterable[str]) -> str | None:
    return next(
        (
            word
            for word in words
            if any(_is_word_form(token, word) for token in tokens)
        ),
        None,
    )


def _contains_word(text: str, word: str) -> bool:
    return any(_is_word_form(token, word) for token in _tokens(text))


def _excerpt(text: str, word: str, limit: int = 120) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized

    match_start = next(
        (
            match.start()
            for match in _ALPHANUMERIC.finditer(normalized)
            if _contains_word(match.group(), word)
        ),
        0,
    )
    start = max(0, match_start - limit // 3)
    end = min(len(normalized), start + limit)
    start = max(0, end - limit)
    excerpt = normalized[start:end]
    if start:
        excerpt = f"...{excerpt}"
    if end < len(normalized):
        excerpt = f"{excerpt}..."
    return excerpt


def _match_evidence(tool: ToolDefinition, word: str) -> str:
    # Descriptions usually provide more review context than names.
    for field_name, text in (("description", tool.description), ("name", tool.name)):
        if _contains_word(text, word):
            quoted_excerpt = json.dumps(_excerpt(text, word), ensure_ascii=True)
            return f"{field_name} contains {quoted_excerpt}"
    raise AssertionError(f"matched word {word!r} has no source text")


def _check_readonly(tool: ToolDefinition, tokens: set[str]) -> Finding | None:
    if tool.effective_annotations["readOnlyHint"] is not True:
        return None
    matched_word = _first_match(tokens, STATE_CHANGING_WORDS)
    if matched_word is None:
        return None
    return Finding(
        tool=tool.name,
        rule_id="MCP001",
        severity="WARN",
        message=(
            "Potential annotation mismatch: tool text may conflict with effective "
            "readOnlyHint=true. Review recommended."
        ),
        evidence=_match_evidence(tool, matched_word),
    )


def _check_destructive(tool: ToolDefinition, tokens: set[str]) -> Finding | None:
    effective = tool.effective_annotations
    if effective["readOnlyHint"] or effective["destructiveHint"] is not False:
        return None
    matched_word = _first_match(tokens, DESTRUCTIVE_WORDS)
    if matched_word is None:
        return None
    return Finding(
        tool=tool.name,
        rule_id="MCP002",
        severity="WARN",
        message=(
            "Potential annotation mismatch: tool text may conflict with effective "
            "destructiveHint=false. Review recommended."
        ),
        evidence=_match_evidence(tool, matched_word),
    )


def _check_idempotent(tool: ToolDefinition, tokens: set[str]) -> Finding | None:
    effective = tool.effective_annotations
    if effective["readOnlyHint"] or effective["idempotentHint"] is not True:
        return None
    matched_word = _first_match(tokens, NON_IDEMPOTENT_WORDS)
    if matched_word is None:
        return None
    return Finding(
        tool=tool.name,
        rule_id="MCP003",
        severity="WARN",
        message=(
            "Potential annotation mismatch: tool text may conflict with effective "
            "idempotentHint=true. Review recommended."
        ),
        evidence=_match_evidence(tool, matched_word),
    )


def _check_open_world(tool: ToolDefinition, tokens: set[str]) -> Finding | None:
    if tool.effective_annotations["openWorldHint"] is not False:
        return None
    matched_word = _first_match(tokens, OPEN_WORLD_WORDS)
    if matched_word is None:
        return None
    return Finding(
        tool=tool.name,
        rule_id="MCP004",
        severity="WARN",
        message=(
            "Potential annotation mismatch: tool text may conflict with effective "
            "openWorldHint=false. Review recommended."
        ),
        evidence=_match_evidence(tool, matched_word),
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

    effective = tool.effective_annotations
    for hint, default in ANNOTATION_DEFAULTS.items():
        if hint not in tool.annotations:
            if effective["readOnlyHint"] and hint in (
                "destructiveHint",
                "idempotentHint",
            ):
                continue
            default_text = str(default).lower()
            findings.append(
                Finding(
                    tool=tool.name,
                    rule_id="MCP005",
                    severity="INFO",
                    message=(
                        f"Annotation coverage: '{hint}' was not explicitly specified; "
                        f"its effective MCP default is {default_text}."
                    ),
                    evidence=(
                        f'annotations omit "{hint}"; effective value is {default_text}'
                    ),
                )
            )

    return findings


def lint_tools(tools: Iterable[ToolDefinition]) -> list[Finding]:
    """Run all rules against tools while preserving their input order."""

    return [finding for tool in tools for finding in lint_tool(tool)]
