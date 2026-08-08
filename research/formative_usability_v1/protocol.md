# Formative usability protocol

Status: **FROZEN BEFORE PARTICIPANT TESTING**

Protocol version: `formative-usability-v1`

Freeze timestamp: `2026-08-08T20:52:51+09:00`

Product under test: `mcp-annotation-audit` commit
`db7e8693836f394d9b2cc646236b38ea0203a2c1`

MCP schema interpretation: `2025-11-25`

## Purpose and product hypothesis

This study looks for major usability or comprehension failures before a
12-person confirmatory study. It is deliberately formative and descriptive;
it must not be reported as a powered hypothesis test.

Frozen product hypothesis:

> MCP developers can understand explicit annotations, effective defaults,
> applicability, and fields deserving source review more accurately and
> efficiently using `mcp-annotation-audit` than by inspecting raw MCP Tool
> definitions alone.

The comparison is:

- **A — Raw JSON:** annotation-relevant raw MCP Tool objects.
- **B — Audit report:** the unedited human-readable output produced by the
  frozen CLI from the same raw objects.

## Participants

Recruit 3–5 developers; target 4 so all counterbalancing sequences are filled.
A valid participant must:

- write or review software at least monthly;
- be comfortable reading JSON and command-line output;
- have worked with an API, tool schema, or developer protocol in the last
  year; and
- not have designed, implemented, or participated in prior evaluation of this
  repository.

Prior MCP experience is recorded but not required. Aim for at least two
participants who have built or integrated an MCP server/client when the pool
permits. Do not recruit annotation experts exclusively. Record only coarse
experience bands; do not commit names, employers, contact details, recordings,
or other identifying information to the repository.

A session is invalid if the participant fails an eligibility rule, has already
seen an answer key or both representations of a case set, uses outside source
code during a scored block, or experiences a disruption that prevents timing.
Replace invalid sessions up to the five-valid-participant maximum and document
the exclusion without scoring it.

## Design

Use a within-subject crossover. Every participant completes one set in A and
the other set in B, so nobody sees the same Tool in both representations.
Assign valid participants to the next sequence slot in enrollment order:

| Slot | Block 1 | Block 2 |
|---|---|---|
| S1 | A / Set X | B / Set Y |
| S2 | B / Set X | A / Set Y |
| S3 | A / Set Y | B / Set X |
| S4 | B / Set Y | A / Set X |
| S5 | A / Set X | B / Set Y |

The sets are position-matched by explicit-annotation pattern. Each has one
case with 1 expected review field, one with 3, one with 4, and one with 0.
Each also has two cases where effective `readOnlyHint=true`, making
`destructiveHint` and `idempotentHint` inapplicable. The set totals are
identical: 12 applicable fields, 4 explicit applicable fields, and 8 expected
review fields.

The raw stimuli are annotation-relevant subsets of real Tool inventories
captured at pinned upstream commits. Input schemas were not retained in the
frozen research inventory and are intentionally absent in both sets; names,
descriptions, and advertised annotations are unchanged. The audit reports are
generated from those exact subsets. This controlled elision is a limitation
to carry into the confirmatory-study design.

## Measures

Collect these measures separately for A and B:

- overall correctness across frozen binary-scored responses;
- task completion count and elapsed time per case and block;
- explicit-versus-default origin errors;
- effective-value errors;
- applicability errors;
- source-review precision, recall, and F1;
- any claim that an omission establishes a vulnerability;
- confidence on a 1–5 scale after each case; and
- think-aloud observations, post-condition feedback, and exit-interview themes.

Do not infer actual implementation behavior from a name or description. The
scored source-review decision is only whether a field is omitted and
applicable, not whether source inspection would ultimately find the default
precise or imprecise.

## Materials and blinding

Participants may see only the files listed in the README disclosure section.
The reference card is available in both conditions. Keep the answer key,
evaluation rules, alternate representation, and historical source-audit
classifications hidden until both blocks and all scored questions are complete.

The moderator may know the answers but must not score aloud, correct an answer,
explain report terminology, or teach annotation semantics during a block.
A second person should score de-identified responses when practical. If the
moderator is also the scorer, score only after the session ends.

## Session procedure (45–60 minutes)

1. **Eligibility and consent — 5 minutes.** Confirm the criteria, explain that
   the artifact—not the participant—is being evaluated, and obtain consent for
   written notes. Recording requires separate consent and storage outside this
   repository.
2. **Neutral orientation — 5 minutes.** Provide the participant instructions,
   reference card, and response format. Answer procedural questions only. Do
   not demonstrate either scored case set or disclose the hypothesis direction.
3. **Block 1 — at most 20 minutes.** Reveal only the assigned artifact. Start
   the block timer when it is visible. Start and stop a case timer at the
   participant's first view and final answer. Encourage think-aloud without
   prompting toward an answer. Stop at 20 minutes and mark remaining items
   incomplete.
4. **Post-condition questions — 3 minutes.** Ask the frozen questions in the
   observation template. Give no correctness feedback.
5. **Break and representation switch — 2 minutes.** Remove Block 1 materials,
   provide the other set and representation, and allow up to one minute to
   inspect its layout. Do not explain its meaning.
6. **Block 2 — at most 20 minutes.** Repeat the same procedure.
7. **Post-condition and exit interview — 5–10 minutes.** Ask all frozen probes,
   then stop timing. Only after every scored response is locked may the
   moderator debrief or discuss expected answers.

The moderator may say, “Please use the artifact and reference card; answer as
you would in practice.” No other semantic help is permitted. Record every
request for help and whether it was answered procedurally or declined.

## Product freeze and deviations

Do not change product code, report wording, examples, instructions, tasks,
answers, scoring, or decision thresholds after the first valid participant
starts. Do not patch the product between sessions. Verify `MANIFEST.sha256`
before every session.

If a material problem appears, continue only when doing so is safe and useful;
record it under the frozen protocol. A safety or consent concern ends the
session. Any non-safety wording or product fix waits until all planned valid
sessions are complete and the decision rule is applied. Log unavoidable
deviations verbatim and exclude an affected session only under the invalidation
rules above—not because its result is unfavorable.

## Analysis and reporting

Lock each session record before examining aggregate results. After the final
valid session, apply `evaluation_rules.md` without changing thresholds. Report
participant-level paired results and pooled error counts; do not report
p-values, ecosystem prevalence, or generalize beyond this formative sample.

The final experiment conclusion must be exactly one of:

- `READY_FOR_CONFIRMATORY_STUDY`
- `NEEDS_SMALL_USABILITY_FIXES`
- `NEEDS_MAJOR_RETHINK`
- `STOP`

If fixes are selected, describe only the minimum changes directly supported by
participant evidence, following the constraint in the frozen evaluation rules.
