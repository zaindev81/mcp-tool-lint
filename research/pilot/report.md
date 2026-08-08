# Real-world MCP Tool Annotation Pilot

Study date: 2026-08-08 (Asia/Tokyo)

Linter snapshot: `e6889c415d7abadec846fd949c9ce1cbf99c71d1`

Decision: **INCONCLUSIVE**

## Outcome

This pilot did not find evidence that the current linter detects meaningful
real-world annotation mistakes. It did find incomplete explicit annotation
coverage, but omission alone is not an error and was not counted as one.

- Ten repositories were selected by a frozen, popularity-ordered procedure;
  eight could be analyzed reliably and two remained repository-level
  inconclusive results.
- The eight analyzed repositories exposed 267 tools. Of those, 229 (85.77%)
  specified at least one supported annotation and 38 (14.23%) specified none.
- 192 tools (71.91%) omitted at least one *applicable* annotation. These sets
  overlap: a tool can specify one hint while omitting another.
- Explicit values covered 407 of 814 applicable annotation slots (50.00%).
- The frozen linter emitted 16 semantic review candidates: 0 `HIGH` and 16
  `WARN`. Manual source inspection classified 14 as `FALSE_POSITIVE`, two as
  `INCONCLUSIVE`, and none as `TRUE_POSITIVE` or `LIKELY_TRUE_POSITIVE`.
- The approximate false-positive rate among decidable semantic findings was
  therefore 100% (14 / 14). The two inconclusive findings are reported
  separately and excluded from that denominator.
- The other 407 linter findings were MCP005 coverage information. They were
  not treated as vulnerabilities or included in semantic precision.

The omission portion of the hypothesis is plainly observable in this sample.
The more important claim—that omitted or explicit values are meaningfully
wrong and that this keyword linter detects those mistakes—was not established.
The pre-registered `NOT_SUPPORTED` threshold was not met either, because only
five repositories had usable explicit annotations and the protocol required at
least seven. The appropriate pilot decision is therefore `INCONCLUSIVE`, not a
claim that the hypothesis is false.

## Method

The definitions, sample size, strata, extraction rules, finding classes,
metric formula, and decision thresholds were frozen before repository search
and annotation inspection. The complete protocol is in
[`protocol.md`](protocol.md); no post-freeze amendments were made.

The sample used ten functional strata and selected the first eligible result
from each recorded GitHub query sorted by stars. This makes the selection
reproducible and avoids selecting for interesting findings, although it creates
a deliberate popularity bias. Exact queries, rejected higher-ranked results,
snapshot metadata, and selection rationales are in
[`selection.md`](selection.md).

An MCP Tool was a named operation exposed by `tools/list`, an SDK tool
registration/decorator, or an equivalent protocol handler. Prompts, resources,
and internal helpers were excluded. Tool definitions that depended on runtime
external state were not guessed. Explicit annotation values were retained
separately from effective MCP defaults. In accordance with MCP semantics,
omitted fields were interpreted only in the effective-value columns as:

- `readOnlyHint=false`
- `destructiveHint=true`
- `idempotentHint=false`
- `openWorldHint=true`

`destructiveHint` and `idempotentHint` were excluded from applicable coverage
when effective `readOnlyHint=true`. The annotation meanings and defaults used
here match the [MCP project’s annotation guidance](https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/).

Each successfully extracted repository was converted into the linter's input
array without inserting omitted keys. The frozen linter ran once per
repository. Every `HIGH` and `WARN` result was then checked against the pinned
implementation and nearby documentation. Rules were not changed in response
to outcomes.

## Repository sample

Popularity is stars/forks at selection time, not a live value. Tool counts are
for the recorded extraction configuration at the pinned commit.

| Repository | Stratum | Popularity | Language / MCP SDK | Tools | Status | Why selected |
|---|---|---:|---|---:|---|---|
| [mark3labs/mcp-filesystem-server](https://github.com/mark3labs/mcp-filesystem-server) | filesystem | 675 / 109 | Go / mcp-go 0.32.0 | 14 | analyzed | Highest-starred eligible dedicated filesystem server. |
| [prest/prest](https://github.com/prest/prest) | relational database | 4,610 / 315 | Go / custom JSON-RPC | — | inconclusive | Highest-starred eligible PostgreSQL project shipping an MCP server. |
| [github/github-mcp-server](https://github.com/github/github-mcp-server) | developer workflow | 32,040 / 4,750 | Go / official Go SDK 1.7.0 | 85 | analyzed | Highest-starred eligible result and official GitHub server. |
| [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) | browser automation | 35,904 / 2,994 | TypeScript / Playwright MCP stack | 42 | analyzed | Highest-starred eligible dedicated Playwright server. |
| [KnockOutEZ/wigolo](https://github.com/KnockOutEZ/wigolo) | web/HTTP retrieval | 4,407 / 314 | TypeScript / official TS SDK 1.29 | 10 | analyzed | Highest-starred eligible web search/fetch/crawl server. |
| [korotovsky/slack-mcp-server](https://github.com/korotovsky/slack-mcp-server) | communication | 1,770 / 350 | Go / mcp-go 0.44.0 | 22 | analyzed | First eligible dedicated Slack server after three stratum mismatches. |
| [awslabs/mcp](https://github.com/awslabs/mcp) | cloud infrastructure | 9,573 / 1,700 | Python / FastMCP and MCP SDK | — | inconclusive | First eligible AWS collection after excluding an MCP client. |
| [makenotion/notion-mcp-server](https://github.com/makenotion/notion-mcp-server) | productivity | 4,579 / 614 | TypeScript / official TS SDK 1.29 | 24 | analyzed | Highest-starred eligible dedicated Notion server. |
| [t8y2/dbx](https://github.com/t8y2/dbx) | data store | 13,683 / 1,405 | Rust / rmcp 2.2.0 | 12 | analyzed | Highest-starred eligible data-store project with a built-in server. |
| [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | reference/general | 89,337 / 11,404 | TypeScript/Python / official SDKs | 58 | analyzed | Highest-starred eligible reference-server collection. |

The exact commits, activity dates, licenses, extraction notes, and machine-
readable selection reasons are in [`repositories.csv`](repositories.csv).

## Extraction outcomes

The eight analyzed repositories were extracted using one of three lightweight
methods: local credential-free `tools/list`, static SDK registration parsing,
or checked-in generated metadata. Extraction provenance is recorded per tool
in [`tools.csv`](tools.csv), together with explicit values, effective values,
and applicability for all four supported hints.

The two retained inconclusive repositories were not assigned partial or
guessed tool populations:

- `prest/prest` has two unconditional generic tools, up to three tools
  controlled by exposure policy, and one dynamically named/described tool per
  accessible queryable database table. A faithful population requires a
  particular live database catalog.
- `awslabs/mcp` is a collection of 59 server packages containing both static
  decorators and runtime-generated tools sourced from Lambda, Step Functions,
  OpenAPI documents, and AWS service models. No single credential-free setup
  faithfully enumerates a repository-wide population.

Configuration choices for analyzed servers were recorded rather than hidden:
GitHub used all toolsets without feature flags; Playwright enabled the vision,
PDF, and devtools capabilities; Slack included statically registered optional
tools; and the reference collection combined the advertised Everything,
Filesystem, Memory, Sequential Thinking, Git, Time, and Fetch servers.

One representation issue required source reconciliation rather than a protocol
change. The Go SDK serialized omitted false-valued booleans in the GitHub
server's `tools/list` output. Source literals were used to distinguish fields
actually written by the repository from Go zero-value serialization. The
served effective values were not altered.

## Repository-level results

“Any” means at least one supported field was explicit. “Missing” means at
least one *applicable* field was omitted; it can overlap with “any.” Slot
coverage is explicit applicable fields divided by all applicable fields.

| Repository | Tools | Any annotation | No annotations | Missing applicable | Full coverage | Slot coverage | WARN / HIGH |
|---|---:|---:|---:|---:|---:|---:|---:|
| mark3labs/mcp-filesystem-server | 14 | 0 | 14 | 14 | 0 | 0 / 56 | 0 / 0 |
| prest/prest | 0 | 0 | 0 | 0 | 0 | — | 0 / 0 |
| github/github-mcp-server | 85 | 85 | 0 | 85 | 0 | 92 / 232 | 4 / 0 |
| microsoft/playwright-mcp | 42 | 42 | 0 | 24 | 18 | 108 / 132 | 1 / 0 |
| KnockOutEZ/wigolo | 10 | 0 | 10 | 10 | 0 | 0 / 40 | 0 / 0 |
| korotovsky/slack-mcp-server | 22 | 21 | 1 | 22 | 0 | 21 / 68 | 1 / 0 |
| awslabs/mcp | 0 | 0 | 0 | 0 | 0 | — | 0 / 0 |
| makenotion/notion-mcp-server | 24 | 24 | 0 | 24 | 0 | 24 / 72 | 1 / 0 |
| t8y2/dbx | 12 | 0 | 12 | 12 | 0 | 0 / 48 | 0 / 0 |
| modelcontextprotocol/servers | 58 | 57 | 1 | 1 | 57 | 162 / 166 | 9 / 0 |
| **Total analyzed** | **267** | **229** | **38** | **192** | **75** | **407 / 814** | **16 / 0** |

The exact repository aggregates are in
[`repository_stats.csv`](repository_stats.csv), and the calculated totals are
in [`metrics.json`](metrics.json).

## What missing annotations mean in this sample

Missing fields were common, but the raw count mixes several qualitatively
different cases:

- Mark3labs, Wigolo, and dbx omitted all four hints. Obvious read operations in
  the filesystem and database tools consequently inherit conservative
  `readOnlyHint=false` and `destructiveHint=true` defaults. Local operations
  also inherit `openWorldHint=true`, which can be imprecise. This is useful
  coverage information, but it does not prove a dangerous client decision or
  a repository mistake.
- The reference Fetch tool also omitted all hints; its effective
  `openWorldHint=true` is consistent with remote retrieval, while the mutation
  defaults are conservative.
- Slack's unannotated `usergroups_me` combines listing, joining, and leaving,
  making a single static annotation tuple less straightforward than its raw
  omission suggests.
- GitHub and Notion frequently omitted hints whose defaults are natural for
  remote or mutating operations: open-world defaults true, destructive defaults
  true, and idempotence defaults false. A missing-field total cannot distinguish
  deliberate reliance on those defaults from accidental omission.
- Playwright's applicable omissions were chiefly idempotence hints on
  state-changing tools, which correctly default false absent stronger claims.

The pilot did not manually adjudicate all 407 omissions, so it cannot estimate
how many effective defaults are correct, merely conservative, or actually
wrong. Treating those coverage items as vulnerabilities would overstate the
evidence.

## Manual review of semantic findings

All 16 `WARN` findings were reviewed. The table is intentionally complete;
full linter messages, excerpts, classification reasons, and source provenance
are in [`findings.csv`](findings.csv) and
[`manual_classifications.csv`](manual_classifications.csv).

| Repository | Tool | Rule | Classification | Manual reason |
|---|---|---|---|---|
| github/github-mcp-server | `assign_copilot_to_issue` | MCP003 | INCONCLUSIVE | Repeating the assignment is delegated to GitHub; source and public docs do not establish deduplication versus another agent run. “PR created” is not enough to decide idempotence. |
| github/github-mcp-server | `assign_copilot_to_issue_with_intent` | MCP003 | INCONCLUSIVE | Suggestion and direct-assignment branches have service-defined repeat semantics. The matched word “created” does not resolve them. |
| github/github-mcp-server | `list_notifications` | MCP001 | FALSE_POSITIVE | “Updates” is a noun describing notifications; the handler only calls list APIs. |
| github/github-mcp-server | `search_issues` | MCP001 | FALSE_POSITIVE | “Reset” appears in the example query “password reset”; the handler searches issues. |
| korotovsky/slack-mcp-server | `usergroups_list` | MCP001 | FALSE_POSITIVE | “Joining/updating” describes later uses of a returned ID; this handler only retrieves groups. |
| makenotion/notion-mcp-server | `API-retrieve-page-markdown` | MCP001 | FALSE_POSITIVE | “Update” is in a 403 capability message; the operation and generated client use HTTP GET. |
| microsoft/playwright-mcp | `browser_hide_highlight` | MCP001 | FALSE_POSITIVE | It removes only Playwright's transient diagnostic overlay, not application data or target-page state. Read-only confirmation behavior is reasonable. |
| modelcontextprotocol/servers | `trigger-long-running-operation` | MCP001 | FALSE_POSITIVE | “Updates” means progress notifications; the tool waits and reports progress without durable mutation. |
| modelcontextprotocol/servers | `trigger-elicitation-request` | MCP004 | FALSE_POSITIVE | The request goes to the already-connected MCP client/user, not an unpredictable external entity. |
| modelcontextprotocol/servers | `simulate-research-query` | MCP004 | FALSE_POSITIVE | Research is simulated locally and optional elicitation stays on the client connection; no web search occurs. |
| modelcontextprotocol/servers | `trigger-elicitation-request-async` | MCP004 | FALSE_POSITIVE | Async elicitation stays on the existing client session; the generic word “request” does not imply open-world access. |
| modelcontextprotocol/servers | `write_file` | MCP003 | FALSE_POSITIVE | Writing the same content to the same path repeatedly leaves the same contents; “create/overwrite” does not make a PUT-like operation non-idempotent. |
| modelcontextprotocol/servers | `create_directory` | MCP003 | FALSE_POSITIVE | Recursive mkdir succeeds for an existing directory; repeating identical arguments adds no structural effect. |
| modelcontextprotocol/servers | `search_files` | MCP004 | FALSE_POSITIVE | Search is restricted to configured local allowed directories, a closed domain. |
| modelcontextprotocol/servers | `get_file_info` | MCP001 | FALSE_POSITIVE | “Modified” names a timestamp field; the implementation only calls file-stat operations. |
| modelcontextprotocol/servers | `search_nodes` | MCP004 | FALSE_POSITIVE | Search operates on the server's local knowledge-graph file, not external entities. |

No finding qualified for the requested confirmed-finding investigation. The
two Copilot findings were inspected through their GraphQL mutation paths and
[GitHub's coding-agent documentation](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/use-cloud-agent-on-github)
documents that assigning Copilot starts work and can produce a pull request,
but not what an identical repeat assignment does. They remain genuinely
inconclusive rather than upstream-ready reports. No issue or pull request was
opened.

## Basic metrics

| Metric | Result |
|---|---:|
| Repositories selected | 10 |
| Repositories analyzed | 8 |
| Repository-level inconclusive | 2 |
| Tools analyzed | 267 |
| Tools with at least one explicit annotation | 229 (85.77%) |
| Tools with no explicit annotations | 38 (14.23%) |
| Tools missing at least one applicable annotation | 192 (71.91%) |
| Applicable annotation slots explicitly covered | 407 / 814 (50.00%) |
| Total linter findings including coverage | 423 |
| MCP005 coverage items | 407 |
| Semantic review candidates | 16 (0 HIGH, 16 WARN) |
| TRUE_POSITIVE | 0 |
| LIKELY_TRUE_POSITIVE | 0 |
| FALSE_POSITIVE | 14 |
| INCONCLUSIVE findings | 2 |
| Approximate decidable false-positive rate | 100% (14 / 14) |

These are descriptive pilot statistics, not estimates for the broader MCP
ecosystem. Tools are clustered within repositories and are not independent
observations. GitHub and the reference collection alone account for 143 of the
267 analyzed tools, so tool-weighted percentages are especially sensitive to
those two projects.

## Remaining error risks

Observed false-positive mechanisms were broad and repeatable: verbs used as
nouns, examples and error text mistaken for behavior, references to later
actions, transient diagnostic state, local search mistaken for open-world
access, client-session requests mistaken for external access, and creation or
overwrite language mistaken for non-idempotence. Similar wording is likely to
produce more false positives in another sample.

False-negative risk is at least as important but was not measurable here. The
manual review was triggered only by linter findings, so there is no ground-
truth audit of unflagged explicit annotations. The linter can miss synonyms,
irregular wording, behavior not stated in descriptions, conditional effects,
and side effects hidden behind APIs. Runtime-generated tools in the two
inconclusive repositories are also absent from tool-level metrics. Finally,
annotation judgments such as transient-state read-only behavior and
service-defined idempotence can remain ambiguous even after source inspection.

## Hypothesis evaluation

**INCONCLUSIVE.** Annotation omission exists in this small sample, but this
pilot did not demonstrate that the omissions are meaningful mistakes. It also
found no confirmed or likely explicit misconfiguration among the linter's 16
review candidates, while 14 decidable candidates were false positives. That
fails the `SUPPORTED` and `PARTIALLY_SUPPORTED` rules. Because usable explicit
annotations appeared in only five repositories, it also falls short of the
pre-registered seven-repository threshold needed to declare `NOT_SUPPORTED`.

The strongest defensible conclusion is narrower: explicit annotation coverage
is uneven, and the current keyword candidates had no demonstrated positive
yield in this pilot. Whether omitted defaults are materially wrong remains the
unanswered part of the research question.

## One next experiment

Run a pre-registered, blinded source audit of a fixed stratified sample of 40
omitted *applicable* annotation slots from these eight analyzed repositories.
Classify each effective default as correct, conservative-but-imprecise, wrong,
or inconclusive without looking at linter findings. This single experiment
directly tests whether the observed omission is a meaningful problem before
adding repositories, changing rules, or building features.

## Artifacts

- [`protocol.md`](protocol.md): frozen definitions and decision rules
- [`selection.md`](selection.md): queries, exclusions, snapshots, rationales
- [`repositories.csv`](repositories.csv): repository manifest
- [`tools.csv`](tools.csv): 267 extracted tool definitions and hint states
- [`findings.csv`](findings.csv): all 423 linter results and classifications
- [`manual_classifications.csv`](manual_classifications.csv): the 16 semantic reviews
- [`repository_stats.csv`](repository_stats.csv): repository aggregates
- [`metrics.json`](metrics.json): calculated pilot totals
- [`reproduction.md`](reproduction.md): commands and data-flow checks
