# FitzSight Implementation Status

**Version:** v0.7.0  
**Date:** 2026-08-11  
**Phase:** Five-intent Agent + five-scenario benchmark + adversarial evaluation

## Supported Agent intents

1. `crm_routing_ftd_investigation`
2. `net_deposit_anomaly_investigation`
3. `customer_intelligence_segmentation`
4. `marketing_lead_quality_investigation`
5. `false_correlation_guardrail_investigation`

Every intent uses the same trust boundary:

```text
Question
→ local approved-intent gate
→ constrained plan
→ deterministic SQL/Python tools
→ Evidence Registry
→ EvidenceClaimVerifier
→ verified / withheld answer
```

## v0.7 completed

- [x] Americas paid-media / lead-quality benchmark;
- [x] Asia false-correlation benchmark;
- [x] fourth and fifth approved Agent intents;
- [x] channel performance-vs-composition diagnostics;
- [x] explicit falsification check for nearby-event attribution;
- [x] five-scenario deterministic benchmark catalog;
- [x] false-correlation rejection accuracy metric;
- [x] eight-case adversarial safety/evidence suite;
- [x] unsupported trade / AML scope-refusal checks;
- [x] planner SQL / high-impact action rejection checks;
- [x] missing-evidence, causal-overclaim and `_gt` leakage checks;
- [x] UI code expanded to five preset workflows;
- [x] benchmark and compliance documentation;
- [x] v0.7 release documentation and tests.

## Build validation

The full suite is executed in groups because the sandbox has a strict single-process time ceiling.

```text
Group 1: 25 passed
Group 2: 25 passed, 1 skipped
Aggregate: 50 passed, 1 skipped
compileall: PASS
```

The single build skip is the DuckDB-specific integration test. DuckDB itself has already been validated separately in the deployment environment on 2026-08-11.

## Five-scenario benchmark

```text
5 passed / 0 failed
scenario pass rate:                  100%
root-cause scenario accuracy:        100%
false-correlation rejection accuracy:100%
mean evidence coverage:              100%
verifier violations:                 0
```

New scenario 4 — Americas acquisition quality:

```text
lead volume:            +838 (+315.0%)
FTD conversion:         -10.84 pp
Paid Search mix:        +60.52 pp
Paid Search conversion: -16.44 pp
Paid Search p-value:    4.43e-05
verification:           4/4 PASS
```

New scenario 5 — false correlation:

```text
Asia conversion:        -8.13 pp
Affiliate conversion:  -15.81 pp
Affiliate p-value:      0.00463
top negative performance channel: Affiliate
nearby office event causal support: false
false correlation rejected: true
verification:           4/4 PASS
```

## Adversarial evaluation

```text
8 / 8 PASS
overall adversarial pass rate:       100%
scope refusal accuracy:              100%
planner policy catch rate:           100%
verifier evidence-integrity catch:   100%
causal-overclaim catch rate:         100%
ground-truth leak catch rate:        100%
false-correlation rejection rate:    100%
```

## External runtime state

### Done

- DuckDB runtime with `data/generated`;
- constrained planner on DuckDB;
- JSON-file planner on DuckDB.

### Still pending live evidence

- OpenAI Responses API with real credentials/model;
- Streamlit runtime smoke test.

## Next implementation priority

1. validate Streamlit runtime and refine the actual rendered demo;
2. validate the live OpenAI planner if model/API access is available;
3. turn the completed pitch-deck content source into the final PPT/PDF artifact;
4. record a short demo video and prepare initial-round submission assets;
5. add one-command startup / local-demo backup;
6. continue latency/cost measurement once a live model provider is validated.
