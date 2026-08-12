# FitzSight Repository Manifest — v0.12.0

This manifest describes the **v0.12.0 delivery contents**. Project status remains governed by the single external progress truth: `AplusNeutrino/My_Blog/docs/PROJFITZGERALD_PROGRESS.md`.

## Core project files

- `README.md` — product overview, primary/secondary persona, hero/refusal positioning, quick start and limitations
- `MASTER_PLAN.md` — product/competition plan plus decisions through the v0.12 GOAI alignment milestone
- `IMPLEMENTATION_STATUS.md` — current implementation, validation and evidence-gated runtime status
- `PROJECT_PROGRESS.md` — pointer/handoff note to the unique external progress truth; not a second tracker
- `RELEASE_NOTES_v0.12.md` — v0.12 implementation and validation delta
- `LICENSE` — MIT License
- `THIRD_PARTY_NOTICES.md` — dependency/build-tool notices
- `.env.example` — optional provider/runtime environment variables
- `pyproject.toml` — package metadata and core/dev/submission/OpenAI/UI extras
- `SHA256SUMS.txt` — checksums for the repository snapshot in this delivery

## Agent, investigation and evidence core

- `src/fitzsight/agent/catalog.py` — five approved intents and action catalogs; CRM/FTD is the v0.12 hero
- `src/fitzsight/agent/planner.py` — constrained rule / structured JSON planner with v0.12 plan validation
- `src/fitzsight/agent/orchestrator.py` — verified Agent loop plus bounded evidence-only follow-up
- `src/fitzsight/agent/verifier.py` — fail-closed evidence/claim verifier
- `src/fitzsight/investigation/engine.py` — bounded-adaptive CRM/FTD investigation and fail-closed branch handling
- `src/fitzsight/investigation/net_deposit.py` — client-fund-flow anomaly investigation
- `src/fitzsight/investigation/customer_intelligence.py` — descriptive customer segmentation investigation
- `src/fitzsight/investigation/lead_quality.py` — marketing-quality and false-correlation investigations
- `src/fitzsight/evidence/registry.py` — auditable Evidence Registry
- `src/fitzsight/tools/document_evidence.py` — fixed, source-addressed synthetic document evidence lookup
- `synthetic_documents/` — human-readable source material mirrored by the approved document-evidence catalog

## Analytics / deterministic tools

- `src/fitzsight/tools/sql.py` — read-only SQL safety boundary
- `src/fitzsight/tools/comparison.py` — period comparison
- `src/fitzsight/tools/contribution.py` — contribution decomposition
- `src/fitzsight/tools/statistics.py` — statistical tests
- `src/fitzsight/tools/anomaly.py` — robust anomaly scan
- `src/fitzsight/tools/segmentation.py` — transparent descriptive segmentation
- `src/fitzsight/tools/kpi.py` / `src/fitzsight/analytics/kpis.py` — KPI definitions and helpers

## Runtime and UI

- `streamlit_app.py` — Streamlit renderer for verified presentation data
- `src/fitzsight/ui/presenter.py` — pure/testable KPI/chart/trace/Evidence presentation layer; v0.12 trace exposes branch status/reason/Evidence IDs
- `src/fitzsight/demo.py` — canonical five-demo-question catalog
- `scripts/agent_investigate.py` — constrained Agent CLI
- `scripts/start_demo.py` — one-command auto/UI/CLI launcher with deterministic fallback
- `scripts/runtime_doctor.py` — dependency/data/presentation readiness check without secret disclosure
- `scripts/validate_streamlit_runtime.py` — localhost Streamlit health-check validator
- `scripts/validate_openai_runtime.py` — explicit live OpenAI planner → tools → verifier validator
- `scripts/final_machine_check.py` — default-safe local final-machine readiness report; live provider remains explicit opt-in

## v0.12 evaluation and runtime-derived product evidence

- `scripts/run_evaluation_v2_holdout.py` — unseen-seed + question-paraphrase holdout harness
- `scripts/run_evaluation_v2_ablation.py` — controlled Full FitzSight vs no-verifier/evidence-gate architecture ablation
- `scripts/build_hero_evidence.py` — builds product-process evidence from a real deterministic verified CRM/FTD run
- `docs/V0.12_HOLDOUT_RESULTS.json` — holdout evidence
- `docs/V0.12_ABLATION_RESULTS.json` — architecture-ablation evidence
- `docs/V0.12_BENCHMARK_RESULTS.json` — five-scenario fixed benchmark regression
- `docs/V0.12_ADVERSARIAL_RESULTS.json` — adversarial release gate
- `docs/V0.12_HERO_RUN.json` — full runtime-derived hero run
- `docs/V0.12_EVALUATION.md` — evaluation protocol, results and interpretation boundaries
- `docs/V0.12_POSITIONING_AND_HERO.md` — persona, beachhead and hero-workflow contract
- `docs/V0.12_VALIDATION.md` — release validation record and explicit unverified boundaries
- `docs/V0.12_SUBMISSION_PREFLIGHT.json` — local submission-asset preflight result
- `docs/V0.12_HANDOFF_READINESS.json` — local user-takeover readiness result
- `docs/V0.12_FINAL_MACHINE_READINESS.json` — default-safe local final-machine readiness result
- `submission/FitzSight_Hero_Run_Evidence.html` — runtime-derived product-process evidence view
- `submission/FitzSight_Hero_Run_Evidence.png` — static runtime-derived evidence view for presentation use

## GOAI / competition documentation

- `docs/INITIAL_ROUND_PROJECT_SUMMARY.md` — primary persona, beachhead, bounded Agent story and truthful evaluation claims
- `docs/PITCH_DECK_CONTENT.md` — v0.12 source narrative: one CRM/FTD hero + one false-correlation refusal; **the existing PPT/PDF have not yet been regenerated from this source**
- `docs/ARCHITECTURE.md` — current implemented architecture plus v0.12 bounded-adaptivity notes
- `docs/COMPLIANCE_AND_SAFETY.md` — evidence/safety boundary and high-impact-decision exclusions
- `docs/ENTERPRISE_DEPLOYMENT_BOUNDARY.md` — production governance blueprint; RBAC/PII/retention controls are explicitly planned, not current PoC implementation
- `docs/DATA_DICTIONARY.md` — synthetic data fields and ground-truth boundary
- `docs/UI_DEMO.md` — product-process trace/evidence presentation guidance
- `submission/DEMO_RUNBOOK.md` — demo operating sequence and failure fallback
- `submission/PITCH_SPEAKER_NOTES.md`, `submission/PITCH_REHEARSAL.md`, `submission/JUDGE_QA.md` — operator-facing speaking assets

## Final-machine / operator handoff

- `docs/OPERATOR_BOUNDARY.md` — explicit local-automation vs user-manual external-action boundary
- `docs/FINAL_MACHINE_OPERATIONS.md` — final-machine operating model and evidence boundary
- `scripts/build_manual_handoff.py` — local-only portable handoff packet builder
- `scripts/build_final_machine_kit.py` — portable full local presentation-machine kit builder
- `scripts/handoff_readiness.py` — machine-readable user-takeover readiness report
- `scripts/rehearsal_assistant.py` — local human-rehearsal timing recorder
- `scripts/preflight_submission.py` — local release/submission preflight with manual-boundary assertions
- `submission/FitzSight_Manual_Handoff.zip` — v0.12 local manual handoff packet
- `submission/FitzSight_Final_Machine_Kit.zip` — v0.12 final-machine kit
- `submission/START_HERE_MANUAL.md`
- `submission/FINAL_MACHINE_CHECKLIST.md`
- `submission/REHEARSAL_OPERATOR_CARD.md`
- `submission/REHEARSAL_PLAN.json`
- `submission/MANUAL_SUBMISSION_CHECKLIST.md`
- `submission/RUNTIME_VALIDATION_FOR_USER.md`

## Tests

- `tests/` contains the deterministic unit/integration/release-gate suite.
- v0.12 additions include document evidence, bounded-adaptive hero/failure branches and Evaluation v2 checks.
- Release validation: **85 collected / 84 passed / 1 skipped / 0 failed** in complete non-overlapping groups; skip is the build-sandbox DuckDB-specific integration and is not a live runtime PASS.

## Explicitly not claimed by this manifest

- The existing formal GOAI PPTX/PDF is **not** v0.12-synchronized yet; regeneration remains in progress.
- Streamlit live runtime was not validated in the build sandbox.
- OpenAI live planner/provider telemetry was not requested or validated.
- Current PoC does not implement production SSO/RBAC, row/field policy, PII masking or retention governance.
- No GOAI portal, Gmail, GitHub publish or other external-account write is represented as completed by this delivery.
