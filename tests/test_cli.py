from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"


SAFE_ANNOTATIONS = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
}


class CliTests(unittest.TestCase):
    def run_cli(
        self,
        data=None,
        *,
        raw: str | None = None,
        raw_bytes: bytes | None = None,
        extra_arguments: tuple[str, ...] = (),
        environment_overrides: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "tools.json"
            if raw_bytes is not None:
                input_path.write_bytes(raw_bytes)
            else:
                contents = raw if raw is not None else json.dumps(data)
                input_path.write_text(contents, encoding="utf-8")

            environment = os.environ.copy()
            existing_pythonpath = environment.get("PYTHONPATH")
            environment["PYTHONPATH"] = os.pathsep.join(
                part
                for part in (str(SRC_ROOT), existing_pythonpath)
                if part
            )
            if environment_overrides:
                environment.update(environment_overrides)

            return subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "mcp_tool_lint.cli",
                    str(input_path),
                    *extra_arguments,
                ],
                cwd=PROJECT_ROOT,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )

    def test_human_output_groups_review_candidates_and_clean_tools(self) -> None:
        result = self.run_cli(
            [
                {
                    "name": "delete_file",
                    "description": "Delete a local file",
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": False,
                        "openWorldHint": False,
                    },
                },
                {
                    "name": "send_email",
                    "description": "Send an email",
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": True,
                        "idempotentHint": True,
                        "openWorldHint": True,
                    },
                },
                {
                    "name": "get_user",
                    "description": "Get a user from local memory",
                    "annotations": SAFE_ANNOTATIONS,
                },
            ]
        )

        self.assertEqual(0, result.returncode)
        self.assertEqual("", result.stderr)
        self.assertIn("△ delete_file", result.stdout)
        self.assertNotIn("HIGH", result.stdout)
        self.assertIn("MCP001", result.stdout)
        self.assertNotIn("MCP002", result.stdout)
        self.assertIn("△ send_email", result.stdout)
        self.assertIn("WARN", result.stdout)
        self.assertIn("MCP003", result.stdout)
        self.assertIn("Review recommended", result.stdout)
        self.assertIn("✓ get_user", result.stdout)
        self.assertIn("OK", result.stdout)

    def test_human_output_uses_ascii_markers_when_stdout_is_ascii(self) -> None:
        result = self.run_cli(
            [
                {
                    "name": "delete_file",
                    "description": "Delete a local file",
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": True,
                        "idempotentHint": False,
                        "openWorldHint": True,
                    },
                },
                {
                    "name": "send_email",
                    "description": "Send an email",
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": True,
                        "idempotentHint": True,
                        "openWorldHint": True,
                    },
                },
                {"name": "lookup_user"},
                {
                    "name": "get_user",
                    "description": "Get a user from local memory",
                    "annotations": SAFE_ANNOTATIONS,
                },
            ],
            environment_overrides={"PYTHONIOENCODING": "ascii"},
        )

        self.assertEqual(0, result.returncode)
        self.assertEqual("", result.stderr)
        self.assertIn("! delete_file", result.stdout)
        self.assertIn("! send_email", result.stdout)
        self.assertIn("i lookup_user", result.stdout)
        self.assertIn("+ get_user", result.stdout)
        for marker in ("✗", "△", "ⓘ", "✓"):
            self.assertNotIn(marker, result.stdout)
        self.assertFalse(result.stdout.startswith("x "))
        self.assertNotIn("\nx ", result.stdout)

    def test_non_ascii_evidence_is_escaped_for_ascii_stdout(self) -> None:
        data = [
            {
                "name": "delete_resume",
                "description": "Delete résumé",
                "annotations": {
                    "readOnlyHint": True,
                    "destructiveHint": True,
                    "idempotentHint": False,
                    "openWorldHint": True,
                },
            }
        ]

        for extra_arguments in ((), ("--json",)):
            with self.subTest(arguments=extra_arguments):
                result = self.run_cli(
                    data,
                    extra_arguments=extra_arguments,
                    environment_overrides={"PYTHONIOENCODING": "ascii"},
                )

                self.assertEqual(0, result.returncode)
                self.assertEqual("", result.stderr)
                result.stdout.encode("ascii")
                output = (
                    json.loads(result.stdout)[0]["evidence"]
                    if extra_arguments
                    else result.stdout
                )
                self.assertIn(r"r\u00e9sum\u00e9", output)

    def test_json_output_has_required_shape_and_stable_order(self) -> None:
        result = self.run_cli(
            [
                {
                    "name": "delete_send_email",
                    "description": "Delete a record and send email",
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True,
                        "openWorldHint": False,
                    },
                }
            ],
            extra_arguments=("--json",),
        )

        self.assertEqual(0, result.returncode)
        self.assertEqual("", result.stderr)
        findings = json.loads(result.stdout)
        self.assertEqual(
            ["MCP001", "MCP004"],
            [finding["rule_id"] for finding in findings],
        )
        for finding in findings:
            self.assertEqual(
                {"tool", "rule_id", "severity", "message", "evidence"},
                set(finding),
            )
            self.assertEqual("delete_send_email", finding["tool"])
            self.assertTrue(finding["message"])
            self.assertTrue(finding["evidence"])

    def test_clean_result_exits_zero(self) -> None:
        result = self.run_cli(
            [
                {
                    "name": "get_user",
                    "description": "Get a user from local memory",
                    "annotations": SAFE_ANNOTATIONS,
                }
            ]
        )

        self.assertEqual(0, result.returncode)
        self.assertEqual("", result.stderr)
        self.assertIn("✓ get_user", result.stdout)

    def test_warn_only_result_exits_zero(self) -> None:
        result = self.run_cli(
            [
                {
                    "name": "send_email",
                    "description": "Send an email",
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": True,
                        "idempotentHint": True,
                        "openWorldHint": True,
                    },
                }
            ]
        )

        self.assertEqual(0, result.returncode)
        self.assertEqual("", result.stderr)
        self.assertIn("△ send_email", result.stdout)
        self.assertIn("MCP003", result.stdout)

    def test_info_only_result_exits_zero(self) -> None:
        result = self.run_cli(
            [{"name": "get_user", "description": "Get a user"}]
        )

        self.assertEqual(0, result.returncode)
        self.assertEqual("", result.stderr)
        self.assertIn("ⓘ get_user", result.stdout)
        self.assertEqual(4, result.stdout.count("MCP005"))

    def test_invalid_json_exits_two_and_writes_diagnostic_to_stderr(self) -> None:
        result = self.run_cli(raw='[{"name": "broken"}')

        self.assertEqual(2, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertTrue(result.stderr.strip())

    def test_invalid_utf8_exits_two_and_writes_diagnostic_to_stderr(self) -> None:
        result = self.run_cli(raw_bytes=b'[{"name": "\xff"}]')

        self.assertEqual(2, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertTrue(result.stderr.strip())

    def test_invalid_input_shape_exits_two(self) -> None:
        result = self.run_cli({"name": "not-an-array"})

        self.assertEqual(2, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertTrue(result.stderr.strip())

    def test_missing_file_exits_two(self) -> None:
        environment = os.environ.copy()
        existing_pythonpath = environment.get("PYTHONPATH")
        environment["PYTHONPATH"] = os.pathsep.join(
            part for part in (str(SRC_ROOT), existing_pythonpath) if part
        )
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "mcp_tool_lint.cli",
                "/definitely/not/a/real/mcp-tool-lint-input.json",
            ],
            cwd=PROJECT_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(2, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertTrue(result.stderr.strip())

    def test_missing_required_path_is_a_usage_error(self) -> None:
        environment = os.environ.copy()
        existing_pythonpath = environment.get("PYTHONPATH")
        environment["PYTHONPATH"] = os.pathsep.join(
            part for part in (str(SRC_ROOT), existing_pythonpath) if part
        )
        result = subprocess.run(
            [sys.executable, "-m", "mcp_tool_lint.cli"],
            cwd=PROJECT_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(2, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertTrue(result.stderr.strip())


if __name__ == "__main__":
    unittest.main()
