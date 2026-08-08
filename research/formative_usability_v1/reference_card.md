# MCP Tool annotation reference card

Use these rules for every task. An annotation is **explicit** only when its key
appears in the Tool's `annotations` object. If it is absent, its effective value
comes from the MCP default.

| Annotation | Effective default when omitted | Applicability used in this study |
|---|---:|---|
| `readOnlyHint` | `false` | Applicable to every Tool |
| `destructiveHint` | `true` | Applicable when effective `readOnlyHint` is `false`; otherwise not applicable |
| `idempotentHint` | `false` | Applicable when effective `readOnlyHint` is `false`; otherwise not applicable |
| `openWorldHint` | `true` | Applicable to every Tool |

An explicit value overrides its default. An explicit field remains explicit
even when the applicability rule marks it not applicable.

For this study, send a field to source review exactly when both are true:

1. the field is omitted and therefore uses an MCP default; and
2. the field is applicable.
