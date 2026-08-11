# FitzSight Implementation Status

**Version:** v0.8.0  
**Date:** 2026-08-11  
**Phase:** Initial-round submission sprint — five-intent Agent complete, presentation/demo assets generated

## Supported Agent intents

1. `crm_routing_ftd_investigation`
2. `net_deposit_anomaly_investigation`
3. `customer_intelligence_segmentation`
4. `marketing_lead_quality_investigation`
5. `false_correlation_guardrail_investigation`

Every intent retains the same trust boundary:

```text
Question
→ local approved-intent gate
→ constrained plan
→ deterministic SQL/Python tools
→ Evidence Registry
→ EvidenceClaimVerifier
→ verified / withheld answer
```

## v0.8 completed in this delivery

- [x] v0.7 five-intent Agent, five-scenario benchmark, and adversarial release gate retained;
- [x] one-command competition launcher `scripts/start_demo.py`;
- [x] automatic deterministic CLI fallback when Streamlit is unavailable;
- [x] explicit UI / CLI launcher modes and dry-run support;
- [x] submission preflight checker `scripts/preflight_submission.py`;
- [x] formal 12-slide initial-round PPTX;
- [x] PDF exported from the same deck through LibreOffice;
- [x] rendered PDF visually reviewed for clipping / overlap;
- [x] demo runbook;
- [x] pitch speaker notes;
- [x] initial-round submission checklist;
- [x] reproducible pitch-deck build script;
- [x] release and submission documentation;
- [x] new launcher / preflight tests.

## Core benchmark state

```text
5 / 5 deterministic scenarios PASS
scenario pass rate:                   100%
root-cause scenario accuracy:         100%
false-correlation rejection accuracy: 100%
mean evidence coverage:               100%
verifier violations:                  0
```

Adversarial release gate:

```text
8 / 8 PASS
scope refusal accuracy:              100%
planner policy catch rate:           100%
verifier evidence-integrity catch:   100%
causal-overclaim catch rate:         100%
ground-truth leak catch rate:        100%
false-correlation rejection rate:    100%
```

## Submission assets

```text
submission/
├── FitzSight_GOAI_Initial_Round.pptx
├── FitzSight_GOAI_Initial_Round.pdf
├── README.md
├── DEMO_RUNBOOK.md
├── PITCH_SPEAKER_NOTES.md
└── SUBMISSION_CHECKLIST.md
```

The slide deck is a competition-facing summary of already implemented synthetic benchmark evidence. It does not introduce a second analytical path.

## External runtime state

### Done

- DuckDB runtime with `data/generated`;
- constrained planner on DuckDB;
- JSON-file planner on DuckDB.

### Still pending live evidence

- OpenAI Responses API with real credentials/model;
- Streamlit runtime smoke test on the final demo environment.

## Remaining competition work

1. obtain real Streamlit runtime evidence on the final presentation machine;
2. validate OpenAI Responses live planner only if model/API access is available and stable;
3. record the demo video and create offline/local backup copies;
4. re-check final GOAI portal constraints immediately before submission;
5. submit and retain confirmation evidence;
6. rehearse the 5–8 minute pitch and <3 minute demo.
