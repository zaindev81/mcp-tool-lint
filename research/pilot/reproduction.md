# Pilot Reproduction Notes

The pilot is pinned to linter commit
`e6889c415d7abadec846fd949c9ce1cbf99c71d1`. Repository commits and extraction
notes are in [`repositories.csv`](repositories.csv); the recorded search
queries and selection order are in [`selection.md`](selection.md).

## Artifact flow

```text
pinned repository source
        |
        v
 tools/*.json  -- frozen linter -->  linter/*.json
        |                                |
        +---------- analyze.py ----------+
                         |
                         +--> tools.csv
                         +--> findings.csv
                         +--> repository_stats.csv
                         +--> metrics.json
```

`manual_classifications.csv` is the only hand-classified input to
`analyze.py`. The script asserts that it contains exactly one review for every
non-MCP005 linter finding, with neither missing nor extra rows.

## Tool collection

The stored `tools/*.json` files are the immutable extracted inputs used for
the reported run. Each tool's source provenance is retained there and in
`tools.csv`. Two small research collectors document the repeatable extraction
methods; they are not product features.

For an mcp-go source file containing literal or constant registrations:

```bash
go run research/pilot/extract_mcp_go_tools.go -- /path/to/server.go
```

For a credential-free local stdio server:

```bash
PILOT_SERVER_CWD=/path/to/pinned/repository \
  node research/pilot/extract_tools_stdio.mjs -- SERVER_COMMAND ARGUMENTS
```

The remaining stored inputs came from static registrations or checked-in
generated metadata, as described in the repository manifest. `prest/prest` and
`awslabs/mcp` deliberately have no partial tool JSON because the frozen
protocol requires a faithful population rather than a guessed subset.

## Linter run

From this repository at the pinned linter commit, each stored tool array was
run independently:

```bash
for input in research/pilot/tools/*.json; do
  output="research/pilot/linter/$(basename "$input")"
  PYTHONPATH=src python3 -m mcp_tool_lint.cli --json "$input" > "$output"
done
```

The command writes JSON even when the findings are only coverage information.
The frozen CLI returns zero for these runs because no `HIGH` finding was
emitted.

## Rebuild derived datasets

```bash
python3 research/pilot/analyze.py
```

Expected headline output:

```text
repositories_selected: 10
repositories_analyzed: 8
total_tools_analyzed: 267
semantic_review_candidates: 16
true_positives: 0
likely_true_positives: 0
false_positives: 14
inconclusive_findings: 2
hypothesis_decision: INCONCLUSIVE
```

## Project regression suite

The study did not alter product code or tests. Verify the frozen linter with:

```bash
python3 -m unittest discover -s tests
```

## Representative human-readable cases

These commands select one coverage-only case, one known heuristic false
positive, and one inconclusive semantic candidate from the stored data:

```bash
python3 - <<'PY' >/tmp/pilot-read-file.json
import json
tools = json.load(open("research/pilot/tools/mark3labs_mcp-filesystem-server.json"))
print(json.dumps([next(tool for tool in tools if tool["name"] == "read_file")]))
PY
PYTHONPATH=src python3 -m mcp_tool_lint.cli /tmp/pilot-read-file.json

python3 - <<'PY' >/tmp/pilot-search-files.json
import json
tools = json.load(open("research/pilot/tools/modelcontextprotocol_servers.json"))
print(json.dumps([next(tool for tool in tools if tool["name"] == "search_files")]))
PY
PYTHONPATH=src python3 -m mcp_tool_lint.cli /tmp/pilot-search-files.json

python3 - <<'PY' >/tmp/pilot-copilot-assignment.json
import json
tools = json.load(open("research/pilot/tools/github_github-mcp-server.json"))
print(json.dumps([next(tool for tool in tools if tool["name"] == "assign_copilot_to_issue")]))
PY
PYTHONPATH=src python3 -m mcp_tool_lint.cli /tmp/pilot-copilot-assignment.json
```

All three should exit zero. The first reports four MCP005 `INFO` items with
effective defaults. The second reports one MCP004 `WARN`; manual source review
classifies it as a false positive because the search is local. The third
reports one MCP003 `WARN` plus two MCP005 items; repeat-call behavior is
delegated to GitHub and remains inconclusive.
