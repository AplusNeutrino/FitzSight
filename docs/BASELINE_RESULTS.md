# Baseline Results — CRM Routing Change

**Version:** v0.1  
**Synthetic seed:** `20260811`  
**Scenario date:** `2026-07-15`

This document records the deterministic baseline result for the first synthetic benchmark scenario. It exists to prove that the injected ground truth is detectable **before** an LLM or autonomous Agent is added.

## Ground truth

Affected cohort:

- Region: Europe
- Teams: Team A + Team B
- Change: CRM routing degradation
- Expected mechanism: response latency increases, then FTD conversion decreases

Control cohort:

- Region: Europe
- Teams other than Team A + Team B

## Result

| Metric | Affected pre | Affected post | Control pre | Control post |
|---|---:|---:|---:|---:|
| Sample size | 2,452 | 322 | 3,483 | 513 |
| FTD conversion | 23.37% | 15.84% | 21.88% | 20.66% |
| Conversion change | — | **-7.53 pp** | — | -1.21 pp |
| Median response time | 94.3 min | **123.45 min** | 93.9 min | 95.8 min |
| Conversion p-value | — | **0.00235** | — | 0.53327 |

## Interpretation

The baseline detects the intended benchmark mechanism:

1. the affected European teams show a material increase in response time after the routing change;
2. their FTD conversion rate falls by approximately 7.53 percentage points;
3. the conversion shift is statistically significant under the current chi-square baseline (`p ≈ 0.00235`);
4. the European control cohort changes much less and is not statistically significant under the same baseline.

This is sufficient for the v0.1 Definition of Done: **the synthetic ground truth can be recovered without an Agent**.

## Important limitation

This is a synthetic benchmark, not a causal study on real financial-company data. The current test establishes that the injected scenario is discoverable. Future versions should improve the analysis with fixed-window comparisons, effect sizes, confidence intervals, robustness checks, and explicit causal-language guardrails.
