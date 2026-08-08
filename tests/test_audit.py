from __future__ import annotations

import json
import sys
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from mcp_annotation_audit.audit import audit_tools, report_to_dict
from mcp_annotation_audit.models import ToolDefinition


class AuditTests(unittest.TestCase):
    def test_omitted_annotations_use_defaults_and_all_apply_to_default_writer(self) -> None:
        report = audit_tools([ToolDefinition(name="lookup")])
        tool = report.tools[0]

        self.assertEqual(
            {
                "readOnlyHint": False,
                "destructiveHint": True,
                "idempotentHint": False,
                "openWorldHint": True,
            },
            {hint: status.value for hint, status in tool.annotations.items()},
        )
        self.assertTrue(
            all(
                status.source == "mcp_default"
                for status in tool.annotations.values()
            )
        )
        self.assertTrue(all(status.applicable for status in tool.annotations.values()))
        self.assertEqual(
            (
                "readOnlyHint",
                "destructiveHint",
                "idempotentHint",
                "openWorldHint",
            ),
            tool.manual_review_fields,
        )
        self.assertEqual(4, tool.coverage.applicable_fields)
        self.assertEqual(0, tool.coverage.explicit_applicable_fields)
        self.assertEqual(0.0, tool.coverage.coverage_percent)

    def test_read_only_tool_excludes_conditional_fields_from_coverage_and_review(self) -> None:
        report = audit_tools(
            [ToolDefinition(name="read", annotations={"readOnlyHint": True})]
        )
        tool = report.tools[0]

        self.assertFalse(tool.annotations["destructiveHint"].applicable)
        self.assertFalse(tool.annotations["idempotentHint"].applicable)
        self.assertFalse(tool.annotations["destructiveHint"].manual_review)
        self.assertFalse(tool.annotations["idempotentHint"].manual_review)
        self.assertEqual(("openWorldHint",), tool.manual_review_fields)
        self.assertEqual(2, tool.coverage.applicable_fields)
        self.assertEqual(1, tool.coverage.explicit_applicable_fields)
        self.assertEqual(50.0, tool.coverage.coverage_percent)

    def test_explicit_inapplicable_fields_remain_visible_but_do_not_count(self) -> None:
        report = audit_tools(
            [
                ToolDefinition(
                    name="read",
                    annotations={
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True,
                        "openWorldHint": False,
                    },
                )
            ]
        )
        tool = report.tools[0]

        self.assertTrue(tool.annotations["destructiveHint"].explicit)
        self.assertFalse(tool.annotations["destructiveHint"].applicable)
        self.assertTrue(tool.annotations["idempotentHint"].explicit)
        self.assertFalse(tool.annotations["idempotentHint"].applicable)
        self.assertEqual(2, tool.coverage.applicable_fields)
        self.assertEqual(2, tool.coverage.explicit_applicable_fields)
        self.assertEqual(100.0, tool.coverage.coverage_percent)
        self.assertEqual((), tool.manual_review_fields)
        self.assertIsNone(
            report.annotation_coverage["destructiveHint"].coverage_percent
        )
        self.assertIsNone(
            report.annotation_coverage["idempotentHint"].coverage_percent
        )

    def test_aggregate_and_per_annotation_coverage(self) -> None:
        report = audit_tools(
            [
                ToolDefinition(
                    name="read",
                    annotations={"readOnlyHint": True, "openWorldHint": False},
                ),
                ToolDefinition(
                    name="write",
                    annotations={
                        "readOnlyHint": False,
                        "destructiveHint": False,
                    },
                ),
                ToolDefinition(name="unannotated"),
            ]
        )

        summary = report.summary
        self.assertEqual(3, summary.tools)
        self.assertEqual(2, summary.tools_with_any_explicit_annotations)
        self.assertEqual(1, summary.tools_with_no_explicit_annotations)
        self.assertEqual(1, summary.tools_with_full_applicable_coverage)
        self.assertEqual(2, summary.tools_with_manual_review_fields)
        self.assertEqual(10, summary.coverage.applicable_fields)
        self.assertEqual(4, summary.coverage.explicit_applicable_fields)
        self.assertEqual(40.0, summary.coverage.coverage_percent)

        expected = {
            "readOnlyHint": (3, 2, 66.7),
            "destructiveHint": (2, 1, 50.0),
            "idempotentHint": (2, 0, 0.0),
            "openWorldHint": (3, 1, 33.3),
        }
        self.assertEqual(
            expected,
            {
                hint: (
                    coverage.applicable_fields,
                    coverage.explicit_applicable_fields,
                    coverage.coverage_percent,
                )
                for hint, coverage in report.annotation_coverage.items()
            },
        )

    def test_tool_words_do_not_change_annotation_audit(self) -> None:
        annotations = {
            "readOnlyHint": True,
            "openWorldHint": False,
        }
        report = audit_tools(
            [
                ToolDefinition(name="delete_send_remote", annotations=annotations),
                ToolDefinition(name="get_local_value", annotations=annotations),
            ]
        )

        first, second = report.tools
        self.assertEqual(first.annotations, second.annotations)
        self.assertEqual(first.coverage, second.coverage)
        self.assertEqual(first.manual_review_fields, second.manual_review_fields)

    def test_json_report_is_versioned_complete_and_has_no_linter_findings(self) -> None:
        data = report_to_dict(audit_tools([ToolDefinition(name="lookup")]))

        self.assertEqual(1, data["report_schema_version"])
        self.assertEqual("2025-11-25", data["mcp_schema_version"])
        self.assertEqual("omitted_applicable_annotations", data["review_basis"])
        self.assertEqual(
            [
                "readOnlyHint",
                "destructiveHint",
                "idempotentHint",
                "openWorldHint",
            ],
            list(data["annotation_coverage"]),
        )
        tool = data["tools"][0]
        self.assertEqual(
            {
                "value",
                "source",
                "explicit",
                "applicable",
                "manual_review",
            },
            set(tool["annotations"]["readOnlyHint"]),
        )
        serialized = json.dumps(data)
        for removed_field in ("rule_id", "severity", "evidence"):
            self.assertNotIn(removed_field, serialized)


if __name__ == "__main__":
    unittest.main()
