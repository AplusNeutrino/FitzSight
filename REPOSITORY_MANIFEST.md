# FitzSight Repository Manifest — v0.12.1

This manifest describes the **v0.12.1 delivery snapshot**. Project task status remains governed only by `AplusNeutrino/My_Blog/docs/PROJFITZGERALD_PROGRESS.md`; this manifest is inventory, not a tracker.

## Release identity

- `pyproject.toml` / `src/fitzsight/__init__.py` — v0.12.1 package identity
- `RELEASE_NOTES_v0.12.1.md` — formal-deck / reviewer-gate patch delta
- `docs/V0.12.1_VALIDATION.md` — test, presentation and local-release validation
- `docs/V0.12.1_GOAI_REVIEWER_GATE.md` — one-time GOAI handbook audit; not a second tracker
- `SHA256SUMS.txt` — repository-snapshot checksums

## Implemented Agent/evidence core

- `src/fitzsight/agent/` — five approved intents, constrained planning, orchestration, renderer and EvidenceClaimVerifier
- `src/fitzsight/investigation/engine.py` — bounded-adaptive CRM/FTD hero with fail-closed dependency handling
- `src/fitzsight/investigation/net_deposit.py` — client-fund-flow investigation
- `src/fitzsight/investigation/customer_intelligence.py` — descriptive segmentation investigation
- `src/fitzsight/investigation/lead_quality.py` — acquisition-quality and false-correlation investigations
- `src/fitzsight/evidence/registry.py` — auditable Evidence Registry
- `src/fitzsight/tools/document_evidence.py` + `synthetic_documents/` — fixed synthetic source/paragraph document evidence
- deterministic read-only KPI/comparison/contribution/statistics/anomaly/segmentation tools under `src/fitzsight/tools/`

## Evaluation evidence

- fixed regression: `docs/V0.12.1_BENCHMARK_RESULTS.json`
- adversarial regression: `docs/V0.12.1_ADVERSARIAL_RESULTS.json`
- holdout/paraphrase: `docs/V0.12_HOLDOUT_RESULTS.json`
- controlled architecture ablation: `docs/V0.12_ABLATION_RESULTS.json`
- runtime-derived hero: `docs/V0.12_HERO_RUN.json`
- evaluation protocol: `docs/V0.12_EVALUATION.md`

## Synchronized competition assets

- `docs/PITCH_DECK_CONTENT.md` — one CRM/FTD hero + one false-correlation refusal content contract
- `submission/FitzSight_GOAI_Initial_Round.pptx` — regenerated 12-slide formal deck
- `submission/FitzSight_GOAI_Initial_Round.pdf` — same-source PDF, render-reviewed
- `submission/FitzSight_Hero_Run_Evidence.png` — full runtime-derived hero evidence view
- `submission/FitzSight_Hero_Run_Trace.png` / `FitzSight_Hero_Run_Answer.png` — runtime-derived presentation crops
- `submission/PITCH_SPEAKER_NOTES.md`, `DEMO_RUNBOOK.md`, `DEMO_VIDEO_SCRIPT.md`, `PITCH_REHEARSAL.md`, `REHEARSAL_OPERATOR_CARD.md`, `JUDGE_QA.md` — operator/pitch assets
- `submission/PORTAL_COPY.md`, `GOAI_FIELD_MAP.md`, `SUBMISSION_CHECKLIST.md` — user-manual submission aids

## Safety / deployment boundaries

- `docs/COMPLIANCE_AND_SAFETY.md` — analytical decision-support and high-impact non-use boundary
- `docs/ENTERPRISE_DEPLOYMENT_BOUNDARY.md` — production blueprint; SSO/RBAC, row/field controls, PII masking and retention are not current PoC claims
- `docs/OPERATOR_BOUNDARY.md` — local automation vs user-manual external actions

## Portable handoff

- `submission/FitzSight_GOAI_Upload_Bundle.zip`
- `submission/FitzSight_Manual_Handoff.zip`
- `submission/FitzSight_Final_Machine_Kit.zip`
- `scripts/build_submission_bundle.py`, `build_manual_handoff.py`, `build_final_machine_kit.py`
- `scripts/preflight_submission.py`, `handoff_readiness.py`, `final_machine_check.py`

## Tests

The deterministic unit/integration/release-gate suite contains **87 collected tests: 86 passed, 1 skipped, 0 failed** in the v0.12.1 build environment. The skip is DuckDB-specific build-environment integration and is not a substitute for live runtime evidence.

## Explicitly not claimed

- Streamlit live runtime on the final presentation machine.
- OpenAI live planner/provider telemetry.
- Production SSO/RBAC/PII/retention controls.
- GOAI portal/email/final-submit confirmation.
- Human pitch/demo/Q&A rehearsal completion.
