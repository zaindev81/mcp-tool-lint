# Omitted MCP Tool Annotations: Pre-registered Source-Audit Protocol

Status: **FROZEN BEFORE SAMPLING OR SOURCE AUDIT**  
Protocol version: `omitted-annotations-v1`  
Frozen at: `2026-08-08T17:44:28+09:00`  
Experiment owner: `mcp-tool-lint` research pilot

## Research question and hypothesis

Research question: when an applicable boolean MCP Tool annotation is omitted,
how often does the resulting MCP default accurately describe the implementation,
and how often is it materially less precise or wrong?

Pre-registered hypothesis:

> Omitted MCP Tool annotations sometimes cause effective default values to
> inaccurately or imprecisely represent the actual behavior of the tool.

This experiment is independent of the earlier keyword-heuristic experiment. It
does not test, tune, or use those heuristics.

## Frozen inputs

The sampling frame is the pilot's checked-in tool inventory:

- `research/pilot/tools.csv`
  - SHA-256: `d93e30f120fe36c24ff80ed661845005330bd392bf581afc31357a67b21e6a20`
- `research/pilot/repositories.csv`
  - SHA-256: `0a1a4ec90a189d91207dfaa8876d2afb8df4ce4461b7e3f7b756b4e38025a232`
- linter repository commit: `e6889c415d7abadec846fd949c9ce1cbf99c71d1`
- upstream source snapshots: each repository's `pinned_commit` in those files

Only the eight repositories marked `ANALYZED` in the pilot repository manifest
are in the frame. The two repositories previously marked
`INCONCLUSIVE_REPOSITORY` are outside the frame because no faithful tool
population was captured for them.

The applicable MCP defaults are frozen from the official `ToolAnnotations`
schema:

| Annotation | Default when omitted | Applicability |
|---|---:|---|
| `readOnlyHint` | `false` | all tools |
| `destructiveHint` | `true` | meaningful when effective `readOnlyHint == false` |
| `idempotentHint` | `false` | meaningful when effective `readOnlyHint == false` |
| `openWorldHint` | `true` | all tools |

Primary specification reference: [MCP 2025-11-25 schema,
`ToolAnnotations`](https://modelcontextprotocol.io/specification/2025-11-25/schema#toolannotations).
The four defaults are unchanged in the source snapshots relevant to this
experiment.

## Sampling unit, inclusion, and exclusion

The sampling unit is one omitted applicable boolean annotation field on one
advertised tool, not an entire tool.

A field is included in the candidate frame exactly when:

1. its row is present in the frozen `tools.csv` inventory;
2. it is one of `readOnlyHint`, `destructiveHint`, `idempotentHint`, or
   `openWorldHint`;
3. `<annotation>_explicit` is the literal string `false`; and
4. `<annotation>_applicable` is the literal string `true`.

Applicability is frozen from the effective advertised metadata. In particular,
an omitted `readOnlyHint` has effective value `false`, so an omitted
`destructiveHint` or `idempotentHint` may be in frame even if later source
review establishes that the implementation is actually read-only. Such a
result is part of the omission problem and does not trigger replacement.

Excluded are:

- explicit annotation fields, regardless of their value;
- `title` and any non-boolean or newly introduced annotations;
- fields marked inapplicable in the frozen inventory;
- tools from repositories without a faithful captured population;
- tools absent from the frozen inventory; and
- all selection based on names, descriptions, prior warnings, prior manual
  classifications, or perceived suspiciousness.

Each tool may contribute at most one sampled field. This reduces within-tool
pseudo-replication and ensures 40 distinct implementations are reviewed.

## Deterministic stratified sampling method

Target sample size: exactly 40 fields, with exactly 10 from each annotation
type.

Random seed (UTF-8 literal):

```text
mcp-tool-lint-omitted-annotations-pilot-2026-08-08-v1
```

Canonical tool key is the compact JSON encoding of this array, with keys not
involved and with non-ASCII characters preserved:

```text
[repository,pinned_commit,source_server,tool]
```

Canonical field-unit ID is the compact JSON encoding of:

```text
[repository,pinned_commit,source_server,tool,annotation_type]
```

`rank(label)` is the lowercase hexadecimal SHA-256 digest of:

```text
UTF8(seed + "\0" + label)
```

Sampling is performed in this fixed annotation order:

1. `readOnlyHint`
2. `destructiveHint`
3. `idempotentHint`
4. `openWorldHint`

For each annotation stratum:

1. Remove candidate units whose tool key was selected in an earlier stratum.
2. Group remaining units by repository.
3. Sort repositories by `rank("repo\0" + annotation_type + "\0" + repository)`.
4. Within each repository, sort units by `rank(field_unit_ID)`.
5. In repository order, select the first unit from each non-empty repository,
   stopping if the stratum quota of 10 is reached.
6. If fewer than 10 have been selected, pool all unselected eligible units in
   the stratum, sort them by `rank(field_unit_ID)`, and take the first units
   whose tool keys remain unselected until the quota is filled.
7. Add selected tool keys to the global exclusion set before processing the
   next annotation stratum.

Ties, if any, are broken by the canonical field-unit ID in ascending Unicode
code-point order. The sampling script must assert 40 rows, 10 per annotation,
40 unique tool keys, and a non-empty source pointer for every row.

No sampled case will be replaced because it is difficult, surprising, or
inconclusive. A failure to retrieve or understand its pinned implementation is
classified `INCONCLUSIVE`.

## Blinding and audit sequence

Before all 40 classifications are locked, the auditor will not open or use:

- `research/pilot/findings.csv`;
- `research/pilot/manual_classifications.csv`;
- `research/pilot/linter/*.json`;
- the result sections of `research/pilot/report.md`; or
- prior linter warning status as evidence in any form.

The sampling script will read only the frozen tool inventory columns needed to
construct the frame and output the sample. Selection is entirely mechanical.
Tool names and source pointers are revealed only after selection. Descriptions
may be consulted after selection for navigation but never establish a
classification.

Known blinding limitation recorded before sampling: while locating the frozen
inventory, the auditor saw three illustrative tool names in the pilot's
reproduction notes (`read_file`, `search_files`, and
`assign_copilot_to_issue`) and learned that the latter two had prior semantic
warnings. These tools will be neither included nor excluded intentionally. If
mechanically sampled, their prior result will be ignored and the case will be
decided from pinned source under this protocol.

Audit order is the sample's deterministic `sample_id` order. For each case the
auditor will inspect the pinned implementation and directly relevant helpers
before recording one classification and a concise justification. Checked-in
tests, schemas, and first-party API documentation may corroborate behavior.
Names and descriptions alone may not.

## Operational semantic definitions

“Environment” means state observable outside the call's transient local
variables and returned value: files, databases, repositories, browser/session
state, server-persistent memory, subprocess-visible state, and remote services.
Incidental logging, metrics, tracing, and transparent caches are ignored unless
they are a documented user-observable purpose of the tool.

The value of a hint is evaluated over all successful behaviors permitted by
the input schema and ordinary supported configuration. A single supported path
is enough to establish a conservative `may` property. Pure error paths are not
effects.

- `readOnlyHint` is actually `true` only if every supported successful path
  leaves the environment unchanged. It is actually `false` if any supported
  path creates, updates, deletes, sends, executes, or otherwise mutates
  environmental state.
- `destructiveHint` is actually `true` if any supported path can delete,
  overwrite, revoke, cancel, close, replace, or otherwise alter pre-existing
  state. It is actually `false` when mutations are exclusively additive. A
  read-only implementation has no destructive effect and is treated as the
  conservative-opposite case for an omission that became applicable through
  effective `readOnlyHint: false`.
- `idempotentHint` is actually `true` only if, after one call with given
  arguments, repeating the call with the same arguments can add no further
  environmental effect. Response variation, reads of newly changed external
  state, incidental logs/metrics, and the fact that a repeat may return an
  error do not by themselves defeat idempotence. It is `false` if any
  supported same-argument repetition can append, increment, duplicate,
  re-send, re-trigger, or otherwise add an effect. A read-only implementation
  is treated as the conservative-opposite case under the same applicability
  rule above.
- `openWorldHint` is actually `true` if any supported path can communicate
  with or obtain content from entities outside the server-controlled local
  domain, including arbitrary/public URLs, remote SaaS or source-control APIs,
  remote communication systems, externally hosted databases/services, or
  caller-selected subprocesses capable of such access. It is `false` for
  computation, clocks, server-local files/process state, and server-owned
  in-process memory with no such interaction. Merely accepting user input does
  not make a tool open-world.

For a tool with modes or branches, these definitions deliberately choose the
conservative aggregate value: all paths must satisfy `readOnlyHint: true` or
`idempotentHint: true`, while one qualifying path establishes
`destructiveHint: true` or `openWorldHint: true`.

## Classification definitions

Each sampled field receives exactly one label:

- `CORRECT`: source evidence establishes that the implementation's aggregate
  semantic value equals the omission-induced MCP default.
- `CONSERVATIVE_IMPRECISE`: source evidence establishes the opposite literal
  value, but the omission-induced value is the safer, more cautious
  representation and an explicit annotation would materially improve
  precision. Material improvement means it could validly affect approval/risk
  presentation, retry eligibility, trust-boundary handling, or equivalent
  client behavior—not merely wording or style.
- `WRONG`: source evidence establishes a conflict that is not a safe
  conservative approximation, such as an omission-induced effective value
  that understates behavior or would authorize materially unsafe handling.
  The category is retained even though the four specified MCP defaults are
  intentionally conservative and therefore make this outcome structurally
  unlikely.
- `INCONCLUSIVE`: pinned source and relevant context do not establish a
  reliable aggregate semantic value, or do not establish materiality, without
  relying on a name/description, unsupported deployment assumptions, or
  speculation about a dependency.

The opposite of each omission default (`readOnlyHint: true`,
`destructiveHint: false`, `idempotentHint: true`, or `openWorldHint: false`) is
presumptively conservative-imprecise only after source establishes it and the
materiality condition. Uncertainty is never counted as support.

## Evidence rules

Every row must record:

- repository and pinned commit;
- tool and sampled annotation;
- omission-induced default;
- classification;
- concise behavior summary;
- source file path plus line range or stable symbol;
- directly relevant helper/API evidence when needed; and
- a justification connecting evidence to the annotation definition.

Implementation code is required evidence. Tool name or prose description may
only help locate code. If behavior delegates to a dependency, the audit must
trace a locally pinned helper, checked-in API operation/schema, or authoritative
first-party API contract far enough to establish the relevant effect. Otherwise
the case is `INCONCLUSIVE`.

Classifications are locked when written to the completed audit dataset. They
will not be changed after aggregate counts are viewed except to correct a
mechanical transcription error, which must be logged.

## Inconclusive cases and protocol deviations

`INCONCLUSIVE` cases remain in the 40-case denominator and are not replaced.
Percentages will be reported both over all 40 sampled fields and, secondarily,
over conclusive fields. No imputation is allowed.

If more than 8 cases (20%) are inconclusive, the decision is automatically
`INCONCLUSIVE`, regardless of the observed supportive cases.

No classification or threshold definition may change after source inspection
begins. If a material protocol defect requires a change, this experiment stops;
the reason is documented, and any revised procedure starts as a separately
named experiment with a new seed and sample.

## Pre-registered metrics

The report will include:

- counts and percentages for all four classifications over all 40 fields;
- the same counts and percentages over conclusive fields;
- counts by repository and annotation type;
- supportive count = `CONSERVATIVE_IMPRECISE + WRONG`;
- number of distinct repositories and annotation types containing supportive
  cases; and
- the inconclusive count and reasons.

No confidence interval or significance test will be used to make a
population-level claim. This is a descriptive 40-case pilot.

## Success, failure, and decision rule

The experiment is evaluable only if at least 32 of 40 cases are conclusive.
Subject to that gate:

- `SUPPORTED`: at least 8 supportive cases, supportive cases are at least 20%
  of conclusive cases, and they span at least 3 repositories and at least 2
  annotation types.
- `PARTIALLY_SUPPORTED`: at least 4 supportive cases and at least 10% of
  conclusive cases, but the full `SUPPORTED` threshold or breadth condition is
  not met.
- `NOT_SUPPORTED`: fewer than 4 supportive cases or less than 10% of
  conclusive cases.
- `INCONCLUSIVE`: fewer than 32 conclusive cases, a material protocol failure,
  or evidence-integrity failure prevents the pre-registered rule from being
  applied.

Here, “success” means `SUPPORTED`; “partial success” means
`PARTIALLY_SUPPORTED`; “failure” means `NOT_SUPPORTED`; and inability to make a
reliable decision means `INCONCLUSIVE`.

After applying this rule, the final report will recommend exactly one next
action. The action will be chosen from: expand the source audit; pivot toward
annotation coverage/quality tooling; investigate one annotation type more
deeply; or stop this research direction. No product feature will be added in
this experiment.
