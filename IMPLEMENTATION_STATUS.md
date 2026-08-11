# FitzSight Implementation Status

**Version:** v0.6.0  
**Date:** 2026-08-11  
**Phase:** Three-intent Agent + deterministic Customer Intelligence + initial-round materials

## Supported Agent intents

1. `crm_routing_ftd_investigation`
2. `net_deposit_anomaly_investigation`
3. `customer_intelligence_segmentation`

All three retain the same architecture boundary:

```text
Question
→ local approved-intent gate
→ constrained plan
→ deterministic tools
→ Evidence Registry
→ EvidenceClaimVerifier
→ verified / withheld answer
```

## v0.6 completed

- [x] deterministic behavioral customer segmentation;
- [x] third approved Agent intent;
- [x] complete customer-intelligence investigation loop;
- [x] no `*_gt` usage in normal segmentation SQL;
- [x] three-scenario benchmark catalog;
- [x] compact SQL evidence preview/digest mode for large segmentation feature queries;
- [x] root-cause scenario accuracy metric;
- [x] evidence-coverage metric;
- [x] verifier-violation / overclaim metric;
- [x] deterministic latency measurement;
- [x] UI code for business KPI cards;
- [x] UI code for intent-specific charts;
- [x] UI code for plan trace and evidence cards;
- [x] formal initial-round Project Summary;
- [x] pitch-deck content source draft;
- [x] MIT License and third-party notice;
- [x] v0.6 docs and tests.

## Validation

```text
Group 1: 24 passed
Group 2: 21 passed, 1 skipped
Aggregate: 46 passed, 1 skipped
compileall: PASS
```

Three-scenario benchmark:

```text
3 passed / 0 failed
scenario pass rate:           100%
root-cause scenario accuracy: 100%
mean evidence coverage:       100%
verifier violations:          0
```

Customer Intelligence:

```text
European customers:          6,770
segments:                     4
coverage:                     100%
High Value customer share:    4.1%
High Value deposit share:    55.8%
verification:                 5/5 PASS
```

## External runtime state

### Done

- DuckDB deployment runtime: verified with `data/generated`;
- default constrained planner on DuckDB: verified;
- JSON-file planner on DuckDB: verified.

### Still pending live evidence

- OpenAI Responses API with real credentials/model;
- Streamlit runtime smoke test.

## Next implementation priority

1. validate Streamlit runtime and improve the demo based on actual rendering;
2. validate live OpenAI planner if credentials/model access are available;
3. add benchmark scenarios 4 and 5;
4. turn pitch-deck source content into the final PPT/PDF artifact;
5. record demo video and prepare submission package;
6. continue adversarial/overclaim benchmark coverage.
