# Formative usability results template

Copy this file to `results.md` after the final valid session. Do not edit this
frozen template. Replace every placeholder, retain excluded-session and
deviation records, and apply `evaluation_rules.md` without changing thresholds.

## Study integrity

| Item | Result |
|---|---|
| Valid participants (`3`–`5`) | `<n>` |
| Invalid/excluded sessions | `<count and frozen reasons>` |
| Sequence slots completed | `<slots>` |
| First / last session timestamp | `<timestamps>` |
| Manifest passed before every session | `<yes/no; details>` |
| Product or material changes during sessions | `<none or deviation>` |

## Participant-level paired measures

| Participant | Sequence | A correct / 68 | B correct / 68 | Delta pp | A seconds | B seconds | B/A ratio | A complete | B complete | A confidence | B confidence | A vulnerability errors | B vulnerability errors |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `<ID>` | `<S#>` |  |  |  |  |  |  |  |  |  |  |  |  |

Median paired accuracy delta: `<value>` percentage points

Median paired time ratio: `<value>`

## Pooled measures

| Measure | A raw JSON | B audit report |
|---|---:|---:|
| Overall correctness |  |  |
| Origin error rate |  |  |
| Effective-value error rate |  |  |
| Applicability error rate |  |  |
| Source-review precision |  |  |
| Source-review recall |  |  |
| Source-review F1 |  |  |
| Vulnerability-error responses |  |  |
| Participants with a vulnerability error |  |  |
| Completed cases / possible |  |  |
| Median participant confidence |  |  |

## Qualitative findings

| Issue ID | Severity | Participants | Condition(s) | Evidence: behavior, quote, or error | Interpretation |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

Summarize preferences and suggestions separately from observed issues. Do not
count repeated comments from one participant as recurrence.

## Decision-gate audit

| Ordered gate | Matched? | Evidence |
|---|:---:|---|
| `STOP` |  |  |
| `READY_FOR_CONFIRMATORY_STUDY` |  |  |
| `NEEDS_SMALL_USABILITY_FIXES` |  |  |
| `NEEDS_MAJOR_RETHINK` fallback |  |  |

## Final decision

`<EXACTLY_ONE_FROZEN_OUTCOME_TOKEN>`

If fixes are required, list only evidence-qualified minimum changes:

| Issue ID | Participant evidence | Minimum change | Why anything larger is unnecessary |
|---|---|---|---|
|  |  |  |  |

If the decision is `READY_FOR_CONFIRMATORY_STUDY` or `STOP`, remove the fixes
table rather than proposing speculative work.
