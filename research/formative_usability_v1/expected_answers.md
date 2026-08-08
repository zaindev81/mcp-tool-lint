# Expected answers — facilitator only

Status: **FROZEN BEFORE PARTICIPANT TESTING**

Do not show this file to participants until both blocks are complete and all
scored answers are locked.

## Scoring legend

- Origin: `E` = explicit, `D` = MCP default
- Effective value: `T` = true, `F` = false
- Applicable and source review: `Y` = yes, `N` = no

Each annotation row has four binary-scored answers. Each Tool also has one
binary omission/vulnerability answer, for 17 scored answers per Tool and 68
per condition. Confidence and source-review prioritization are not correctness
items.

## Set X

| Case | Tool | Annotation | Origin | Value | Applicable | Review |
|---|---|---|:---:|:---:|:---:|:---:|
| X1 | `actions_get` | `readOnlyHint` | E | T | Y | N |
| X1 | `actions_get` | `destructiveHint` | D | T | N | N |
| X1 | `actions_get` | `idempotentHint` | D | F | N | N |
| X1 | `actions_get` | `openWorldHint` | D | T | Y | Y |
| X2 | `create_branch` | `readOnlyHint` | E | F | Y | N |
| X2 | `create_branch` | `destructiveHint` | D | T | Y | Y |
| X2 | `create_branch` | `idempotentHint` | D | F | Y | Y |
| X2 | `create_branch` | `openWorldHint` | D | T | Y | Y |
| X3 | `search_files` | `readOnlyHint` | D | F | Y | Y |
| X3 | `search_files` | `destructiveHint` | D | T | Y | Y |
| X3 | `search_files` | `idempotentHint` | D | F | Y | Y |
| X3 | `search_files` | `openWorldHint` | D | T | Y | Y |
| X4 | `echo` | `readOnlyHint` | E | T | Y | N |
| X4 | `echo` | `destructiveHint` | E | F | N | N |
| X4 | `echo` | `idempotentHint` | E | T | N | N |
| X4 | `echo` | `openWorldHint` | E | F | Y | N |

## Set Y

| Case | Tool | Annotation | Origin | Value | Applicable | Review |
|---|---|---|:---:|:---:|:---:|:---:|
| Y1 | `API-get-users` | `readOnlyHint` | E | T | Y | N |
| Y1 | `API-get-users` | `destructiveHint` | D | T | N | N |
| Y1 | `API-get-users` | `idempotentHint` | D | F | N | N |
| Y1 | `API-get-users` | `openWorldHint` | D | T | Y | Y |
| Y2 | `dismiss_notification` | `readOnlyHint` | E | F | Y | N |
| Y2 | `dismiss_notification` | `destructiveHint` | D | T | Y | Y |
| Y2 | `dismiss_notification` | `idempotentHint` | D | F | Y | Y |
| Y2 | `dismiss_notification` | `openWorldHint` | D | T | Y | Y |
| Y3 | `read_file` | `readOnlyHint` | D | F | Y | Y |
| Y3 | `read_file` | `destructiveHint` | D | T | Y | Y |
| Y3 | `read_file` | `idempotentHint` | D | F | Y | Y |
| Y3 | `read_file` | `openWorldHint` | D | T | Y | Y |
| Y4 | `get-sum` | `readOnlyHint` | E | T | Y | N |
| Y4 | `get-sum` | `destructiveHint` | E | F | N | N |
| Y4 | `get-sum` | `idempotentHint` | E | T | N | N |
| Y4 | `get-sum` | `openWorldHint` | E | F | Y | N |

## Omission/vulnerability answer

The expected answer for every Tool is **no**. An omitted applicable annotation
uses a defined default and may warrant source review; the artifact does not
inspect implementation behavior or establish an error, severity, exploit, or
vulnerability. Score the yes/no choice only. Code the one-sentence explanation
qualitatively as `correct rationale`, `unclear rationale`, or `vulnerability
misconception`.

## Matched-set check

Positions X1/Y1, X2/Y2, X3/Y3, and X4/Y4 have identical answers. Each set has:

- 64 annotation judgments plus 4 vulnerability judgments;
- 12 applicable fields;
- 4 explicit applicable fields;
- 8 source-review fields; and
- 4 explicit but inapplicable conditional fields.

## Stimulus provenance

| Upstream repository | Pinned commit | Frozen inventory SHA-256 | Selected Tools |
|---|---|---|---|
| `github/github-mcp-server` | `eb4c099e05ef622445e930b18682a0464f22418f` | `350132325cb32db4b3908bdd0190a7f8031e224d9682ef5fa0c59811dfbbc364` | `actions_get`, `create_branch`, `dismiss_notification` |
| `makenotion/notion-mcp-server` | `1d38420769c8a1fe2d583ff1e7d2d108d4eb0b30` | `fac3dbe2fa24899e4a23dc2293b8e06981c25dc6966a2a17a48a064b03cecbae` | `API-get-users` |
| `mark3labs/mcp-filesystem-server` | `ba3f07f22c309d932fa9b1cebe1eb7c55fcbb83b` | `0d58c2865a9b6370251b8883126e7794d5e6c6ad30bff01e6f5932b87cf8288a` | `search_files`, `read_file` |
| `modelcontextprotocol/servers` | `76d64c822f5125032f89eb71dbdb94e42b434821` | `79c9c2bcebfa27a47400ccef171e32e4637e789618b65fa57234995059e39716` | `echo`, `get-sum` |

Descriptions and annotation objects in the raw stimuli are exact copies of the
listed frozen inventories. The report files are exact stdout from the frozen
product invoked without `--json` on the corresponding raw stimulus.
