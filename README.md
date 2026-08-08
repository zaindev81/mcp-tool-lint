# mcp-annotation-audit

`mcp-annotation-audit` is a small proof-of-concept developer tool for inspecting
coverage of the four boolean behavioral annotations on
[Model Context Protocol (MCP)](https://modelcontextprotocol.io/) Tools. It shows
which values are explicit, which come from MCP defaults, which fields are
applicable, and which omitted applicable fields may benefit from human review.

It does not infer Tool behavior or decide whether an annotation is correct.
An omitted annotation is not reported as an error or vulnerability.

## Why this project pivoted

This repository began as `mcp-tool-lint`, a keyword-based static linter. Its
first research experiment analyzed 267 Tools and produced 16 semantic review
candidates: 0 true positives, 0 likely true positives, 14 false positives, and
2 inconclusive results. That is strong negative evidence for the heuristic and
it has been removed rather than tuned.

A separate pre-registered source audit examined 40 omitted applicable fields:
26 defaults were correct, 11 were conservative but materially imprecise, none
were wrong, and 3 were inconclusive. That result supports investigating a
coverage and annotation-quality aid, not a vulnerability detector.

The original reports and data remain unchanged under [`research/pilot`](research/pilot)
and [`research/omitted_annotations_pilot`](research/omitted_annotations_pilot).

## Pivot boundary

- **Retained:** JSON input, strict validation of the supported booleans,
  explicit/effective value separation, MCP defaults, applicability rules, and
  dependency-free operation.
- **Removed:** keyword matching, semantic mismatch rules, severities, evidence
  excerpts, and finding-based exit status.
- **Historical only:** the `mcp-tool-lint` command and `MCP001`–`MCP005` finding
  schema remain reproducible from the pinned research commit but are not
  supported aliases in this PoC.
- **Renamed:** the product, distribution, command, and Python namespace now use
  `mcp-annotation-audit`; omitted applicable fields are called manual review
  fields rather than findings.

## Installation

Python 3.10 or newer is required. From a clone of this repository:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

## Usage

Audit a JSON array of MCP-compatible Tool definitions:

```bash
mcp-annotation-audit examples/tools.json
```

Request a versioned, machine-readable report:

```bash
mcp-annotation-audit examples/tools.json --json
```

The command exits with status `0` after any valid audit, regardless of coverage,
and `2` for invalid input or command usage.

The human report includes aggregate and per-annotation coverage followed by
per-Tool details. A defaulted applicable field is labeled as a manual review
field; this means only that source inspection may determine whether an explicit
value would improve precision.

## Defaults and applicability

The PoC is pinned to the
[MCP `2025-11-25` ToolAnnotations schema](https://modelcontextprotocol.io/specification/2025-11-25/schema#toolannotations):

| Annotation | Default when omitted | Applicability |
|---|---:|---|
| `readOnlyHint` | `false` | All Tools |
| `destructiveHint` | `true` | Meaningful when effective `readOnlyHint` is `false` |
| `idempotentHint` | `false` | Meaningful when effective `readOnlyHint` is `false` |
| `openWorldHint` | `true` | All Tools |

Coverage is `explicit applicable fields / applicable fields`. An explicit
`destructiveHint` or `idempotentHint` remains visible when a Tool is effectively
read-only, but it is excluded from the coverage numerator and denominator.

The JSON report records:

- the report schema and MCP schema versions;
- aggregate Tool and field counts;
- aggregate coverage for each annotation;
- every effective value, its `explicit` or `mcp_default` source, and its
  applicability; and
- per-Tool fields suggested for manual review solely because they are omitted
  and applicable.

## Input scope

The input must be a non-empty top-level JSON array. Each item needs a non-blank
string `name`; `annotations`, when present, must be an object. Explicit values
for the four supported hints must be JSON booleans. Other Tool fields and
annotation keys are ignored because this is not a full MCP schema validator.

## Non-goals

- Keyword or LLM-based semantic inference
- Automatic annotation values, recommendations, ranking, or auto-fix
- Correctness, risk, severity, or vulnerability classification
- Source-code analysis or MCP runtime interception
- Live server discovery or JSON-RPC envelope support
- A web UI, database, cloud service, GitHub Action, or plugin system
- Coverage of `title`, proposed annotations, or fields outside the four boolean
  behavioral hints

## Tests

Run the standard-library test suite without installing extra dependencies:

```bash
python3 -m unittest discover -s tests
```

## Current evidence gap

The source audit shows that some omitted defaults are materially imprecise. It
does not yet show that developers understand this report, find the review list
actionable, or improve annotations because of it. It also does not estimate
ecosystem-wide prevalence.

## License

MIT
