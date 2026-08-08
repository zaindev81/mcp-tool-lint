# mcp-tool-lint

`mcp-tool-lint` is a small proof-of-concept static linter for annotations on
[Model Context Protocol (MCP)](https://modelcontextprotocol.io/) Tool
definitions. It reads tools from JSON and reports annotation values that look
inconsistent with a tool's name or description.

## Problem

MCP Tool annotations communicate properties such as whether a tool is
read-only, destructive, idempotent, or able to interact with the wider world.
An omitted or misleading annotation can cause a client or a user to make an
unsafe assumption about a tool.

## Hypothesis

MCP server developers may incorrectly configure or omit Tool annotations, and
a small deterministic linter can identify potentially dangerous or misleading
configurations before runtime.

This project is intentionally a narrow PoC. It does not run tools or use an
LLM; it only compares annotations with keywords in tool names and descriptions.

## Installation

Python 3.10 or newer is required. From a clone of this repository, install the
package in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

## Usage

Lint a JSON array of MCP-compatible Tool definitions:

```bash
mcp-tool-lint examples/tools.json
```

Request machine-readable findings:

```bash
mcp-tool-lint examples/tools.json --json
```

The command exits with status `1` when it finds any `HIGH` findings, `0`
otherwise, and `2` for invalid input or command usage.
Status symbols fall back to `x`, `!`, `i`, and `+` when stdout cannot encode
the Unicode markers.

Example findings include:

```text
✗ delete_file
  HIGH [MCP001]: Tool is marked read-only but appears to modify state. (evidence: delete)
  HIGH [MCP002]: Tool is marked non-destructive but appears destructive. (evidence: delete)

△ send_email
  WARN [MCP003]: Tool is marked idempotent but may not be idempotent. (evidence: send)

✓ get_user
  OK
```

JSON output is an array of findings with stable rule IDs and evidence:

```json
[
  {
    "tool": "delete_file",
    "rule_id": "MCP001",
    "severity": "HIGH",
    "message": "Tool is marked read-only but appears to modify state.",
    "evidence": "delete"
  }
]
```

The supported annotations are `readOnlyHint`, `destructiveHint`,
`idempotentHint`, and `openWorldHint`. Missing annotations are reported as
informational findings, not vulnerabilities.

## Tests

Run the standard-library test suite without installing additional test
dependencies:

```bash
python -m unittest discover -s tests
```

## Current limitations

- Rules use exact, case-insensitive keyword matching; they do not understand
  intent, negation, synonyms, or domain context.
- A matching word can be harmless in context, so findings may be false
  positives and require human review.
- Unrecognized wording and inflected terms can produce false negatives.
- The input must be a top-level JSON array; JSON-RPC `tools/list` envelopes,
  live MCP servers, and standard input are not supported.
- This is an annotation consistency check, not a security scanner or proof that
  a tool is safe.

## Research / Validation

The next step is to run the linter against real open-source MCP servers and
measure:

- number of tools analyzed
- missing annotations
- suspicious annotations
- confirmed annotation mistakes
- false-positive rate

Those results should determine whether the rules are useful enough to refine or
whether the hypothesis should be rejected before expanding the project.

## License

MIT
