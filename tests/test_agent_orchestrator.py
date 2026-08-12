import json
from pathlib import Path

from fitzsight.agent.orchestrator import FitzSightAgent
from fitzsight.agent.planner import CRM_ACTIONS, CRM_INTENT, ConstrainedRulePlanner, StructuredJSONPlanner
from fitzsight.agent.verifier import EvidenceClaimVerifier
from fitzsight.data.generator import GeneratorConfig, write_csv_bundle
from fitzsight.data.store import AnalyticsStore
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.investigation.engine import DeterministicInvestigationEngine
from fitzsight.tools.schema import SchemaInspectorTool
from fitzsight.tools.sql import ReadOnlySQLTool
from fitzsight.tools.statistics import StatisticalTestTool

QUESTION = "Why did European FTD conversion deteriorate after July 15?"


def _agent(tmp_path: Path, planner):
    data_dir = tmp_path / "data"
    write_csv_bundle(data_dir, GeneratorConfig(seed=20260811, n_customers=10_000, n_salespeople=50))
    registry = EvidenceRegistry()
    store = AnalyticsStore(data_dir, backend="sqlite")
    store.load_csv_directory()
    engine = DeterministicInvestigationEngine(
        schema_tool=SchemaInspectorTool(store, registry),
        sql_tool=ReadOnlySQLTool(store, registry, max_rows=5000),
        stats_tool=StatisticalTestTool(registry),
        registry=registry,
    )
    agent = FitzSightAgent(
        planner=planner,
        engine=engine,
        verifier=EvidenceClaimVerifier(registry),
        registry=registry,
    )
    return store, registry, agent


def test_constrained_agent_runs_question_to_verified_answer(tmp_path):
    store, registry, agent = _agent(tmp_path, ConstrainedRulePlanner())
    try:
        result = agent.run(QUESTION)
        payload = result.to_dict()
        assert payload["product"] == "FitzSight"
        assert payload["mode"] == "agent_v0.12_bounded_adaptive"
        assert payload["verification"]["passed"] is True
        assert payload["final_answer"]["status"] == "verified"
        assert payload["investigation"]["diagnosis"]["root_cause_status"] == "supported_candidate"
        assert len(payload["final_answer"]["findings"]) >= 6
        assert len(payload["audit_evidence"]) >= 13
        assert registry.get(payload["plan_evidence_id"]).tool_name == "agent.plan"
        assert registry.get(payload["final_answer_evidence_id"]).tool_name == "agent.final_answer"
    finally:
        store.close()


def test_structured_llm_plan_cannot_bypass_deterministic_executor(tmp_path):
    plan_payload = {
        "intent": CRM_INTENT,
        "steps": [
            {"action": action, "purpose": f"Perform approved step {action}."}
            for action in CRM_ACTIONS
        ],
    }
    planner = StructuredJSONPlanner(lambda _prompt: json.dumps(plan_payload))
    store, registry, agent = _agent(tmp_path, planner)
    try:
        result = agent.run(QUESTION)
        assert result.planner_mode == "structured_llm_adapter"
        assert result.verification.passed is True
        sql_records = [e for e in result.audit_evidence if e["tool_name"] == "read_only_sql"]
        assert sql_records
        assert all("_gt" not in e["parameters"]["sql"] for e in sql_records)
    finally:
        store.close()
