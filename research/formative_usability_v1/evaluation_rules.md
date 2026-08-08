# Frozen evaluation rules

Status: **FROZEN BEFORE PARTICIPANT TESTING**

Apply these rules only after at least 3 and at most 5 valid participant sessions.
With fewer than 3 valid sessions, the experiment is incomplete and no final
product decision may be issued.

## Response normalization

Accept unambiguous equivalents:

- origin: `explicit` or `MCP default`;
- boolean: `true` or `false`;
- applicability, review, and vulnerability: `yes` or `no`; and
- confidence: integer `1` through `5`.

A blank, unresolved, or contradictory response is incorrect. If the 20-minute
block cap expires, score unanswered correctness items as incorrect, mark the
case incomplete, and use 1200 seconds as block time. Do not reinterpret an
answer from think-aloud comments after the participant locks the case.

## Scored measures

For each condition and participant, score:

1. **Origin correctness:** 16 binary answers (4 fields × 4 Tools).
2. **Effective-value correctness:** 16 binary answers.
3. **Applicability correctness:** 16 binary answers.
4. **Source-review correctness:** 16 binary answers.
5. **Omission/vulnerability correctness:** 4 binary answers.
6. **Overall correctness:** correct answers across the 68 items above.
7. **Completion:** number of fully answered Tool cases, from 0 to 4.
8. **Time:** elapsed seconds per case and block; block time is capped at 1200.
9. **Confidence:** median of the four 1–5 case ratings.

Calculate source-review precision, recall, and F1 from the 16 review choices
per condition, treating `yes` in the answer key as positive:

```text
precision = TP / (TP + FP)
recall    = TP / (TP + FN)
F1        = 2 * precision * recall / (precision + recall)
```

Both sets contain eight positives, so recall is always defined. If there are
no predicted positives, set precision and F1 to 0.

For explicit/default confusion and applicability mistakes, report both the
number of participants with at least one error and the pooled item-error rate.
For vulnerability misconception, report the number of `yes` responses and the
number of participants making at least one such response. Do not soften a
`yes` because its explanation is tentative.

## Paired comparison

Sets X and Y have identical answer structures, so compare A and B within each
participant despite different Tool names. Compute:

```text
accuracy_delta_pp = 100 * (B_correct / 68 - A_correct / 68)
time_ratio        = B_block_seconds / A_block_seconds
```

Report every participant's pair, then the median paired accuracy delta and
median time ratio. Also report pooled A and B measures. Do not discard an
outlier, substitute a mean for the frozen medians, perform a significance test,
or claim the sample estimates a population effect.

Treat an efficiency result as directionally favorable only when either:

- B is at least as accurate and at least 10% faster at the paired median
  (`accuracy_delta_pp >= 0` and `time_ratio <= 0.90`); or
- B is at least 5 percentage points more accurate with no time penalty at the
  paired median (`accuracy_delta_pp >= 5` and `time_ratio <= 1.00`).

## Qualitative coding

Code observations using the participant's behavior or words, not a presumed
cause. Merge observations into one issue only when they describe the same
artifact element and failure mode.

| Severity | Frozen definition |
|---|---|
| `CRITICAL` | The report directly causes or strongly reinforces an unsafe vulnerability conclusion, suppresses an applicable review field, or prompts an action likely to create material harm; the issue is reproducible from the frozen artifact. |
| `MAJOR` | A participant cannot complete a core task, systematically reverses explicit/default or applicability meaning, or cannot form a usable source-review decision without moderator teaching. |
| `MINOR` | A localized label, layout, redundancy, or navigation problem causes delay or an isolated error but leaves the core model recoverable without teaching. |
| `OBSERVATION` | Preference, suggestion, or hesitation with no observed error, material delay, or blocked decision. |

An issue is **recurrent** when the same failure is observed in at least two
independent participants. One reproducible `CRITICAL` or `MAJOR` issue is
actionable even if it occurs once. A preference alone never justifies a fix.

## Ordered final decision

Apply the gates in this order. The first matching outcome is final.

### 1. `STOP`

Choose `STOP` if any one is true:

- at least half of participants (rounded up) make an omission-as-vulnerability
  error in B, the participant count is higher than in A, and the report's
  framing is cited as evidence;
- B is at least 5 percentage points less accurate and at least 10% slower at
  the paired medians, while at least half of participants independently
  describe the report as misleading or unusable; or
- a recurrent `CRITICAL` issue cannot be removed without contradicting the
  product's frozen non-goals or replacing its underlying audit model.

### 2. `READY_FOR_CONFIRMATORY_STUDY`

Choose `READY_FOR_CONFIRMATORY_STUDY` only if all are true:

- every valid participant completes all four B cases;
- pooled B overall correctness is at least 90%, and every participant's B
  correctness is at least 85%;
- pooled B origin-error and applicability-error rates are each at most 5%;
- pooled B source-review F1 is at least 0.90;
- no participant makes an omission-as-vulnerability error in B;
- the paired comparison meets one of the two directionally favorable
  accuracy/efficiency rules above;
- median B confidence is at least 4; and
- there is no actionable `CRITICAL` or `MAJOR` issue and no recurrent `MINOR`
  issue.

Passing this gate means the report is usable enough to evaluate formally. It
does not confirm the product hypothesis.

### 3. `NEEDS_SMALL_USABILITY_FIXES`

Choose `NEEDS_SMALL_USABILITY_FIXES` when the ready gate failed but all of the
following “promising core” conditions hold:

- pooled B correctness is at least 80%;
- pooled B source-review F1 is at least 0.80;
- pooled B origin-error and applicability-error rates are each at most 15%;
- no more than one participant makes any vulnerability error in B;
- at least half of participants complete all B cases;
- B improves either paired-median accuracy or time without a material
  regression in the other (not more than 5 percentage points less accurate
  and not more than 10% slower); and
- every actionable issue can be addressed by a localized wording, ordering,
  formatting, or navigation change without changing the audit data model,
  adding semantic inference, or expanding product scope.

### 4. `NEEDS_MAJOR_RETHINK`

Choose `NEEDS_MAJOR_RETHINK` for every remaining completed study. This includes
a core comprehension failure, lack of directional value, a required data-model
or conceptual change, or any actionable issue too broad for the small-fix rule
that does not meet the stricter `STOP` criteria.

## Minimum-change constraint

If the outcome calls for fixes, propose a change only when supported by either:

- the same observed failure in at least two participants; or
- one reproducible `CRITICAL` or `MAJOR` failure.

For each proposed change, cite the issue ID, affected participant IDs, exact
error or behavior, and the smallest report surface that can correct it. Do not
add behavior inference, automatic annotation recommendations, severity,
vulnerability detection, ranking, or unrelated polish. Prefer one wording or
layout change over a new feature. After any product change, run a fresh 3–5
person formative round with newly frozen materials before the confirmatory
study.
