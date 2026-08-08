# Formative usability study v1

Status: **FROZEN BEFORE PARTICIPANT TESTING**

Freeze timestamp: `2026-08-08T20:52:51+09:00`

Product under test: `mcp-annotation-audit` at commit
`db7e8693836f394d9b2cc646236b38ea0203a2c1`

This directory contains the complete, pre-session package for a 3–5 person
formative usability study comparing raw MCP Tool JSON with the human-readable
`mcp-annotation-audit` report. The study is a usability gate, not the proposed
12-person confirmatory evaluation and not an inferential hypothesis test.

## Frozen package

- `protocol.md`: design, recruitment, counterbalancing, and session procedure
- `participant_instructions.md`: neutral instructions shown to participants
- `reference_card.md`: the common MCP defaults/applicability reference
- `tasks.md`: exact task wording and response format
- `expected_answers.md`: facilitator-only answer key
- `observation_template.md`: copy once per session; never edit this original
- `evaluation_rules.md`: frozen metrics, issue severity, and decision gates
- `results_template.md`: copy to `results.md` after the last valid session
- `stimuli/`: the two matched case sets in both experimental conditions
- `MANIFEST.sha256`: integrity hashes for every frozen artifact except itself

## Disclosure during a session

Give a participant only:

1. `participant_instructions.md`;
2. `reference_card.md`;
3. `tasks.md`;
4. the one stimulus assigned for the current block; and
5. a blank copy of the response tables in `observation_template.md`.

Do not reveal the other representation of a set, the other set before its
block, the answer key, the evaluation rules, or prior participants' results.

## Integrity check

From this directory, verify the freeze before every session:

```bash
shasum -a 256 -c MANIFEST.sha256
```

If any hash fails, stop the session. Restore the frozen artifact or record a
protocol deviation before recruiting another participant. Copies containing
participant responses and the eventual `results.md` are data, not frozen
study materials, and must not replace files listed in the manifest.
