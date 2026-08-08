# Session observation template

Copy this file once per participant. Keep the frozen original unchanged. Use a
non-identifying ID such as `P01`; do not record names or employers here.

## Session metadata

| Field | Value |
|---|---|
| Participant ID |  |
| Date / timezone |  |
| Moderator |  |
| Sequence slot (`S1`–`S5`) |  |
| Valid session (`yes` / `no`) |  |
| If invalid, frozen exclusion reason |  |
| Software work (`monthly+`) |  |
| JSON / CLI comfort (`low` / `medium` / `high`) |  |
| API or protocol work in last year (`yes` / `no`) |  |
| MCP experience (`none` / `used` / `built or integrated`) |  |
| Prior repository involvement (`yes` / `no`) |  |
| Notes consent obtained (`yes` / `no`) |  |
| Manifest verified (`yes` / `no`) |  |

## Block record

Copy this section for each block.

| Field | Value |
|---|---|
| Block (`1` / `2`) |  |
| Condition (`A raw` / `B report`) |  |
| Set (`X` / `Y`) |  |
| Block start timestamp |  |
| Block end timestamp |  |
| Elapsed seconds, capped at 1200 |  |
| Cases completed (`0`–`4`) |  |
| Outside help or disruption |  |

### Case record

Copy this subsection four times per block.

| Field | Value |
|---|---|
| Case ID and Tool |  |
| Start timestamp |  |
| End timestamp |  |
| Elapsed seconds |  |
| Completed before cap (`yes` / `no`) |  |

| Annotation | Origin response | Effective value | Applicable | Source review |
|---|---|---|---|---|
| `readOnlyHint` |  |  |  |  |
| `destructiveHint` |  |  |  |  |
| `idempotentHint` |  |  |  |  |
| `openWorldHint` |  |  |  |  |

| Case-level response | Value |
|---|---|
| Omission establishes vulnerability (`yes` / `no`) |  |
| One-sentence rationale (verbatim) |  |
| Confidence (`1`–`5`) |  |
| First source-review field, or `none` |  |
| Prioritization reason (verbatim) |  |

Think-aloud and behavior notes (timestamp where practical):

- first place looked:
- hesitations or backtracking:
- explicit/default language used:
- applicability reasoning:
- source-review interpretation:
- security/vulnerability language:
- reference-card use:
- notable quote:

### Post-condition questions

Ask verbatim after the block and before any correctness feedback.

1. What was easiest and hardest about this artifact?
2. Which answers felt directly stated, and which did you have to derive?
3. In your own words, what does a “manual review field” or “source-review
   candidate” mean?
4. What, if anything, would you do next after seeing these results?
5. Did any wording imply an error, severity, security problem, or vulnerability?
6. What single change would make this artifact clearer or faster to use?

Verbatim responses and observations:

-

## Exit interview

Ask after both blocks and before debriefing.

1. Which representation would you choose for an annotation review, and why?
2. Did `explicit`, `MCP default`, `applicable`, and `manual review` mean what
   you expected? Identify any term that did not.
3. When is source inspection warranted, based on the materials you saw?
4. Does omission alone say anything conclusive about a vulnerability? Explain.
5. What information was missing, redundant, or distracting?
6. Is there any reason you would not use the report in real development work?

Verbatim responses and observations:

-

## Moderator help and deviations

| Timestamp | Participant request or event | Moderator response | Procedural only? | Deviation / validity impact |
|---|---|---|:---:|---|
|  |  |  |  |  |

## Usability issue log

Use frozen severity definitions from `evaluation_rules.md`. One observation may
support more than one issue, but do not merge unlike causes merely to reach an
evidence threshold.

| Issue ID | Condition / case | Observed behavior or quote | Associated scored error | Severity | Reproducible? | Candidate minimum fix (after study only) |
|---|---|---|---|---|:---:|---|
|  |  |  |  |  |  |  |
