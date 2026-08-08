"""Load and minimally validate MCP Tool definitions from JSON."""

from __future__ import annotations

import json
from pathlib import Path

from .models import SUPPORTED_HINTS, ToolDefinition


class ToolInputError(ValueError):
    """Raised when an input file is unreadable or has an invalid shape."""


def parse_tools_data(data: object) -> list[ToolDefinition]:
    """Validate decoded JSON and return the fields used by the linter."""

    if not isinstance(data, list):
        raise ToolInputError("input must be a JSON array of tool definitions")
    if not data:
        raise ToolInputError("input must contain at least one tool definition")

    return [_parse_tool(item, index) for index, item in enumerate(data)]


def _parse_tool(item: object, index: int) -> ToolDefinition:
    location = f"tool at index {index}"
    if not isinstance(item, dict):
        raise ToolInputError(f"{location} must be a JSON object")

    name = item.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ToolInputError(f"{location} must have a non-blank string name")

    description = item.get("description", "")
    if not isinstance(description, str):
        raise ToolInputError(f"{location} description must be a string")

    raw_annotations = item.get("annotations", {})
    if not isinstance(raw_annotations, dict):
        raise ToolInputError(f"{location} annotations must be a JSON object")

    annotations: dict[str, bool] = {}
    for hint in SUPPORTED_HINTS:
        if hint not in raw_annotations:
            continue
        value = raw_annotations[hint]
        if type(value) is not bool:
            raise ToolInputError(f"{location} annotation {hint} must be a boolean")
        annotations[hint] = value

    return ToolDefinition(
        name=name,
        description=description,
        annotations=annotations,
    )


def load_tools(path: str | Path) -> list[ToolDefinition]:
    """Read a UTF-8 JSON file and parse its tool definitions."""

    input_path = Path(path)
    try:
        contents = input_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ToolInputError(
            f"invalid UTF-8 in {input_path} at byte {exc.start}"
        ) from exc
    except OSError as exc:
        raise ToolInputError(f"cannot read {input_path}: {exc.strerror or exc}") from exc

    try:
        data = json.loads(contents)
    except json.JSONDecodeError as exc:
        raise ToolInputError(
            f"invalid JSON in {input_path} at line {exc.lineno}, column {exc.colno}"
        ) from exc

    return parse_tools_data(data)
