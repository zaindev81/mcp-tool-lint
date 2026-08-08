# Scored tasks

Complete these tasks for each Tool in the assigned set, in the order shown in
the artifact. Do not inspect the other set or another representation.

## Task 1 — Origin, value, applicability, and review

Fill one row per annotation:

| Annotation | Origin (`explicit` / `MCP default`) | Effective value (`true` / `false`) | Applicable (`yes` / `no`) | Source review (`yes` / `no`) |
|---|---|---|---|---|
| `readOnlyHint` |  |  |  |  |
| `destructiveHint` |  |  |  |  |
| `idempotentHint` |  |  |  |  |
| `openWorldHint` |  |  |  |  |

Use the frozen source-review rule from the reference card. A review answer is
about whether source inspection is warranted, not what the implementation's
annotation value ultimately should be.

## Task 2 — Omission and vulnerability

Answer `yes` or `no`, then give one sentence of reasoning:

> Based only on this artifact, does an omitted annotation establish that this
> Tool contains a vulnerability?

## Task 3 — Confidence

Rate confidence in the completed case:

- `1` — guessing
- `2` — low confidence
- `3` — moderately confident
- `4` — confident
- `5` — certain

## Task 4 — Source-review actionability (qualitative)

If you selected any source-review fields, name the one you would inspect first
in normal development work and briefly explain why. If you selected none,
write `none`. This item has no correctness score; it is used to evaluate whether
the review decision is actionable and how participants prioritize it.
