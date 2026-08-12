from pathlib import Path

from fitzsight.agent.orchestrator import FitzSightAgent
from fitzsight.agent.planner import ConstrainedRulePlanner
from fitzsight.agent.verifier import EvidenceClaimVerifier
from fitzsight.data.generator import GeneratorConfig, write_csv_bundle
from fitzsight.data.store import AnalyticsStore
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.investigation.engine import DeterministicInvestigationEngine
from fitzsight.tools.schema import SchemaInspectorTool
from fitzsight.tools.sql import ReadOnlySQLTool
from fitzsight.tools.statistics import StatisticalTestTool

QUESTION = "Why did European FTD conversion deteriorate after July 15?"


class EventFailingSQLProxy:
    """Delegates all SQL except the operational-event lookup, which fails closed."""

    def __init__(self, inner: ReadOnlySQLTool, registry: EvidenceRegistry):
        self.inner = inner
        self.registry = registry

    def run(self, sql: str, **kwargs):
        if "FROM business_events" in sql:
            record = self.registry.register(
                "read_only_sql",
                {"sql": sql, "backend": self.inner.store.backend, "simulated_dependency_failure": True},
                {"error": "SimulatedEventDependencyFailure"},
                status="error",
            )
            raise RuntimeError(f"Simulated event dependency failure [{record.evidence_id}]")
        return self.inner.run(sql, **kwargs)


def _build(tmp_path: Path, *, fail_event: bool = False):
    data_dir = tmp_path / "data"
    write_csv_bundle(data_dir, GeneratorConfig(seed=20260811, n_customers=10_000, n_salespeople=50))
    registry = EvidenceRegistry()
    store = AnalyticsStore(data_dir, backend="sqlite")
    store.load_csv_directory()
    base_sql = ReadOnlySQLTool(store, registry, max_rows=5000)
    sql = EventFailingSQLProxy(base_sql, registry) if fail_event else base_sql
    engine = DeterministicInvestigationEngine(
        schema_tool=SchemaInspectorTool(store, registry),
        sql_tool=sql,
        stats_tool=StatisticalTestTool(registry),
        registry=registry,
    )
    agent = FitzSightAgent(
        planner=ConstrainedRulePlanner(),
        engine=engine,
        verifier=EvidenceClaimVerifier(registry),
        registry=registry,
    )
    return store, registry, agent


def test_hero_run_uses_bounded_result_driven_branch_and_document_evidence(tmp_path):
    store, registry, agent = _build(tmp_path)
    try:
        run = agent.run(QUESTION)
        payload = run.to_dict()
        assert payload["verification"]["passed"] is True
        assert payload["investigation"]["diagnosis"]["root_cause_status"] == "supported_candidate"
        assert payload["investigation"]["metrics"]["bounded_branching"] == {
            "drilldown_triggered": True,
            "event_check_triggered": True,
            "event_check_status": "executed",
        }
        assert payload["investigation"]["metrics"]["document_evidence"]["source_ref"] == "CRM-CHANGE-2026-0715#p1"
        actions = {row["action"]: row for row in payload["investigation"]["execution_trace"]}
        assert actions["contribution_decomposition"]["status"] == "executed"
        assert actions["anomaly_scan"]["status"] == "executed"
        assert actions["event_check"]["status"] == "executed"
        assert actions["document_evidence_check"]["status"] == "executed"
        assert any(row["tool_name"] == "agent.branch_decision" for row in payload["audit_evidence"])
        assert any(row["tool_name"] == "document_evidence" for row in payload["audit_evidence"])

        follow_up = agent.answer_follow_up(run, "What evidence supports the CRM routing change candidate?")
        assert follow_up.status == "verified_with_guardrail"
        assert "CRM-CHANGE-2026-0715#p1" in follow_up.answer
        assert registry.get(follow_up.evidence_record_id).tool_name == "agent.follow_up"
    finally:
        store.close()


def test_event_tool_failure_withholds_root_cause_but_keeps_verified_answer(tmp_path):
    store, registry, agent = _build(tmp_path, fail_event=True)
    try:
        run = agent.run(QUESTION)
        payload = run.to_dict()
        assert payload["investigation"]["metrics"]["bounded_branching"]["event_check_status"] == "tool_error_fail_closed"
        assert payload["investigation"]["diagnosis"]["root_cause_status"] == "insufficient_evidence"
        assert payload["investigation"]["metrics"]["document_evidence"] is None
        assert payload["verification"]["passed"] is True
        assert payload["final_answer"]["status"] == "verified"
        assert "insufficient" in payload["final_answer"]["headline"].lower()
        c4 = next(claim for claim in payload["investigation"]["claims"] if claim["claim_id"] == "C4")
        assert c4["status"] == "insufficient_evidence"
        assert all(registry.get(eid).status == "success" for eid in c4["evidence_ids"])
    finally:
        store.close()
