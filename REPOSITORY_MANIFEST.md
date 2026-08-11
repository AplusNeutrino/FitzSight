# FitzSight Repository Manifest — v0.7.0

## Core project files

- `README.md` — project overview, quick start, five workflows, evaluation, safety
- `MASTER_PLAN.md` — long-term product/competition plan and architecture decisions
- `IMPLEMENTATION_STATUS.md` — current implementation snapshot
- `LICENSE` — MIT License
- `THIRD_PARTY_NOTICES.md` — dependency notice
- `PROJECT_PROGRESS.md` — pointer to external progress truth source
- `.env.example` — optional provider/runtime environment variables
- `pyproject.toml` — package/dependency metadata

## Runtime and UI

- `streamlit_app.py` — five-workflow verified-output demo UI
- `scripts/agent_investigate.py` — constrained Agent CLI
- `scripts/generate_data.py` — synthetic data generation
- `scripts/run_benchmark.py` — five-scenario deterministic benchmark
- `scripts/run_adversarial_evaluation.py` — adversarial safety/evidence release gate

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
- `docs/V0.7_BENCHMARK_RESULTS.json` — raw benchmark result
- `docs/V0.7_ADVERSARIAL_RESULTS.json` — raw adversarial result
- `docs/EVALUATION_SUMMARY.md` — judge-friendly evaluation summary

## Competition / documentation

- `docs/INITIAL_ROUND_PROJECT_SUMMARY.md`
- `docs/PITCH_DECK_CONTENT.md`
- `docs/COMPLIANCE_AND_SAFETY.md`
- `docs/BENCHMARK_SCENARIOS.md`
- `docs/ADVERSARIAL_EVALUATION.md`
- `docs/V0.7_VALIDATION.md`
- historical release validation/results remain under `docs/V0.x_*`.

## Tests

`tests/` covers deterministic data generation, SQL safety, statistics, evidence, planner policy, verifier behavior, five Agent intents, OpenAI provider contract, benchmark catalog, and v0.7 adversarial checks.
