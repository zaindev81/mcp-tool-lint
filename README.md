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
otherwise, and `2` for invalid input or command usage. The current keyword
rules produce `WARN` review candidates, not `HIGH` findings, so a keyword match
alone does not fail the command.
Status symbols fall back to `x`, `!`, `i`, and `+` when stdout cannot encode
the Unicode markers.

Example findings include:

```text
△ delete_file
  WARN [MCP001]: Potential annotation mismatch: tool text may conflict with effective readOnlyHint=true. Review recommended. (evidence: description contains "Delete a local file")

△ send_email
  WARN [MCP003]: Potential annotation mismatch: tool text may conflict with effective idempotentHint=true. Review recommended. (evidence: description contains "Send an email message")

✓ get_user
  OK
```

JSON output is an array of findings with stable rule IDs and evidence:

```json
[
  {
    "tool": "delete_file",
    "rule_id": "MCP001",
    "severity": "WARN",
    "message": "Potential annotation mismatch: tool text may conflict with effective readOnlyHint=true. Review recommended.",
    "evidence": "description contains \"Delete a local file\""
  }
]
```

The supported annotations are `readOnlyHint`, `destructiveHint`,
`idempotentHint`, and `openWorldHint`. Explicit values are preserved separately
from effective values. When omitted, the MCP defaults are:

- `readOnlyHint=false`
- `destructiveHint=true`
- `idempotentHint=false`
- `openWorldHint=true`

MCP005 reports applicable omissions as annotation coverage information and
includes the effective default; it does not describe them as vulnerabilities.
`destructiveHint` and `idempotentHint` are evaluated and reported for coverage
only when effective `readOnlyHint` is false.

## Tests

Run the standard-library test suite without installing additional test
dependencies:

```bash
python -m unittest discover -s tests
```

## Current limitations

- Rules use case-insensitive keyword matching with a few common inflections;
  they do not understand intent, negation, synonyms, or domain context.
- A matching word can be harmless in context, so findings may be false
  positives and require human review.
- Unrecognized wording, irregular inflections, and behavior omitted from the
  tool text can produce false negatives.
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
