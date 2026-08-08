# MCP Tool Annotation Pilot Protocol

Status: **frozen before repository search and annotation inspection**

Protocol date: 2026-08-08 (Asia/Tokyo)

Linter commit: `e6889c415d7abadec846fd949c9ce1cbf99c71d1`

## Research question

Do real open-source MCP servers omit or incorrectly configure MCP Tool
annotations often enough that this static linter identifies meaningful review
candidates?

The pilot is designed to falsify, not confirm, that hypothesis. Missing
annotations are coverage data, not vulnerabilities. Keyword findings are
review candidates, not proof of behavior.

## Sample size and selection

Select exactly ten public GitHub repositories, one from each stratum below:

1. local filesystem or local storage
2. relational database
3. GitHub or developer workflow
4. browser or web automation
5. web or HTTP retrieval
6. communication or messaging
7. cloud infrastructure
8. productivity or knowledge management
9. cache, search, or data store
10. general-purpose or reference MCP servers

For each stratum, run the recorded GitHub repository search query sorted by
stars descending on the protocol date. Examine results in that order and
select the first eligible repository not already selected. Record the query,
rank examined, rejection reasons, repository metadata, and selected commit.
This deliberately introduces a popularity bias, which will be reported as a
limitation, but avoids choosing repositories based on annotation outcomes.

Do not replace a selected repository merely because its tools or annotations
are difficult to extract. If it met the eligibility criteria at selection but
reliable extraction later fails, retain it as `INCONCLUSIVE_REPOSITORY`.

## Repository inclusion criteria

A repository must:

- be public, non-archived, and not a fork;
- contain an identifiable open-source license;
- describe itself as an MCP server or MCP server collection;
- contain implementation source that serves at least one MCP Tool;
- have a default-branch commit within the 24 months preceding the protocol
  date;
- allow a source commit to be pinned and inspected; and
- primarily implement the selected stratum, rather than merely mentioning it.

Monorepositories are eligible only when MCP servers are a primary purpose. A
repository may satisfy multiple strata but can be selected only once.

## Exclusion criteria

Exclude:

- MCP clients, SDKs, directories, registries, tutorials, or link lists without
  an implemented server;
- templates with no concrete exposed tools;
- mirrors, forks, archived repositories, and duplicate implementations;
- repositories without an identifiable open-source license;
- repositories with no commit in the preceding 24 months; and
- repositories that do not actually fit the stratum after pre-annotation
  source inspection.

Failure to extract tools after selection is not an exclusion.

## Unit of analysis: MCP Tool

An MCP Tool is a named operation exposed through MCP `tools/list`, an MCP SDK
tool registration/decorator, or the repository's protocol-equivalent tool
handler. Prompts, resources, resource templates, and non-MCP helper functions
are excluded. Separately exposed aliases count separately. Statically
enumerated generated tools count separately; tools whose names and metadata
exist only at runtime make the repository inconclusive unless a faithful local
enumeration is possible without external services or credentials.

The extraction snapshot is the selected repository commit. Record the source
file and line or other reproducible provenance for each tool.

## Annotation extraction

For every tool, record its name, description, and each of:

- `readOnlyHint`
- `destructiveHint`
- `idempotentHint`
- `openWorldHint`

For each field, record whether it is explicitly specified. Preserve an omitted
field as omitted in the extraction dataset; do not write the MCP default into
the explicit-value column. Effective defaults may be recorded separately:

- `readOnlyHint=false`
- `destructiveHint=true`
- `idempotentHint=false`
- `openWorldHint=true`

## Definitions fixed for analysis

**Missing annotation field**
: A supported annotation key absent from the tool definition. For coverage
  analysis, omitted `destructiveHint` and `idempotentHint` are non-applicable
  when effective `readOnlyHint=true`; their raw omission is still recorded.

**Tool with annotations**
: A tool with at least one explicitly specified supported annotation.

**Tool missing annotations**
: A tool with at least one omitted applicable supported annotation. This can
  overlap with "tool with annotations."

**Suspicious annotation**
: A `HIGH` or `WARN` finding emitted by the frozen linter. This is a candidate
  for manual review, not a vulnerability or confirmed error.

**Confirmed mistake / `TRUE_POSITIVE`**
: Direct source behavior or authoritative repository documentation strongly
  contradicts the explicit annotation value.

**`LIKELY_TRUE_POSITIVE`**
: The explicit annotation appears inconsistent with the inspected behavior,
  but important behavior is conditional, delegated, or otherwise not fully
  confirmable statically.

**`FALSE_POSITIVE`**
: The annotation is reasonable for the observed behavior and the linter's
  textual heuristic is misleading.

**`INCONCLUSIVE` finding**
: Available source and documentation do not establish whether the explicit
  annotation is correct.

**`INCONCLUSIVE_REPOSITORY`**
: Tool metadata cannot be extracted reliably from the pinned source. It stays
  in the repository denominator but contributes no tool-level observations.

MCP005 findings are coverage information and receive classification
`COVERAGE_INFO`, not one of the semantic finding classifications.

## Lint and manual-review procedure

1. Convert extracted tools to the linter's accepted JSON array without adding
   omitted annotation keys.
2. Run the frozen linter commit once per repository and save JSON output.
3. Do not change rules, keywords, severities, or extraction because of results.
4. Record every finding verbatim with repository and tool provenance.
5. Manually inspect every `HIGH` and `WARN` finding against the tool
   implementation and nearby documentation.
6. Assign exactly one classification and a short evidence-based reason.
7. For `TRUE_POSITIVE` and strong `LIKELY_TRUE_POSITIVE` findings, record the
   relevant behavior and whether an upstream report appears reasonable. Do not
   contact maintainers in this pilot.

## Metrics

Report:

- repositories selected and repositories successfully analyzed;
- total tools analyzed;
- tools with at least one explicit supported annotation;
- tools with at least one omitted applicable annotation;
- applicable annotation slots and explicitly covered slots;
- total `HIGH`/`WARN` findings and separate MCP005 coverage items;
- counts of each manual classification;
- approximate false-positive rate:
  `FALSE_POSITIVE / (TRUE_POSITIVE + LIKELY_TRUE_POSITIVE + FALSE_POSITIVE)`.

Exclude inconclusive findings from that rate and report their count beside it.
Do not make population-level or statistically strong claims from ten
repositories.

## Hypothesis decision rule

- `SUPPORTED`: at least two repositories contain confirmed or strong likely
  mistakes, and the decidable false-positive rate is at most 30%.
- `PARTIALLY_SUPPORTED`: at least one confirmed/likely mistake exists, but the
  false-positive rate exceeds 30% or coverage limits are substantial.
- `NOT_SUPPORTED`: no confirmed/likely mistakes are found despite usable
  annotations in at least seven repositories and at least 50 annotated tools.
- `INCONCLUSIVE`: none of the above applies, especially when annotations or
  extractable tools are too sparse.

The thresholds are pilot decision aids, not statistical significance tests.

## Protocol amendments

Any post-freeze methodological change must be appended here with timestamp,
reason, and likely effect. Never silently revise the definitions after seeing
results.

No amendments at freeze time.
