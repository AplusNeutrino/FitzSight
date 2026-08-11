# FitzSight Implementation Status

**Version:** v0.5.0  
**Date:** 2026-08-11  
**Phase:** Multi-intent Agent + optional model-provider/UI integration

## v0.5 completed in this delivery

- [x] existing CRM / FTD Agent intent retained
- [x] second financial-operations intent: `net_deposit_anomaly_investigation`
- [x] deterministic high-value withdrawal shock benchmark
- [x] weekly deposit / withdrawal / net-deposit measurement
- [x] exact deposit-vs-withdrawal driver decomposition
- [x] top-customer withdrawal concentration analysis
- [x] regional net-deposit-per-customer control
- [x] multi-intent deterministic router
- [x] intent-specific constrained action catalog
- [x] local scope classifier before provider invocation
- [x] optional OpenAI Responses structured planner provider
- [x] strict JSON-schema provider request
- [x] `store=False` provider request
- [x] provider fake-client integration tests
- [x] minimal Streamlit demo shell
- [x] two-scenario benchmark catalog
- [x] deterministic benchmark runner
- [x] existing EvidenceClaimVerifier retained across both intents
- [x] v0.5 docs and examples

## Build-environment validation

Test suite is executed in groups because the sandbox has a strict process-time ceiling.

```text
Planner + provider tests:         13 passed
Net-deposit / benchmark tests:     3 passed
Agent + verifier tests:            5 passed
Tool/evidence/statistics tests:   14 passed
Generator/investigation/store:     5 passed, 1 skipped
-----------------------------------------------------
Aggregate:                        40 passed, 1 skipped
```

After the final median-control fix, the affected v0.5 net-deposit tests were re-run and passed.

Collection check:

```text
41 tests collected
```

(40 pass + one DuckDB-specific skip in the grouped build validation; see `docs/V0.5_VALIDATION.md` for exact commands.)

Additional validation:

```text
python -m compileall -q src scripts tests streamlit_app.py
PASS
```

Two-scenario deterministic benchmark:

```text
scenario_count: 2
passed:         2
failed:         0
backend:        sqlite
```

Default-seed net-deposit result:

```text
Baseline net deposits:       $141,733.52
Current net deposits:        -$82,168.18
Net-deposit change:          -$223,901.70
Deposit change:               +$24,365.52
Withdrawal change:           +$248,267.22
Top-11 withdrawal share:      92.2%
Verification:                 5/5 PASS
```

## Runtime validation still pending outside this build environment

- [ ] DuckDB-specific backend integration with actual `duckdb`
- [ ] live OpenAI API call with user credentials/model access
- [ ] Streamlit runtime smoke test with optional UI dependency
- [ ] final open-source license selection

## Still not implemented

- customer segmentation Agent capability;
- third/fourth/fifth benchmark scenarios;
- production authentication / RBAC;
- final visual design and charts;
- final GOAI PPT/PDF and demo recording;
- production database connectors.

## Next P0/P1 slice

1. validate DuckDB / OpenAI / Streamlit in deployment environment;
2. add Customer Intelligence / segmentation as the next Agent capability;
3. expand benchmark catalog toward five scenarios;
4. add UI business KPI cards and charts;
5. begin initial-round competition deck and demo narrative.
