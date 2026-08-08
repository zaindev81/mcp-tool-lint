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


class CliTests(unittest.TestCase):
    def run_cli(
        self,
        data=None,
        *,
        raw: str | None = None,
        raw_bytes: bytes | None = None,
        extra_arguments: tuple[str, ...] = (),
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
                part for part in (str(SRC_ROOT), existing_pythonpath) if part
            )
            return subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "mcp_annotation_audit.cli",
                    str(input_path),
                    *extra_arguments,
                ],
                cwd=PROJECT_ROOT,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )

    def test_human_output_reports_coverage_defaults_applicability_and_review(self) -> None:
        result = self.run_cli(
            [
                {
                    "name": "read_local",
                    "annotations": {
                        "readOnlyHint": True,
                        "openWorldHint": False,
                    },
                },
                {
                    "name": "write_local",
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                    },
                },
                {"name": "unannotated"},
            ]
        )

        self.assertEqual(0, result.returncode)
        self.assertEqual("", result.stderr)
        self.assertIn("Applicable annotation coverage: 4/10 (40.0%)", result.stdout)
        self.assertIn("Tools with manual review fields: 2", result.stdout)
        self.assertIn("not detected errors or vulnerabilities", result.stdout)
        self.assertIn("readOnlyHint: true (explicit; applicable)", result.stdout)
        self.assertIn(
            "destructiveHint: true (MCP default; not applicable while effective readOnlyHint=true)",
            result.stdout,
        )
        self.assertIn(
            "idempotentHint: false (MCP default; applicable; manual review field)",
            result.stdout,
        )
        self.assertIn(
            "Manual review fields: idempotentHint, openWorldHint", result.stdout
        )
        for old_term in ("MCP001", "MCP002", "MCP003", "MCP004", "WARN", "HIGH"):
            self.assertNotIn(old_term, result.stdout)

    def test_json_output_has_stable_research_shape(self) -> None:
        result = self.run_cli(
            [
                {
                    "name": "read_local",
                    "annotations": {"readOnlyHint": True},
                }
            ],
            extra_arguments=("--json",),
        )

        self.assertEqual(0, result.returncode)
        self.assertEqual("", result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(1, report["report_schema_version"])
        self.assertEqual("2025-11-25", report["mcp_schema_version"])
        self.assertEqual(2, report["summary"]["applicable_fields"])
        self.assertEqual(1, report["summary"]["explicit_applicable_fields"])
        self.assertEqual(50.0, report["summary"]["coverage_percent"])
        tool = report["tools"][0]
        self.assertEqual(["openWorldHint"], tool["manual_review"]["fields"])
        self.assertEqual(
            {
                "value": True,
                "source": "mcp_default",
                "explicit": False,
                "applicable": False,
                "manual_review": False,
            },
            tool["annotations"]["destructiveHint"],
        )

    def test_omitted_annotations_do_not_fail_the_audit(self) -> None:
        result = self.run_cli([{"name": "delete_send_remote"}])

        self.assertEqual(0, result.returncode)
        self.assertEqual("", result.stderr)
        self.assertIn("Applicable annotation coverage: 0/4 (0.0%)", result.stdout)
        self.assertNotIn("Potential annotation mismatch", result.stdout)

    def test_invalid_inputs_exit_two_and_write_only_to_stderr(self) -> None:
        cases = (
            {"raw": '[{"name": "broken"}'},
            {"raw_bytes": b'[{"name": "\xff"}]'},
            {"data": {"name": "not-an-array"}},
            {"data": [{"name": "bad", "annotations": {"readOnlyHint": 1}}]},
        )
        for case in cases:
            with self.subTest(case=case):
                result = self.run_cli(**case)
                self.assertEqual(2, result.returncode)
                self.assertEqual("", result.stdout)
                self.assertIn("mcp-annotation-audit: error:", result.stderr)

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
                "mcp_annotation_audit.cli",
                "/definitely/not/a/real/audit-input.json",
            ],
            cwd=PROJECT_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(2, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertIn("mcp-annotation-audit: error:", result.stderr)

    def test_missing_path_is_a_usage_error_with_new_command_name(self) -> None:
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(SRC_ROOT)
        result = subprocess.run(
            [sys.executable, "-m", "mcp_annotation_audit.cli"],
            cwd=PROJECT_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(2, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertIn("usage: mcp-annotation-audit", result.stderr)


if __name__ == "__main__":
    unittest.main()
