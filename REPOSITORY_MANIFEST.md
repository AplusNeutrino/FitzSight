# FitzSight Repository Manifest — v0.8.0

## Core project files

- `README.md` — project overview, quick start, five workflows, evaluation, submission assets, safety
- `MASTER_PLAN.md` — long-term product/competition plan and architecture decisions
- `IMPLEMENTATION_STATUS.md` — current implementation snapshot
- `LICENSE` — MIT License
- `THIRD_PARTY_NOTICES.md` — dependency/build-tool notice
- `PROJECT_PROGRESS.md` — pointer to external progress truth source
- `.env.example` — optional provider/runtime environment variables
- `pyproject.toml` — package/dependency metadata and optional `submission` extra

## Runtime and UI

- `streamlit_app.py` — five-workflow verified-output demo UI
- `scripts/agent_investigate.py` — constrained Agent CLI
- `scripts/start_demo.py` — one-command auto/UI/CLI competition launcher with deterministic fallback
- `scripts/generate_data.py` — synthetic data generation
- `scripts/run_benchmark.py` — five-scenario deterministic benchmark
- `scripts/run_adversarial_evaluation.py` — adversarial safety/evidence release gate

## Submission / competition assets

- `scripts/build_pitch_deck.py` — reproducible 12-slide PPTX builder + optional LibreOffice PDF export
- `scripts/preflight_submission.py` — local submission/repository preflight
- `submission/FitzSight_GOAI_Initial_Round.pptx` — editable formal initial-round deck
- `submission/FitzSight_GOAI_Initial_Round.pdf` — reviewed PDF exported from the same deck
- `submission/DEMO_RUNBOOK.md` — <3 minute recommended demo path and fallback route
- `submission/PITCH_SPEAKER_NOTES.md` — 12-slide speaking notes
- `submission/JUDGE_QA.md` — judge Q&A preparation
- `submission/SUBMISSION_CHECKLIST.md` — technical/compliance/portal checklist

## Agent and tools

- `src/fitzsight/agent/` — intent catalog, planner, orchestrator, verifier, renderer
- `src/fitzsight/investigation/` — five deterministic investigation workflows
- `src/fitzsight/tools/` — schema, read-only SQL, KPI, statistics, contribution, anomaly, segmentation
- `src/fitzsight/evidence/` — append-only evidence registry
- `src/fitzsight/data/` — synthetic generator, scenarios, local analytical store
- `src/fitzsight/providers/` — optional model-provider adapter

## Evaluation

- `evaluation/benchmark_catalog.json` — five business scenarios
- `evaluation/adversarial_cases.json` — eight adversarial cases
- `docs/V0.8_BENCHMARK_RESULTS.json` — v0.8 rebuild of benchmark output on SQLite fallback
- `docs/V0.8_ADVERSARIAL_RESULTS.json` — v0.8 rebuild of adversarial output
- `docs/V0.8_SUBMISSION_PREFLIGHT.json` — local submission preflight result
- `docs/EVALUATION_SUMMARY.md` — judge-friendly evaluation summary

## Competition / documentation

- `docs/INITIAL_ROUND_PROJECT_SUMMARY.md`
- `docs/PITCH_DECK_CONTENT.md`
- `docs/COMPLIANCE_AND_SAFETY.md`
- `docs/BENCHMARK_SCENARIOS.md`
- `docs/ADVERSARIAL_EVALUATION.md`
- `docs/V0.8_VALIDATION.md`
- historical release validation/results remain under `docs/V0.x_*`.

## Tests

`tests/` covers deterministic data generation, SQL safety, statistics, evidence, planner policy, verifier behavior, five Agent intents, OpenAI provider contract, benchmark catalog, adversarial checks, one-command launcher behavior, submission preflight policy, and PPTX/PDF submission assets.
