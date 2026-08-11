# FitzSight v0.4.0 Release Notes

Date: 2026-08-11

## Theme

**Constrained Agent Orchestration**

v0.4 introduces the first Agent layer above FitzSight's deterministic v0.3 analytical stack.

## Added

- `ConstrainedRulePlanner` as a reliable no-API fallback;
- provider-neutral `StructuredJSONPlanner` adapter;
- strict Agent plan schema and action allow-list;
- pre-model scope refusal for unsupported questions;
- explicit prohibition on planner-generated SQL/tool arguments;
- `FitzSightAgent` orchestration layer;
- evidence-linked planning audit record;
- `EvidenceClaimVerifier` with fail-closed claim validation;
- evidence digest/status validation;
- `_gt` evaluation-boundary check;
- causal-overclaim guardrail enforcement;
- verified final-answer renderer;
- complete Agent audit evidence output;
- `scripts/agent_investigate.py`;
- example valid planner JSON;
- Agent planner/verifier/orchestrator tests;
- `docs/AGENT_LAYER.md`.

## Safety model

The planner may select only the current approved high-level action sequence. It cannot emit SQL or execute business actions. All quantitative conclusions continue to originate from the deterministic Tool Layer.

## Deferred

- external LLM provider integration;
- multi-intent planning;
- customer segmentation;
- Streamlit UI;
- final open-source license;
- DuckDB runtime validation remains dependent on an environment with DuckDB installed.
