# FitzSight Repository Manifest

**Version:** v0.6.0  
**Date:** 2026-08-11  
**Verified source baseline:** `AplusNeutrino/FitzSight` main commit `c8e751b2e7afe68f7d96837bbeffbebd4e957fd2` (`Release FitzSight v0.5.0`)

This manifest records the v0.6.0 delivery snapshot. Generated synthetic benchmark CSV files are intentionally excluded; only `data/generated/.gitkeep` is shipped. The application regenerates deterministic synthetic data when required.

## Key v0.6 additions

- `src/fitzsight/tools/segmentation.py` — transparent behavioral-value Customer Segmentation Tool
- `src/fitzsight/investigation/customer_intelligence.py` — third deterministic investigation engine
- `src/fitzsight/agent/catalog.py` — three approved Agent intents
- `src/fitzsight/investigation/router.py` — three-intent deterministic router
- `src/fitzsight/tools/sql.py` — compact evidence preview/digest mode for large bounded queries
- `streamlit_app.py` — three demo presets + KPI cards + verified charts + plan trace + Evidence cards
- `evaluation/benchmark_catalog.json` — three-scenario benchmark catalog
- `scripts/run_benchmark.py` — scenario pass / root-cause / evidence / verifier / latency metrics
- `examples/valid_customer_intelligence_plan.json` — third structured-plan example
- `docs/CUSTOMER_INTELLIGENCE.md`
- `docs/INITIAL_ROUND_PROJECT_SUMMARY.md`
- `docs/PITCH_DECK_CONTENT.md`
- `docs/V0.6_VALIDATION.md`
- `docs/V0.6_BENCHMARK_RESULTS.json`
- `docs/V0.6_SAMPLE_CUSTOMER_INTELLIGENCE.json`
- `LICENSE` — MIT
- `THIRD_PARTY_NOTICES.md`
- v0.6 automated tests

## Validation evidence

```text
Test group 1: 25 passed
Test group 2: 21 passed, 1 skipped
Aggregate:    46 passed, 1 skipped
compileall:   PASS
benchmark:    3 / 3 PASS
```

The single build-environment skip is the DuckDB-specific test because the build sandbox lacks DuckDB. Separate deployment evidence has already validated the DuckDB runtime using `data/generated`, with both the default constrained planner and JSON-file planner reaching final status `verified`.

## External runtime state

Still requiring separate real runtime evidence:

- OpenAI Responses live API planner
- Streamlit runtime smoke test

## Delivery integrity

`SHA256SUMS.txt` contains a SHA-256 checksum for every shipped repository file except itself.
