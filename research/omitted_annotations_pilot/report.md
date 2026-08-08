# Omitted MCP Tool Annotations: 40-Field Blinded Source Audit

## Result

**Decision: SUPPORTED.**

In this deliberately small, stratified sample, 11 of 40 omitted applicable
annotation fields (27.5%) produced defaults that were safe but materially less
precise than the source-supported annotation. No sampled omission understated
risk (`WRONG`: 0). Three remote-API idempotency cases remained inconclusive.

Among the 37 conclusive cases, 11 (29.7%) supported the hypothesis. Supportive
cases spanned five repositories and all four annotation types, satisfying every
pre-registered `SUPPORTED` threshold. These are descriptive sample results, not
an estimate of prevalence across MCP tools or repositories.

## Protocol integrity and blinding

The [protocol](protocol.md) was frozen at
`2026-08-08T17:44:28+09:00`, before sampling or source inspection.

- Protocol SHA-256:
  `3925bd32a09d1fc1aca3bf1f0706fb4be47ae7234cc90900ae8138d37deffbbb`
- Sample SHA-256:
  `5789400ef5bf1ee47a75a42e818375cc20f83c418c8d7702da67b143c09e3399`
- Locked classifications SHA-256:
  `a0ecf1db52df60b89c30789da524d8246a7912a83295e8aeb11ce17de30e8931`

The protocol hash still matched after the audit. No definitions, thresholds,
or sampled cases were changed, and no case was replaced. All eight upstream
repositories were inspected at the commits recorded in the dataset. The audit
used implementation code and directly relevant helpers; first-party API
contracts were used only when a tool delegated the decisive behavior to a
remote service.

The previous keyword-linter findings, manual classifications, and linter JSON
were not opened or used. The pre-registered limitation remains: while locating
the old inventory, the auditor had already encountered the names `read_file`,
`search_files`, and `assign_copilot_to_issue` and learned that the latter two
had previous warnings. Mechanical sampling selected `read_file` and
`search_files`; both were classified solely from pinned source. No tool was
selected or prioritized because it looked suspicious.

The annotation defaults and applicability follow the official
[MCP `ToolAnnotations` schema](https://modelcontextprotocol.io/specification/2025-11-25/schema#toolannotations).
The observed shape of the results is consistent with MCP's deliberate use of
cautious defaults, as described in the official
[Tool Annotations article](https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/):
imprecision appeared, but unsafe understatement did not.

## Sampling

The frozen inventory yielded 407 omitted applicable field units:

| Annotation | Candidate fields |
|---|---:|
| `readOnlyHint` | 61 |
| `destructiveHint` | 65 |
| `idempotentHint` | 113 |
| `openWorldHint` | 168 |
| **Total** | **407** |

The [sampling script](sample.py) used seed
`mcp-tool-lint-omitted-annotations-pilot-2026-08-08-v1`, SHA-256 ranking,
repository-first spread, and a global one-field-per-tool constraint. It selected
exactly 10 fields of each type, 40 distinct tools total, across all eight
repositories. Names, descriptions, prior warnings, and perceived suspiciousness
played no role in selection. The exact selected units and random ranks are in
[sample.csv](sample.csv).

Because annotation strata were forced to equal size rather than sampled in
proportion to their 407-field frame counts, the aggregate percentages below
must not be treated as prevalence estimates for that frame.

## Aggregate classifications

| Classification | Count | % of all 40 | Count among conclusive | % of 37 conclusive |
|---|---:|---:|---:|---:|
| `CORRECT` | 26 | 65.0% | 26 | 70.3% |
| `CONSERVATIVE_IMPRECISE` | 11 | 27.5% | 11 | 29.7% |
| `WRONG` | 0 | 0.0% | 0 | 0.0% |
| `INCONCLUSIVE` | 3 | 7.5% | 0 | 0.0% |

“Supportive” was pre-registered as `CONSERVATIVE_IMPRECISE + WRONG`. Thus the
supportive count was 11/40 (27.5%), or 11/37 (29.7%) among conclusive cases.

## Annotation-type statistics

| Annotation | n | Correct | Conservative-imprecise | Wrong | Inconclusive | Supportive % of all | Supportive % conclusive |
|---|---:|---:|---:|---:|---:|---:|---:|
| `readOnlyHint` | 10 | 8 | 2 | 0 | 0 | 20.0% | 20.0% |
| `destructiveHint` | 10 | 6 | 4 | 0 | 0 | 40.0% | 40.0% |
| `idempotentHint` | 10 | 3 | 4 | 0 | 3 | 40.0% | 57.1% |
| `openWorldHint` | 10 | 9 | 1 | 0 | 0 | 10.0% | 10.0% |

The evidence was not confined to one annotation type. The largest resolved
imprecision count was for `destructiveHint`; all inconclusive cases were
`idempotentHint`, reflecting uncertainty about repeat-call effects hidden
behind remote APIs rather than a changed classification rule.

## Repository-level statistics

| Repository | n | Correct | Conservative-imprecise | Wrong | Inconclusive | Supportive % of all |
|---|---:|---:|---:|---:|---:|---:|
| `KnockOutEZ/wigolo` | 5 | 4 | 1 | 0 | 0 | 20.0% |
| `github/github-mcp-server` | 11 | 7 | 2 | 0 | 2 | 18.2% |
| `korotovsky/slack-mcp-server` | 6 | 4 | 2 | 0 | 0 | 33.3% |
| `makenotion/notion-mcp-server` | 4 | 3 | 0 | 0 | 1 | 0.0% |
| `mark3labs/mcp-filesystem-server` | 8 | 3 | 5 | 0 | 0 | 62.5% |
| `microsoft/playwright-mcp` | 1 | 1 | 0 | 0 | 0 | 0.0% |
| `modelcontextprotocol/servers` | 1 | 0 | 1 | 0 | 0 | 100.0% |
| `t8y2/dbx` | 4 | 4 | 0 | 0 | 0 | 0.0% |

Repository sample sizes are small and unequal by design. These rows describe
the audited cases only and are not repository quality rankings.

## Inconclusive cases

- `S027`, Notion `API-update-a-data-source` / `idempotentHint`: the proxy and
  first-party contract establish assignment-like PATCH operations, but not
  whether an identical repeat changes service metadata or emits another event.
- `S028`, GitHub `update_pull_request` / `idempotentHint`: fixed-field updates
  coexist with optional reviewer requests, whose repeated notification/event
  behavior is not established by source or contract.
- `S030`, GitHub `create_pull_request` / `idempotentHint`: source always calls
  the create endpoint, while the contract does not specify whether an identical
  head/base repeat is rejected, coalesced, or creates another resource.

These cases remain in the 40-case denominator. They were not inferred from the
HTTP method alone and were not replaced.

## Decision and interpretation

The experiment was evaluable: 37 conclusive cases exceeded the required 32.
The `SUPPORTED` rule was met directly:

- 11 supportive cases, threshold at least 8;
- 29.7% supportive among conclusive cases, threshold at least 20%;
- five repositories with supportive cases, threshold at least three; and
- four annotation types with supportive cases, threshold at least two.

This supports the new omission/default hypothesis independently of the failed
keyword-heuristic hypothesis. More narrowly, the pilot found a recurring
precision problem: conservative defaults often prevented unsafe
understatement, but omitted explicit values could still materially affect
approval, retry, or trust-boundary handling. It does not show that keyword
heuristics detect these cases, and no keyword heuristic or product feature was
changed.

## One next action

**Pivot toward annotation coverage/quality tooling.**

## Artifacts and reproduction

- [protocol.md](protocol.md) and [protocol.sha256](protocol.sha256): frozen
  definitions and integrity marker.
- [sample.py](sample.py) and [sample.csv](sample.csv): deterministic selection
  procedure and exact 40-field sample.
- [classifications.csv](classifications.csv) and
  [classifications.sha256](classifications.sha256): locked judgments and audit
  evidence.
- [audit.csv](audit.csv): sample metadata joined to classifications and evidence.
- [annotation_statistics.csv](annotation_statistics.csv) and
  [repository_statistics.csv](repository_statistics.csv): grouped statistics.
- [metrics.json](metrics.json): aggregate metrics, threshold inputs, decision,
  and the single next action.
- [analyze.py](analyze.py): validation and result-generation script.

Reproduce selection and results from the experiment directory:

```bash
python3 sample.py --input ../pilot/tools.csv --output /tmp/omitted-sample.csv
shasum -a 256 /tmp/omitted-sample.csv
python3 analyze.py \
  --sample sample.csv \
  --classifications classifications.csv \
  --output-dir .
```
