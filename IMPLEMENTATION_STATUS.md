# FitzSight Implementation Status

**Version:** v0.4.0  
**Date:** 2026-08-11  
**Phase:** Constrained Agent MVP implemented above deterministic evidence-first tools.

## v0.4 completed

- [x] v0.3 contribution and anomaly diagnostic tools retained
- [x] constrained intent/planning contract
- [x] deterministic no-API planner fallback
- [x] provider-neutral structured LLM planner adapter
- [x] strict approved action sequence
- [x] unsupported-question refusal before external planner call
- [x] planner SQL/tool-argument prohibition
- [x] Agent orchestration layer
- [x] EvidenceClaimVerifier
- [x] evidence existence, digest and success-status verification
- [x] evaluation-only `_gt` SQL boundary verification
- [x] causal-overclaim verification
- [x] fail-closed final answer rendering
- [x] planning/verifier/final-answer audit records
- [x] Agent CLI
- [x] structured plan example
- [x] expanded tests and documentation

## Important architecture boundary

```text
Planner / future LLM
    ↓ approved high-level actions only
Deterministic tools
    ↓
Evidence Registry
    ↓
Verifier
    ↓
Final answer
```

An LLM is not a calculator and does not receive unrestricted SQL execution authority.

## Still pending

- DuckDB runtime validation in an environment with `duckdb` installed;
- customer segmentation (P1);
- a concrete external model-provider adapter and credentials;
- multi-intent planning;
- Streamlit UI;
- final license;
- competition submission assets.
