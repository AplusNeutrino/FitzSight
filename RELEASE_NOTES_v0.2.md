# FitzSight v0.2.0 Release Notes

**Date:** 2026-08-11

## Purpose

v0.2 adds the deterministic analytical Tool Layer required before introducing an LLM planner/orchestrator.

The release objective is:

> A business question can trigger a real, read-only, evidence-linked investigation in which calculations and statistical results come from deterministic Tools rather than language-model arithmetic.

## Added

- formal **FitzSight** naming throughout the maintained implementation snapshot;
- `src/fitzsight` Python package;
- AnalyticsStore with preferred DuckDB implementation and explicit SQLite fallback;
- Schema Inspector Tool;
- read-only SQL Tool and conservative SQL safety policy;
- KPI Tool;
- Period Comparison Tool;
- statistical test Tool;
- expanded Evidence Registry;
- deterministic investigation data models;
- deterministic European FTD / July 15 investigation engine;
- evidence-linked claims;
- causal-language guardrail;
- architecture / Tool Layer / validation documentation;
- expanded test suite.

## Validation

Build-environment result:

```text
17 passed, 1 skipped
```

The skipped test is DuckDB-specific runtime integration because the build environment cannot install the missing DuckDB package. SQLite fallback integration passed and the full deterministic benchmark investigation recovered the expected pattern.

DuckDB must be revalidated after deployment with:

```bash
pip install -e ".[dev]"
pytest -q
python scripts/investigate.py --backend duckdb
```

## Known limitations

- one deterministic benchmark intent;
- no LLM Agent yet;
- no generic contribution or anomaly Tool yet;
- no UI yet;
- synthetic data only;
- final license decision pending.
