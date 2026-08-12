# FitzSight Repository Manifest — v0.11.0

## Core project files

- `README.md` — product overview, five workflows, validation and final-machine path
- `MASTER_PLAN.md` — product/competition plan plus implementation decisions through v0.11
- `IMPLEMENTATION_STATUS.md` — current implementation/runtime/operator snapshot
- `LICENSE` — MIT License
- `THIRD_PARTY_NOTICES.md` — dependency/build-tool notices
- `PROJECT_PROGRESS.md` — pointer to the external project-progress truth source
- `.env.example` — optional provider/runtime environment variables
- `pyproject.toml` — package metadata and core/dev/submission/OpenAI/UI extras

## Runtime and UI

- `streamlit_app.py` — Streamlit renderer for verified presentation data
- `src/fitzsight/ui/presenter.py` — pure/testable KPI/chart/trace/Evidence presentation layer
- `src/fitzsight/demo.py` — canonical five-demo-question catalog
- `scripts/agent_investigate.py` — constrained Agent CLI
- `scripts/start_demo.py` — one-command auto/UI/CLI launcher with deterministic fallback
- `scripts/runtime_doctor.py` — dependency/data/presentation readiness check without secret disclosure
- `scripts/validate_streamlit_runtime.py` — real localhost Streamlit health-check validator
- `scripts/validate_openai_runtime.py` — explicit live OpenAI planner → tools → verifier validator
- `scripts/final_machine_check.py` — one-command final-machine local readiness report; OpenAI remains explicit opt-in

## Final-machine / operator handoff

- `docs/OPERATOR_BOUNDARY.md` — explicit local-automation vs user-manual external-action boundary
- `docs/FINAL_MACHINE_OPERATIONS.md` — final-machine operating model and evidence boundary
- `scripts/build_manual_handoff.py` — local-only portable handoff packet builder
- `scripts/build_final_machine_kit.py` — portable full local presentation-machine kit builder
- `scripts/handoff_readiness.py` — machine-readable user-takeover readiness report
- `scripts/rehearsal_assistant.py` — local human-rehearsal timing recorder
- `scripts/preflight_submission.py` — local release/submission preflight with manual-boundary assertions
- `submission/START_HERE_MANUAL.md`
- `submission/FINAL_MACHINE_CHECKLIST.md`
- `submission/REHEARSAL_OPERATOR_CARD.md`
- `submission/REHEARSAL_PLAN.json`
- `submission/MANUAL_SUBMISSION_CHECKLIST.md`
- `submission/RUNTIME_VALIDATION_FOR_USER.md`
- `submission/GOAI_FIELD_MAP.md`
- `submission/FitzSight_Manual_Handoff.zip`
- `submission/FitzSight_Final_Machine_Kit.zip`

## Competition assets

- `submission/FitzSight_GOAI_Initial_Round.pptx`
- `submission/FitzSight_GOAI_Initial_Round.pdf`
- `submission/FitzSight_Offline_Demo.html`
- `submission/FitzSight_Offline_Demo.json`
- `submission/FitzSight_Offline_Demo_Backup.mp4`
- `submission/FitzSight_GOAI_Upload_Bundle.zip`
- `submission/PORTAL_COPY.md`
- `submission/DEMO_RUNBOOK.md`
- `submission/PITCH_REHEARSAL.md`
- `submission/PITCH_SPEAKER_NOTES.md`
- `submission/JUDGE_QA.md`
- `submission/SUBMISSION_CHECKLIST.md`

## Agent, investigations and tools

- `src/fitzsight/agent/` — intent catalog, constrained planners, orchestration, verifier, renderer
- `src/fitzsight/investigation/` — five deterministic financial-operations workflows
- `src/fitzsight/tools/` — schema, read-only SQL, KPI, statistics, contribution, anomaly, segmentation
- `src/fitzsight/evidence/` — append-only evidence registry
- `src/fitzsight/data/` — synthetic generator, scenario definitions, analytical store
- `src/fitzsight/providers/` — optional OpenAI Responses planner + runtime telemetry

## Evaluation

- `evaluation/benchmark_catalog.json` — stable five-scenario benchmark contract
- `evaluation/adversarial_cases.json` — eight adversarial cases
- `scripts/run_benchmark.py` — scenario/evidence/verifier evaluation
- `scripts/run_adversarial_evaluation.py` — safety/evidence release gate
- `scripts/measure_latency.py` — deterministic full-Agent latency measurement
- `docs/V0.11_BENCHMARK_RESULTS.json`
- `docs/V0.11_ADVERSARIAL_RESULTS.json`
- `docs/V0.11_FINAL_MACHINE_READINESS.json`
- `docs/V0.11_HANDOFF_READINESS.json`
- `docs/V0.11_SUBMISSION_PREFLIGHT.json`
- `docs/V0.11_VALIDATION.md`
- historical `docs/V0.x_*` files remain as release evidence

## Tests

`tests/` covers data generation, read-only SQL safety, statistics, evidence integrity, planner policy, verifier behavior, all five Agent workflows, UI presentation logic, OpenAI provider contract/telemetry, runtime/launch assets, benchmark/adversarial release gates, submission preflight, dynamic pitch-deck metrics, manual handoff guarantees, final-machine kit integrity, local readiness, and human-rehearsal timing boundaries.
