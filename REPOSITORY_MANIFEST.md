# FitzSight Repository Manifest

**Version:** v0.5.0  
**Generated:** 2026-08-11  

This manifest records the v0.5.0 delivery snapshot. Generated benchmark CSVs are intentionally excluded; only `data/generated/.gitkeep` is shipped.

## Key v0.5 additions

- `src/fitzsight/agent/catalog.py` — approved multi-intent/action catalog
- `src/fitzsight/investigation/net_deposit.py` — second deterministic investigation
- `src/fitzsight/investigation/router.py` — deterministic intent router
- `src/fitzsight/providers/openai_planner.py` — optional Responses structured planner
- `streamlit_app.py` — minimal verified-results demo shell
- `evaluation/benchmark_catalog.json` — two-scenario catalog
- `scripts/run_benchmark.py` — deterministic benchmark runner
- `docs/V0.5_VALIDATION.md` — v0.5 validation evidence

## Files (93)

- `.env.example`
- `.gitignore`
- `IMPLEMENTATION_STATUS.md`
- `MASTER_PLAN.md`
- `PROJECT_PROGRESS.md`
- `README.md`
- `RELEASE_NOTES_v0.1.md`
- `RELEASE_NOTES_v0.2.md`
- `RELEASE_NOTES_v0.3.md`
- `RELEASE_NOTES_v0.4.md`
- `RELEASE_NOTES_v0.5.md`
- `data/generated/.gitkeep`
- `docs/AGENT_LAYER.md`
- `docs/ARCHITECTURE.md`
- `docs/BASELINE_RESULTS.md`
- `docs/DATA_DICTIONARY.md`
- `docs/DIAGNOSTIC_TOOLS.md`
- `docs/MODEL_PROVIDER.md`
- `docs/MULTI_INTENT.md`
- `docs/TOOL_LAYER.md`
- `docs/UI_DEMO.md`
- `docs/V0.2_VALIDATION.md`
- `docs/V0.3_SAMPLE_INVESTIGATION.json`
- `docs/V0.3_VALIDATION.md`
- `docs/V0.4_SAMPLE_AGENT_SUMMARY.json`
- `docs/V0.4_VALIDATION.md`
- `docs/V0.5_SAMPLE_NET_DEPOSIT_SUMMARY.json`
- `docs/V0.5_VALIDATION.md`
- `evaluation/benchmark_catalog.json`
- `examples/valid_agent_plan.json`
- `examples/valid_net_deposit_plan.json`
- `pyproject.toml`
- `scripts/agent_investigate.py`
- `scripts/generate_data.py`
- `scripts/investigate.py`
- `scripts/run_baseline.py`
- `scripts/run_benchmark.py`
- `src/fitzsight/__init__.py`
- `src/fitzsight/agent/__init__.py`
- `src/fitzsight/agent/catalog.py`
- `src/fitzsight/agent/models.py`
- `src/fitzsight/agent/orchestrator.py`
- `src/fitzsight/agent/planner.py`
- `src/fitzsight/agent/renderer.py`
- `src/fitzsight/agent/verifier.py`
- `src/fitzsight/analytics/__init__.py`
- `src/fitzsight/analytics/baseline.py`
- `src/fitzsight/analytics/kpis.py`
- `src/fitzsight/data/__init__.py`
- `src/fitzsight/data/generator.py`
- `src/fitzsight/data/scenarios.py`
- `src/fitzsight/data/store.py`
- `src/fitzsight/evidence/__init__.py`
- `src/fitzsight/evidence/registry.py`
- `src/fitzsight/investigation/__init__.py`
- `src/fitzsight/investigation/engine.py`
- `src/fitzsight/investigation/models.py`
- `src/fitzsight/investigation/net_deposit.py`
- `src/fitzsight/investigation/router.py`
- `src/fitzsight/providers/__init__.py`
- `src/fitzsight/providers/openai_planner.py`
- `src/fitzsight/runtime.py`
- `src/fitzsight/tools/__init__.py`
- `src/fitzsight/tools/anomaly.py`
- `src/fitzsight/tools/base.py`
- `src/fitzsight/tools/comparison.py`
- `src/fitzsight/tools/contribution.py`
- `src/fitzsight/tools/kpi.py`
- `src/fitzsight/tools/schema.py`
- `src/fitzsight/tools/sql.py`
- `src/fitzsight/tools/statistics.py`
- `streamlit_app.py`
- `tests/test_agent_orchestrator.py`
- `tests/test_agent_planner.py`
- `tests/test_agent_verifier.py`
- `tests/test_anomaly.py`
- `tests/test_benchmark_catalog.py`
- `tests/test_contribution.py`
- `tests/test_evidence.py`
- `tests/test_generator.py`
- `tests/test_investigation.py`
- `tests/test_kpi_tools.py`
- `tests/test_kpis.py`
- `tests/test_multi_intent_planner.py`
- `tests/test_net_deposit_agent.py`
- `tests/test_net_deposit_scenario.py`
- `tests/test_openai_planner.py`
- `tests/test_scenario_crm_routing.py`
- `tests/test_sql_safety.py`
- `tests/test_statistics.py`
- `tests/test_store_tools.py`
