# FitzSight v0.7.0 Release Notes

**Date:** 2026-08-11

## Theme

**Five-scenario benchmark completion + false-correlation/adversarial evaluation.**

## Added

- `marketing_lead_quality_investigation` Agent intent;
- `false_correlation_guardrail_investigation` Agent intent;
- synthetic Americas paid-media lead-quality shift;
- synthetic Asia nearby-but-unrelated office event / Affiliate deterioration trap;
- channel performance-effect diagnostics;
- explicit event falsification check;
- five-scenario benchmark catalog;
- false-correlation rejection accuracy metric;
- eight-case adversarial release gate;
- UI support for the fourth and fifth workflows;
- benchmark, compliance, and adversarial documentation.

## Benchmark

```text
5 / 5 scenarios PASS
scenario pass rate:                   100%
root-cause scenario accuracy:         100%
false-correlation rejection accuracy: 100%
mean evidence coverage:               100%
verifier violations:                  0
```

## Adversarial evaluation

```text
8 / 8 PASS
scope refusal accuracy:            100%
planner policy catch rate:         100%
verifier integrity catch rate:     100%
causal overclaim catch rate:       100%
ground-truth leak catch rate:      100%
false-correlation rejection rate:  100%
```

## Test validation

```text
Group 1: 25 passed
Group 2: 25 passed, 1 skipped
Aggregate: 50 passed, 1 skipped
compileall: PASS
```

The build-environment skip remains the DuckDB-specific integration test. DuckDB was separately validated in the deployment environment on 2026-08-11.

## Still pending external runtime evidence

- OpenAI Responses live API planner;
- Streamlit runtime smoke test.

## Compatibility

The local approved-intent contract is now plan version `0.7`. Historical v0.6 benchmark/result documents remain in the repository as release evidence.
