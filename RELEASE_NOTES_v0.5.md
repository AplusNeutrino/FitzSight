# FitzSight v0.5.0 Release Notes

Date: 2026-08-11

## Theme

**Multi-intent Financial Operations Agent**

v0.5 expands FitzSight beyond the original CRM/FTD benchmark and introduces a second end-to-end financial-operations investigation.

## Added

- `net_deposit_anomaly_investigation`
- synthetic European high-value withdrawal-cluster scenario
- net-deposit driver decomposition
- top-customer withdrawal concentration analysis
- regional control comparison
- `MultiIntentInvestigationEngine`
- intent/action catalog
- optional `OpenAIResponsesPlanner`
- strict Responses API JSON-schema planner boundary
- `store=False` model request
- optional Streamlit demo
- two-scenario benchmark catalog
- benchmark runner
- second structured-plan example
- expanded tests and documentation

## Preserved boundaries

- models do not calculate business metrics;
- models do not generate SQL;
- models cannot select arbitrary tools or parameters;
- unsupported questions fail before provider invocation;
- deterministic planner remains the default fallback;
- EvidenceClaimVerifier remains fail closed;
- synthetic `*_gt` data remains outside the normal Agent query surface.

## Validation

Build environment:

```text
40 passed, 1 skipped
compileall PASS
2/2 benchmark scenarios PASS
```

The skip remains the DuckDB-specific integration test because DuckDB is not installed in the build sandbox.

Live OpenAI and Streamlit runtime validation are intentionally not claimed; those require optional dependencies and user-side credentials/runtime.
