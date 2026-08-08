from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from mcp_tool_lint.models import ANNOTATION_DEFAULTS
from mcp_tool_lint.parser import load_tools, parse_tools_data


class ParseToolsDataTests(unittest.TestCase):
    def test_parses_minimal_tool(self) -> None:
        tools = parse_tools_data([{"name": "get_user"}])

        self.assertEqual(1, len(tools))
        self.assertEqual("get_user", tools[0].name)
        self.assertEqual("", tools[0].description)
        self.assertEqual({}, tools[0].annotations)
        self.assertEqual(ANNOTATION_DEFAULTS, tools[0].effective_annotations)

    def test_parses_full_tool_and_ignores_unneeded_mcp_fields(self) -> None:
        tools = parse_tools_data(
            [
                {
                    "name": "delete_file",
                    "title": "Delete file",
                    "description": "Delete a local file",
                    "inputSchema": {"type": "object"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": True,
                        "idempotentHint": True,
                        "openWorldHint": False,
                        "futureHint": "ignored",
                    },
                    "futureToolField": {"allowed": True},
                }
            ]
        )

        self.assertEqual(1, len(tools))
        tool = tools[0]
        self.assertEqual("delete_file", tool.name)
        self.assertEqual("Delete a local file", tool.description)
        for annotation, expected in {
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        }.items():
            self.assertEqual(expected, tool.annotations[annotation])

    def test_keeps_explicit_annotations_separate_from_effective_defaults(self) -> None:
        tool = parse_tools_data(
            [{"name": "get_user", "annotations": {"readOnlyHint": True}}]
        )[0]

        self.assertEqual({"readOnlyHint": True}, tool.annotations)
        self.assertEqual(
            {
                "readOnlyHint": True,
                "destructiveHint": True,
                "idempotentHint": False,
                "openWorldHint": True,
            },
            tool.effective_annotations,
        )

    def test_parses_multiple_tools_in_input_order(self) -> None:
        tools = parse_tools_data(
            [
                {"name": "first"},
                {"name": "second", "description": "Second tool"},
            ]
        )

        self.assertEqual(["first", "second"], [tool.name for tool in tools])

    def test_rejects_empty_or_non_array_root(self) -> None:
        for data in ([], {}, "not an array", None, 42):
            with self.subTest(data=data), self.assertRaises(ValueError):
                parse_tools_data(data)

    def test_rejects_non_object_items(self) -> None:
        for item in (None, "tool", 1, [], True):
            with self.subTest(item=item), self.assertRaises(ValueError):
                parse_tools_data([item])

    def test_rejects_missing_blank_or_non_string_names(self) -> None:
        invalid_tools = (
            {},
            {"name": ""},
            {"name": "   "},
            {"name": None},
            {"name": 123},
        )

        for tool in invalid_tools:
            with self.subTest(tool=tool), self.assertRaises(ValueError):
                parse_tools_data([tool])

    def test_rejects_non_string_description(self) -> None:
        for description in (None, 1, {}, []):
            with self.subTest(description=description), self.assertRaises(ValueError):
                parse_tools_data([{"name": "get_user", "description": description}])

    def test_rejects_non_object_annotations(self) -> None:
        for annotations in (None, "readonly", [], True):
            with self.subTest(annotations=annotations), self.assertRaises(ValueError):
                parse_tools_data([{"name": "get_user", "annotations": annotations}])

    def test_rejects_non_boolean_supported_annotations(self) -> None:
        annotation_names = (
            "readOnlyHint",
            "destructiveHint",
            "idempotentHint",
            "openWorldHint",
        )
        invalid_values = (None, 0, 1, "true", [], {})

        for annotation in annotation_names:
            for value in invalid_values:
                with (
                    self.subTest(annotation=annotation, value=value),
                    self.assertRaises(ValueError),
                ):
                    parse_tools_data(
                        [{"name": "get_user", "annotations": {annotation: value}}]
                    )


class LoadToolsTests(unittest.TestCase):
    def write_temp_file(self, contents: str) -> Path:
        temporary_file = tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".json",
            delete=False,
        )
        with temporary_file:
            temporary_file.write(contents)
        self.addCleanup(Path(temporary_file.name).unlink, missing_ok=True)
        return Path(temporary_file.name)

    def test_loads_json_file(self) -> None:
        path = self.write_temp_file(
            json.dumps([{"name": "get_user", "description": "Get a user"}])
        )

        tools = load_tools(path)

        self.assertEqual(["get_user"], [tool.name for tool in tools])

    def test_rejects_malformed_json(self) -> None:
        path = self.write_temp_file('[{"name": "broken"}')

        with self.assertRaises(ValueError):
            load_tools(path)

    def test_rejects_invalid_utf8(self) -> None:
        temporary_file = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        with temporary_file:
            temporary_file.write(b'[{"name": "\xff"}]')
        path = Path(temporary_file.name)
        self.addCleanup(path.unlink, missing_ok=True)

        with self.assertRaises(ValueError):
            load_tools(path)

    def test_missing_file_is_an_error(self) -> None:
        path = Path(tempfile.gettempdir()) / "mcp-tool-lint-file-does-not-exist.json"

        with self.assertRaises((OSError, ValueError)):
            load_tools(path)


if __name__ == "__main__":
    unittest.main()
