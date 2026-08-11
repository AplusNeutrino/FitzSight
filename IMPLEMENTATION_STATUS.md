# FitzSight Implementation Status

**Version:** v0.2.0  
**Date:** 2026-08-11  
**Phase:** Deterministic Tool Layer complete in build environment; DuckDB runtime validation pending on an environment where the dependency is installed.

## v0.2 completed in this delivery

- [x] Formal product naming normalized to **FitzSight** across the implementation snapshot
- [x] Python import package moved to `src/fitzsight`
- [x] Project metadata renamed to `fitzsight`
- [x] Synthetic-data generator preserved and revalidated
- [x] AnalyticsStore abstraction
- [x] Preferred DuckDB backend implementation
- [x] SQLite offline/restricted-environment fallback
- [x] Schema Inspector Tool
- [x] Read-only SQL safety validator
- [x] Bounded SQL execution with success/error evidence
- [x] Canonical KPI Tool
- [x] Period Comparison Tool
- [x] Two-proportion statistical test + 95% difference CI
- [x] Mann–Whitney U and Welch t-test support
- [x] Evidence Registry expanded with result payload, digest, status and lookup
- [x] Evidence IDs integrated into v0.2 Tool executions
- [x] Deterministic investigation plan and engine
- [x] Claim-to-evidence mapping
- [x] Causal-language guardrail
- [x] Architecture and Tool Layer documentation
- [x] README with explicit limitations
- [x] New automated tests

## Validation completed in the build environment

```text
pytest -q
17 passed, 1 skipped
```

The single skipped test is the DuckDB-specific backend integration test because the build environment does not have the `duckdb` package installed and cannot install packages from the internet. The same analytical workflow was executed end-to-end using the explicit SQLite fallback.

Additional validation:

```text
python -m compileall -q src scripts tests
PASS
```

Deterministic investigation (SQLite fallback):

```text
Affected FTD:        23.37% -> 15.84%
Affected change:     -7.53 pp
Control change:      -1.21 pp
Response median:     +29.15 min
Conversion p-value:  0.002346
Response p-value:    1.86e-17
Root-cause status:   supported_candidate
Evidence records:    6
Claims:              4
```

## Verification still required after deployment

Run in an internet-enabled local/GitHub environment:

```bash
pip install -e ".[dev]"
pytest -q
python scripts/investigate.py --backend duckdb
```

Expected: the DuckDB backend test should no longer skip and the investigation should recover the same benchmark pattern.

## Still not implemented

- general contribution-analysis Tool;
- generic anomaly-detection Tool;
- customer segmentation;
- LLM planner/orchestrator;
- verifier Agent layer;
- Streamlit UI;
- multi-scenario evaluation harness;
- final project license.

## Next implementation priority

Once DuckDB runtime validation is confirmed, proceed to the remaining pre-Agent analytical capabilities, then introduce the LLM only above the deterministic v0.2 Tool contracts.
