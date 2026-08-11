# FitzSight Implementation Status

**Version:** v0.9.0  
**Date:** 2026-08-11  
**Phase:** Runtime + submission completion layer; five-intent analytical core frozen for the initial round

## Analytical core

Supported Agent intents remain:

1. `crm_routing_ftd_investigation`
2. `net_deposit_anomaly_investigation`
3. `customer_intelligence_segmentation`
4. `marketing_lead_quality_investigation`
5. `false_correlation_guardrail_investigation`

The trust boundary is unchanged:

```text
Question
→ local approved-intent gate
→ constrained planner
→ deterministic SQL/Python tools
→ Evidence Registry
→ EvidenceClaimVerifier
→ verified / withheld answer
```

## v0.9 completed

- [x] pure presentation layer under `src/fitzsight/ui/` for KPI cards, charts, trace rows and Evidence cards;
- [x] Streamlit renderer consumes verified presentation data instead of owning business calculations;
- [x] five-workflow offline HTML demo generated from actual verified Agent runs;
- [x] deterministic 1280x720 H.264 MP4 backup video generated from verified offline-demo data;
- [x] runtime doctor for Python/dependency/data/presentation readiness without secret disclosure;
- [x] explicit Streamlit health-check validation command;
- [x] explicit OpenAI live-planner validation command;
- [x] OpenAI Responses planner telemetry for response/model/token/latency metadata with `store=False`;
- [x] deterministic end-to-end latency measurement across five workflows;
- [x] initial-round portal-copy and timed rehearsal assets;
- [x] convenience upload bundle with manifest/checksums;
- [x] submission preflight expanded for offline demo/video/runtime assets;
- [x] competition-facing deck metrics generated from fresh verified Agent runs rather than stale constants;
- [x] current README/project-summary/customer/pitch content synchronized to the current fixed-seed benchmark.

## Current verified synthetic result snapshot

```text
CRM / FTD
  affected:          -7.53 pp
  control:           -1.21 pp
  response median:  +29.15 min

Net deposits
  net change:       -$187.8k
  deposits:          +$59.2k
  withdrawals:      +$246.9k
  top-11 share:       91.6%

Customer Intelligence
  Europe customers:   6,770
  High Value users:     3.7%
  High Value deposits:  53.7%

Marketing quality
  leads:              +315%
  FTD:              -10.84 pp
  Paid Search FTD:  -16.44 pp

False correlation
  Asia FTD:          -8.13 pp
  Affiliate FTD:    -15.81 pp
  nearby office event supported as cause: false
```

## Evaluation state

```text
5 / 5 deterministic scenarios PASS
root-cause scenario accuracy:         100%
false-correlation rejection accuracy: 100%
mean evidence coverage:               100%
verifier violations:                  0

8 / 8 adversarial cases PASS
```

Build-environment deterministic latency measurement (SQLite, 15 verified runs):

```text
overall mean: 292.29 ms
p50:          300.90 ms
p95:          343.35 ms
```

This latency snapshot is environment-specific and excludes live model-provider latency/cost.

## External runtime state

### Done

- DuckDB deployment runtime with `data/generated`;
- constrained planner on DuckDB;
- JSON-file planner on DuckDB.

### Still pending live evidence

- OpenAI Responses API with real credentials/model;
- Streamlit runtime smoke test on the final demo environment.

## Remaining user-controlled competition work

1. run Streamlit live validation on the final presentation machine;
2. optionally run the OpenAI live planner if stable credentials/model access are available;
3. upload the final project introduction + PPT/PDF (+ optional video);
4. capture portal/email confirmation evidence;
5. copy live/local/video assets to a second location;
6. perform a timed 5-8 minute pitch and <3 minute demo rehearsal.
