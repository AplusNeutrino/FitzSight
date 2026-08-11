# FitzSight Implementation Status

**Version:** v0.3.0  
**Date:** 2026-08-11  
**Phase:** Deterministic diagnostic layer expanded; LLM planner/orchestrator not yet introduced.

## v0.3 completed in this delivery

- [x] v0.2 deterministic Tool Layer retained and revalidated
- [x] `ContributionAnalysisTool`
- [x] symmetric binary-rate decomposition by categorical dimension
- [x] performance-effect and composition-effect breakdown
- [x] exact aggregate-change reconstruction within floating-point precision
- [x] `AnomalyDetectionTool`
- [x] median/MAD robust baseline with safe fallbacks
- [x] high / low / two-sided anomaly directions
- [x] team contribution step integrated into the benchmark investigation
- [x] post-change response-time anomaly scan integrated into the benchmark investigation
- [x] six evidence-linked investigation claims
- [x] ten evidence records in the default v0.3 benchmark run
- [x] diagnostic-tool documentation
- [x] expanded automated tests

## Build-environment validation

```text
pytest -q
19 passed, 1 skipped
```

The single skipped test is the DuckDB-specific backend integration test because this build environment cannot install the `duckdb` package. The SQLite fallback executes the full v0.3 deterministic investigation.

```text
python -m compileall -q src scripts tests
PASS
```

Default benchmark output in the build environment:

```text
Affected FTD change:              -7.53 pp
Europe control FTD change:        -1.21 pp
Affected response median change: +29.15 min
Largest negative contributor:     Team A
Second negative contributor:      Team B
Post-change response anomalies:   8 days
Contribution reconstruction err: ~0 pp
Root-cause status:                supported_candidate
Evidence records:                 10
Claims:                           6
```

## Verification still pending

- [ ] DuckDB-specific runtime/integration validation in an environment with `duckdb` installed
- [ ] final open-source license selection

## Still not implemented

- customer segmentation;
- LLM planner/orchestrator;
- autonomous free-form tool selection;
- Verifier Agent layer;
- Streamlit UI;
- multi-scenario evaluation harness;
- final competition submission assets.

## Next P0 implementation slice

1. Introduce a constrained planner/orchestrator contract above deterministic tools.
2. Keep all numeric computation inside SQL/Python tools.
3. Require structured plans and explicit allowed-tool lists.
4. Reject unsupported intents instead of hallucinating workflows.
5. Add deterministic planner fallback so the demo remains usable without model/API access.
6. Add a Verifier layer that checks claims against Evidence IDs before final rendering.

The LLM integration must not bypass read-only SQL, evidence registration, or causal-language guardrails.
