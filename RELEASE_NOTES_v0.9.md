# FitzSight v0.9.0 Release Notes

**Date:** 2026-08-11  
**Theme:** Runtime resilience + competition submission completion

## Added

- pure/testable UI presenter for verified KPI cards, charts, trace and Evidence cards;
- five-workflow self-contained offline HTML demo;
- deterministic H.264 MP4 backup demo generated from verified Agent outputs;
- runtime doctor;
- Streamlit live-runtime validator;
- OpenAI live-planner validator;
- OpenAI Responses telemetry for response/model/token/latency metadata;
- deterministic latency measurement;
- portal-copy, rehearsal and demo-video-script assets;
- convenience initial-round upload bundle;
- expanded submission preflight;
- v0.9 benchmark/adversarial result snapshots.

## Corrected

The active pitch deck and speaker notes no longer depend on stale fixed numeric constants. `scripts/build_pitch_deck.py` now runs the current verified deterministic FitzSight workflows in a temporary dataset and uses those results for Slides 4-8. Active README, project-summary, Customer Intelligence and pitch-content numbers were synchronized to the same current fixed-seed benchmark.

Current net-deposit snapshot: `-$187.8k` net change, `+$59.2k` deposits, `+$246.9k` withdrawals, `91.6%` top-11 withdrawal share. Current Customer Intelligence snapshot: `3.7%` High Value customers and `53.7%` deposit share.

## External runtime boundary

DuckDB remains previously validated in the deployment environment. Streamlit and OpenAI live paths remain pending until actual runtime output is supplied; code/tests/offline artifacts do not substitute for that evidence.
