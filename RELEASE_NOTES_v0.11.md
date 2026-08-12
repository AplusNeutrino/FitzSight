# FitzSight v0.11.0 Release Notes

**Date:** 2026-08-12

v0.11 is a final-machine/operator release. It does not expand the five-intent analytical core and does not automate competition submission.

## Added

- `scripts/final_machine_check.py`
- `scripts/rehearsal_assistant.py`
- `scripts/build_final_machine_kit.py`
- `submission/FitzSight_Final_Machine_Kit.zip`
- `submission/FINAL_MACHINE_CHECKLIST.md`
- `submission/REHEARSAL_OPERATOR_CARD.md`
- `submission/REHEARSAL_PLAN.json`
- `docs/FINAL_MACHINE_OPERATIONS.md`
- `docs/V0.11_FINAL_MACHINE_READINESS.json`
- `docs/V0.11_BENCHMARK_RESULTS.json`
- `docs/V0.11_ADVERSARIAL_RESULTS.json`
- v0.11 final-machine tests

## Final-machine policy

The default final-machine check is local-only except for a localhost Streamlit health probe. It does not call a live model provider unless the user explicitly passes `--include-openai`, and it never opens/submits the competition portal or accesses email/Gmail.

## Validation

```text
79 tests collected
78 passed
1 skipped
compileall PASS

5 / 5 benchmark scenarios PASS
8 / 8 adversarial cases PASS
```

The single build-sandbox skip remains the DuckDB-specific integration test; DuckDB was previously validated in the deployment environment.

## External/manual tasks still open

Streamlit final-machine validation, optional OpenAI live validation, actual competition portal submission/confirmation, and real timed rehearsal remain evidence-gated and are not marked complete by this release.
