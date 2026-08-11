# FitzSight v0.6.0 Release Notes

Date: 2026-08-11

## Headline

**Three-intent Financial Operations Agent + deterministic Customer Intelligence.**

v0.6 expands FitzSight without weakening the core safety model: every supported intent still has a fixed high-level action contract, deterministic execution, evidence-linked claims, and fail-closed verification.

## Added

- `customer_intelligence_segmentation` Agent intent;
- `CustomerSegmentationTool`;
- transparent `behavioral_value_score_v1` segmentation;
- segment deposit / withdrawal / net-deposit / trading profiles;
- customer-intelligence deterministic investigation engine;
- third benchmark scenario;
- compact SQL evidence preview/digest mode for large customer feature queries;
- benchmark scenario pass rate;
- root-cause scenario accuracy;
- evidence-coverage metric;
- verifier-violation metric;
- deterministic latency measurement;
- third Streamlit preset;
- business KPI cards in UI code;
- intent-specific verified charts in UI code;
- plan trace table and evidence-card UI code;
- formal `INITIAL_ROUND_PROJECT_SUMMARY.md`;
- formal `PITCH_DECK_CONTENT.md` source content;
- MIT `LICENSE`;
- `THIRD_PARTY_NOTICES.md`;
- v0.6 validation and benchmark artifacts.

## Validation

```text
46 passed, 1 skipped
compileall PASS
3 / 3 deterministic benchmark scenarios PASS
mean evidence coverage 100%
verifier violations 0
```

The build-environment skip is DuckDB-specific. Separate deployment evidence has already validated DuckDB with both the default constrained planner and JSON-file planner.

## Customer Intelligence default benchmark

```text
Europe customers:           6,770
High Value customers:         278 (4.1%)
High Value deposit share:    55.8%
High Value withdrawal share: 61.0%
verification:                5/5 PASS
```

## Safety boundary

Customer segments are descriptive analytics only. FitzSight does not use them for automated credit, AML, suitability, eligibility, account restriction, customer contact, or adverse-action decisions.

## Still pending

- live OpenAI Responses API runtime validation;
- Streamlit runtime smoke test;
- expansion from 3 to the planned 5 benchmark scenarios;
- final PPT/PDF artifact and demo recording;
- production data connectors/authentication.
