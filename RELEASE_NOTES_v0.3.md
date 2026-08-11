# FitzSight v0.3.0 Release Notes

Date: 2026-08-11

## Goal

v0.3 strengthens the deterministic diagnostic layer before any LLM planner/orchestrator is introduced.

## Added

- `ContributionAnalysisTool`
  - evidence-linked binary-rate decomposition by categorical dimension;
  - separates performance and composition effects;
  - segment contributions reconstruct the aggregate rate change;
- `AnomalyDetectionTool`
  - median/MAD robust baseline;
  - high / low / two-sided modes;
  - deterministic fallback when MAD is zero;
- contribution and anomaly steps integrated into the core CRM-routing investigation;
- two additional evidence-linked claims in the investigation output;
- `docs/DIAGNOSTIC_TOOLS.md`;
- `docs/V0.3_VALIDATION.md`;
- expanded automated tests.

## Validation

```text
pytest -q
19 passed, 1 skipped
```

```text
python -m compileall -q src scripts tests
PASS
```

The only skipped test is still the DuckDB backend integration test because the build environment cannot install the DuckDB dependency. The SQLite fallback executes the complete v0.3 investigation successfully.

## Benchmark highlights

- affected FTD change: about `-7.53 pp`;
- control FTD change: about `-1.21 pp`;
- response median shift: about `+29.15 min`;
- top negative rate-decomposition contributor: `Team A`, followed by `Team B`;
- post-change high response-time anomaly days: `8`;
- contribution reconstruction error: numerical zero within floating-point precision;
- evidence records: `10`;
- claims: `6`.

## Still intentionally absent

- LLM planner/orchestrator;
- autonomous free-form tool selection;
- customer segmentation;
- Streamlit UI;
- multi-scenario benchmark harness;
- final project license.

The next major engineering step is to put a constrained planner/orchestrator above the deterministic tool contracts, without allowing the model to calculate or invent business numbers.
