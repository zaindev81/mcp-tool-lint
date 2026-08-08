from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from mcp_annotation_audit.parser import ToolInputError, load_tools, parse_tools_data


class ParseToolsTests(unittest.TestCase):
    def test_parses_explicit_supported_annotations_only(self) -> None:
        tools = parse_tools_data(
            [
                {
                    "name": "lookup",
                    "description": "Any description",
                    "annotations": {
                        "title": "Lookup",
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True,
                        "openWorldHint": False,
                        "futureHint": True,
                    },
                }
            ]
        )

        self.assertEqual("lookup", tools[0].name)
        self.assertEqual(
            {
                "readOnlyHint": True,
                "destructiveHint": False,
                "idempotentHint": True,
                "openWorldHint": False,
            },
            tools[0].annotations,
        )

    def test_description_is_not_read_or_validated(self) -> None:
        tools = parse_tools_data(
            [
                {"name": "first", "description": 123},
                {"name": "second", "description": "delete send web"},
            ]
        )

        self.assertEqual(["first", "second"], [tool.name for tool in tools])
        self.assertEqual([{}, {}], [tool.annotations for tool in tools])

    def test_rejects_non_array_and_empty_input(self) -> None:
        for data in ({"name": "lookup"}, [], None):
            with self.subTest(data=data), self.assertRaises(ToolInputError):
                parse_tools_data(data)

    def test_rejects_invalid_tool_and_name_shapes(self) -> None:
        for item in ("lookup", {}, {"name": ""}, {"name": "   "}, {"name": 1}):
            with self.subTest(item=item), self.assertRaises(ToolInputError):
                parse_tools_data([item])

    def test_rejects_non_object_annotations(self) -> None:
        for annotations in (None, [], "read-only"):
            with self.subTest(annotations=annotations), self.assertRaises(
                ToolInputError
            ):
                parse_tools_data([{"name": "lookup", "annotations": annotations}])

    def test_rejects_non_boolean_supported_values(self) -> None:
        for value in (None, 0, 1, "true", []):
            with self.subTest(value=value), self.assertRaises(ToolInputError):
                parse_tools_data(
                    [
                        {
                            "name": "lookup",
                            "annotations": {"readOnlyHint": value},
                        }
                    ]
                )


class LoadToolsTests(unittest.TestCase):
    def test_loads_utf8_json_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tools.json"
            path.write_text(
                json.dumps([{"name": "検索", "annotations": {}}]),
                encoding="utf-8",
            )

            tools = load_tools(path)

        self.assertEqual("検索", tools[0].name)

    def test_invalid_json_reports_location(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tools.json"
            path.write_text('[{"name": "broken"}', encoding="utf-8")

            with self.assertRaisesRegex(ToolInputError, r"line 1, column"):
                load_tools(path)

    def test_invalid_utf8_reports_byte(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tools.json"
            path.write_bytes(b'[{"name":"\xff"}]')

            with self.assertRaisesRegex(ToolInputError, r"byte"):
                load_tools(path)

    def test_missing_file_is_input_error(self) -> None:
        with self.assertRaisesRegex(ToolInputError, r"cannot read"):
            load_tools("/definitely/not/a/real/audit-input.json")


if __name__ == "__main__":
    unittest.main()
