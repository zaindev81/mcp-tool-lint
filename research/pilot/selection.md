# Repository Selection Log

Selection snapshot: 2026-08-08

Ordering: GitHub repository search, `sort=stars`, `order=desc`

Eligibility was checked without inspecting tool annotations.

## Recorded queries and selections

| Stratum | Exact query | Selected rank | Repository |
|---|---|---:|---|
| filesystem | `mcp filesystem in:name,description fork:false archived:false` | 1 | `mark3labs/mcp-filesystem-server` |
| relational database | `mcp postgres in:name,description fork:false archived:false` | 1 | `prest/prest` |
| GitHub/developer workflow | `github mcp in:name,description fork:false archived:false` | 1 | `github/github-mcp-server` |
| browser automation | `playwright mcp in:name,description fork:false archived:false` | 1 | `microsoft/playwright-mcp` |
| web/HTTP retrieval | `fetch mcp in:name,description fork:false archived:false` | 1 | `KnockOutEZ/wigolo` |
| communication | `slack mcp in:name,description fork:false archived:false` | 4 | `korotovsky/slack-mcp-server` |
| cloud infrastructure | `aws mcp in:name,description fork:false archived:false` | 2 | `awslabs/mcp` |
| productivity | `notion mcp in:name,description fork:false archived:false` | 1 | `makenotion/notion-mcp-server` |
| cache/search/data store | `redis mcp in:name,description fork:false archived:false` | 1 | `t8y2/dbx` |
| reference/general-purpose | `model context protocol servers in:name,description fork:false archived:false` | 1 | `modelcontextprotocol/servers` |

Communication ranks 1–3 were rejected before annotation inspection:

1. `sansan0/TrendRadar`: a trend-monitoring application that can push to
   Slack and supports MCP, not primarily a Slack/communication MCP server.
2. `PostHog/posthog`: a product analytics platform with Slack and MCP access,
   not primarily a communication MCP server.
3. `OpenCoworkAI/open-cowork`: an AI desktop/client application with MCP and
   Slack integration, not an implemented Slack MCP server as its primary role.

Cloud rank 1, `danny-avila/LibreChat`, was rejected because it is primarily an
MCP-capable chat client/application, not an AWS infrastructure MCP server.

## Frozen repository snapshots

Popularity is stars/forks at selection time. Activity is the pinned HEAD commit
date. Counts are approximate and will naturally change after the snapshot.

| Stratum | Repository | Popularity | Language | Activity | Pinned commit | License | Selection rationale |
|---|---|---:|---|---|---|---|---|
| filesystem | [mark3labs/mcp-filesystem-server](https://github.com/mark3labs/mcp-filesystem-server) | 675 / 109 | Go | 2025-11-23 | `ba3f07f22c309d932fa9b1cebe1eb7c55fcbb83b` | MIT | Highest-starred eligible dedicated filesystem MCP server. |
| relational database | [prest/prest](https://github.com/prest/prest) | 4,610 / 315 | Go | 2026-07-30 | `786d775439c29c2fa9afe401df755981da387b8d` | MIT | Highest-starred eligible PostgreSQL project explicitly shipping an MCP server. |
| GitHub/developer workflow | [github/github-mcp-server](https://github.com/github/github-mcp-server) | 32,040 / 4,750 | Go | 2026-08-07 | `eb4c099e05ef622445e930b18682a0464f22418f` | MIT | Highest-starred eligible result and official GitHub MCP server. |
| browser automation | [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) | 35,904 / 2,994 | TypeScript | 2026-08-07 | `7e0457a7cbf88823bf0146d12c46ae12c6818247` | Apache-2.0 | Highest-starred eligible dedicated Playwright MCP server. |
| web/HTTP retrieval | [KnockOutEZ/wigolo](https://github.com/KnockOutEZ/wigolo) | 4,407 / 314 | TypeScript | 2026-08-01 | `b3ccf92be3ac15ce3ad5a439be11777d992996a3` | AGPL-3.0 | Highest-starred eligible web search/fetch/crawl MCP server. |
| communication | [korotovsky/slack-mcp-server](https://github.com/korotovsky/slack-mcp-server) | 1,770 / 350 | Go | 2026-05-15 | `b88c0de3f706f4f07337c9eda7133c736d1c9524` | MIT | First eligible dedicated Slack server after three stratum mismatches. |
| cloud infrastructure | [awslabs/mcp](https://github.com/awslabs/mcp) | 9,573 / 1,700 | Python | 2026-08-07 | `7ad53dc06ff7999235ab5addbbbb98042718c33a` | Apache-2.0 | First eligible AWS MCP server collection after excluding an MCP client. |
| productivity | [makenotion/notion-mcp-server](https://github.com/makenotion/notion-mcp-server) | 4,579 / 614 | TypeScript | 2026-07-25 | `1d38420769c8a1fe2d583ff1e7d2d108d4eb0b30` | MIT | Highest-starred eligible dedicated Notion MCP server. |
| cache/search/data store | [t8y2/dbx](https://github.com/t8y2/dbx) | 13,683 / 1,405 | Rust | 2026-08-08 | `28b34918436f4901124304b8df8ac694234e9bc2` | Apache-2.0 | Highest-starred eligible data-store project with a built-in MCP server. |
| reference/general-purpose | [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | 89,337 / 11,404 | TypeScript/Python | 2026-07-29 | `76d64c822f5125032f89eb71dbdb94e42b434821` | Apache-2.0/MIT transition | Highest-starred eligible reference-server collection; SDK and registry results would have been excluded. |

No selected repository will be replaced because of extraction difficulty or
annotation outcomes.
