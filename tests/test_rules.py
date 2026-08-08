from __future__ import annotations

import sys
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from mcp_tool_lint.models import ToolDefinition
from mcp_tool_lint.rules import (
    DESTRUCTIVE_WORDS,
    NON_IDEMPOTENT_WORDS,
    STATE_CHANGING_WORDS,
    lint_tool,
    lint_tools,
)


ALL_ANNOTATIONS = {
    "readOnlyHint": False,
    "destructiveHint": True,
    "idempotentHint": False,
    "openWorldHint": True,
}


def make_tool(
    name: str = "get_user",
    description: str = "Get a user",
    **annotation_overrides: bool,
) -> ToolDefinition:
    annotations = {**ALL_ANNOTATIONS, **annotation_overrides}
    return ToolDefinition(
        name=name,
        description=description,
        annotations=annotations,
    )


def findings_for(rule_id: str, tool: ToolDefinition):
    return [finding for finding in lint_tool(tool) if finding.rule_id == rule_id]


class ReadOnlyRuleTests(unittest.TestCase):
    def test_all_state_changing_keywords_trigger_mcp001(self) -> None:
        keywords = (
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

        for keyword in keywords:
            with self.subTest(keyword=keyword):
                tool = make_tool(
                    name=f"{keyword}_item",
                    description="Operate on an item",
                    readOnlyHint=True,
                )
                findings = findings_for("MCP001", tool)
                self.assertEqual(1, len(findings))
                self.assertEqual("HIGH", findings[0].severity)
                self.assertEqual(keyword, findings[0].evidence)

    def test_read_only_rule_includes_other_mutation_vocabularies(self) -> None:
        self.assertLessEqual(set(DESTRUCTIVE_WORDS), set(STATE_CHANGING_WORDS))
        self.assertLessEqual(set(NON_IDEMPOTENT_WORDS), set(STATE_CHANGING_WORDS))

    def test_keyword_in_description_triggers_mcp001(self) -> None:
        tool = make_tool(
            name="manage_item",
            description="This tool will modify an item",
            readOnlyHint=True,
        )

        findings = findings_for("MCP001", tool)

        self.assertEqual(1, len(findings))
        self.assertEqual("modify", findings[0].evidence)

    def test_read_only_false_does_not_trigger_mcp001(self) -> None:
        tool = make_tool(name="delete_item", readOnlyHint=False)

        self.assertEqual([], findings_for("MCP001", tool))

    def test_benign_read_only_tool_does_not_trigger_mcp001(self) -> None:
        tool = make_tool(
            name="get_item",
            description="Return an item without changing it",
            readOnlyHint=True,
        )

        self.assertEqual([], findings_for("MCP001", tool))


class DestructiveRuleTests(unittest.TestCase):
    def test_all_destructive_keywords_trigger_mcp002(self) -> None:
        keywords = (
            "delete",
            "remove",
            "drop",
            "destroy",
            "terminate",
            "revoke",
            "reset",
        )

        for keyword in keywords:
            with self.subTest(keyword=keyword):
                tool = make_tool(
                    name=f"{keyword}_item",
                    description="Operate on an item",
                    destructiveHint=False,
                )
                findings = findings_for("MCP002", tool)
                self.assertEqual(1, len(findings))
                self.assertEqual("HIGH", findings[0].severity)
                self.assertEqual(keyword, findings[0].evidence)

    def test_keyword_in_description_triggers_mcp002(self) -> None:
        tool = make_tool(
            name="manage_token",
            description="Revoke an access token",
            destructiveHint=False,
        )

        findings = findings_for("MCP002", tool)

        self.assertEqual(1, len(findings))
        self.assertEqual("revoke", findings[0].evidence)

    def test_destructive_true_does_not_trigger_mcp002(self) -> None:
        tool = make_tool(name="delete_item", destructiveHint=True)

        self.assertEqual([], findings_for("MCP002", tool))

    def test_benign_non_destructive_tool_does_not_trigger_mcp002(self) -> None:
        tool = make_tool(
            name="list_items",
            description="List all available items",
            destructiveHint=False,
        )

        self.assertEqual([], findings_for("MCP002", tool))


class IdempotencyRuleTests(unittest.TestCase):
    def test_all_non_idempotent_keywords_trigger_mcp003(self) -> None:
        keywords = (
            "send",
            "create",
            "append",
            "increment",
            "purchase",
            "pay",
            "transfer",
        )

        for keyword in keywords:
            with self.subTest(keyword=keyword):
                tool = make_tool(
                    name=f"{keyword}_item",
                    description="Operate on an item",
                    idempotentHint=True,
                )
                findings = findings_for("MCP003", tool)
                self.assertEqual(1, len(findings))
                self.assertEqual("WARN", findings[0].severity)
                self.assertEqual(keyword, findings[0].evidence)

    def test_keyword_in_description_triggers_mcp003(self) -> None:
        tool = make_tool(
            name="notify_user",
            description="Send a notification to the user",
            idempotentHint=True,
        )

        findings = findings_for("MCP003", tool)

        self.assertEqual(1, len(findings))
        self.assertEqual("send", findings[0].evidence)

    def test_idempotent_false_does_not_trigger_mcp003(self) -> None:
        tool = make_tool(name="send_email", idempotentHint=False)

        self.assertEqual([], findings_for("MCP003", tool))

    def test_benign_idempotent_tool_does_not_trigger_mcp003(self) -> None:
        tool = make_tool(
            name="set_status",
            description="Set the status to a supplied value",
            idempotentHint=True,
        )

        self.assertEqual([], findings_for("MCP003", tool))


class OpenWorldRuleTests(unittest.TestCase):
    def test_all_external_system_keywords_trigger_mcp004(self) -> None:
        keywords = (
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

        for keyword in keywords:
            with self.subTest(keyword=keyword):
                tool = make_tool(
                    name=f"{keyword}_resource",
                    description="Read a resource",
                    openWorldHint=False,
                )
                findings = findings_for("MCP004", tool)
                self.assertEqual(1, len(findings))
                self.assertEqual("WARN", findings[0].severity)
                self.assertEqual(keyword, findings[0].evidence)

    def test_keyword_in_description_triggers_mcp004(self) -> None:
        tool = make_tool(
            name="find_issues",
            description="Search GitHub issues",
            openWorldHint=False,
        )

        findings = findings_for("MCP004", tool)

        self.assertEqual(1, len(findings))
        self.assertEqual("search", findings[0].evidence)

    def test_open_world_true_does_not_trigger_mcp004(self) -> None:
        tool = make_tool(name="search_web", openWorldHint=True)

        self.assertEqual([], findings_for("MCP004", tool))

    def test_benign_closed_world_tool_does_not_trigger_mcp004(self) -> None:
        tool = make_tool(
            name="read_local_config",
            description="Read local configuration",
            openWorldHint=False,
        )

        self.assertEqual([], findings_for("MCP004", tool))


class TokenizationTests(unittest.TestCase):
    def test_name_and_description_normalization(self) -> None:
        cases = (
            ("delete_user", "Operate on a user"),
            ("delete-user", "Operate on a user"),
            ("deleteUser", "Operate on a user"),
            ("DELETE.USER", "Operate on a user"),
            ("manage_user", "Please DELETE the user"),
        )

        for name, description in cases:
            with self.subTest(name=name, description=description):
                tool = make_tool(
                    name=name,
                    description=description,
                    readOnlyHint=True,
                )
                findings = findings_for("MCP001", tool)
                self.assertEqual(1, len(findings))
                self.assertEqual("delete", findings[0].evidence)

    def test_keywords_must_be_complete_tokens(self) -> None:
        tool = make_tool(
            name="capital_report",
            description="Summarize recreated records",
            readOnlyHint=True,
            openWorldHint=False,
        )

        findings = lint_tool(tool)

        self.assertNotIn("MCP001", {finding.rule_id for finding in findings})
        self.assertNotIn("MCP004", {finding.rule_id for finding in findings})

    def test_rule_emits_only_first_matching_keyword(self) -> None:
        tool = make_tool(
            name="delete_remove_item",
            description="Drop an item",
            destructiveHint=False,
        )

        findings = findings_for("MCP002", tool)

        self.assertEqual(1, len(findings))
        self.assertEqual("delete", findings[0].evidence)


class MissingAnnotationsRuleTests(unittest.TestCase):
    def test_each_missing_annotation_gets_an_info_finding(self) -> None:
        tool = ToolDefinition(
            name="get_user",
            description="Get a user",
            annotations={},
        )

        findings = findings_for("MCP005", tool)

        self.assertEqual(4, len(findings))
        self.assertTrue(all(finding.severity == "INFO" for finding in findings))
        self.assertEqual(
            {
                "readOnlyHint",
                "destructiveHint",
                "idempotentHint",
                "openWorldHint",
            },
            {finding.evidence for finding in findings},
        )

    def test_only_absent_annotations_are_reported(self) -> None:
        tool = ToolDefinition(
            name="get_user",
            description="Get a user",
            annotations={"readOnlyHint": True, "openWorldHint": False},
        )

        findings = findings_for("MCP005", tool)

        self.assertEqual(
            {"destructiveHint", "idempotentHint"},
            {finding.evidence for finding in findings},
        )

    def test_no_missing_findings_when_all_annotations_are_present(self) -> None:
        tool = make_tool(readOnlyHint=True, openWorldHint=False)

        self.assertEqual([], findings_for("MCP005", tool))


class RuleAggregationTests(unittest.TestCase):
    def test_findings_have_required_fields_and_stable_rule_order(self) -> None:
        tool = make_tool(
            name="delete_send_email",
            description="Delete a record, then send email",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )

        findings = lint_tool(tool)

        self.assertEqual(
            ["MCP001", "MCP002", "MCP003", "MCP004"],
            [finding.rule_id for finding in findings],
        )
        for finding in findings:
            self.assertEqual("delete_send_email", finding.tool)
            self.assertTrue(finding.severity)
            self.assertTrue(finding.message)
            self.assertTrue(finding.evidence)

    def test_lint_tools_preserves_tool_order(self) -> None:
        first = make_tool(name="delete_first", readOnlyHint=True)
        second = make_tool(name="send_second", idempotentHint=True)

        findings = lint_tools([first, second])

        tool_names = [finding.tool for finding in findings]
        first_second_index = tool_names.index("send_second")
        self.assertTrue(
            all(name == "delete_first" for name in tool_names[:first_second_index])
        )
        self.assertTrue(
            all(name == "send_second" for name in tool_names[first_second_index:])
        )

    def test_safe_fully_annotated_tool_has_no_findings(self) -> None:
        tool = make_tool(
            name="get_user",
            description="Get a user from local memory",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )

        self.assertEqual([], lint_tool(tool))


if __name__ == "__main__":
    unittest.main()
