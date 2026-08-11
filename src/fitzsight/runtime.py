from __future__ import annotations

from pathlib import Path

from fitzsight.agent.orchestrator import FitzSightAgent
from fitzsight.agent.planner import Planner
from fitzsight.agent.verifier import EvidenceClaimVerifier
from fitzsight.data.generator import GeneratorConfig, write_csv_bundle
from fitzsight.data.store import AnalyticsStore
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.investigation.customer_intelligence import CustomerIntelligenceInvestigationEngine
from fitzsight.investigation.engine import DeterministicInvestigationEngine
from fitzsight.investigation.net_deposit import NetDepositInvestigationEngine
from fitzsight.investigation.router import MultiIntentInvestigationEngine
from fitzsight.tools.schema import SchemaInspectorTool
from fitzsight.tools.segmentation import CustomerSegmentationTool
from fitzsight.tools.sql import ReadOnlySQLTool
from fitzsight.tools.statistics import StatisticalTestTool


def build_agent_runtime(
    *,
    data_dir: str | Path,
    backend: str,
    planner: Planner,
    generator_config: GeneratorConfig | None = None,
):
    """Build the audited v0.6 runtime and return ``(store, registry, agent)``.

    The caller owns the returned store and must close it. The SQL row bound is
    sized for the 20k-customer synthetic benchmark so customer segmentation can
    analyze the complete European cohort without truncation.
    """

    data_dir = Path(data_dir)
    required = (
        data_dir / "customers.csv",
        data_dir / "sales_activity.csv",
        data_dir / "deposits.csv",
        data_dir / "withdrawals.csv",
        data_dir / "trades.csv",
    )
    if not all(path.exists() for path in required):
        write_csv_bundle(data_dir, generator_config or GeneratorConfig())

    registry = EvidenceRegistry()
    store = AnalyticsStore(data_dir, backend=backend)
    store.load_csv_directory()

    schema_tool = SchemaInspectorTool(store, registry)
    sql_tool = ReadOnlySQLTool(store, registry, max_rows=25_000)
    stats_tool = StatisticalTestTool(registry)
    segmentation_tool = CustomerSegmentationTool(sql_tool, registry)

    crm_engine = DeterministicInvestigationEngine(
        schema_tool=schema_tool,
        sql_tool=sql_tool,
        stats_tool=stats_tool,
        registry=registry,
    )
    net_engine = NetDepositInvestigationEngine(
        schema_tool=schema_tool,
        sql_tool=sql_tool,
        registry=registry,
    )
    customer_engine = CustomerIntelligenceInvestigationEngine(
        schema_tool=schema_tool,
        segmentation_tool=segmentation_tool,
        registry=registry,
    )
    router = MultiIntentInvestigationEngine(
        crm_engine=crm_engine,
        net_deposit_engine=net_engine,
        customer_intelligence_engine=customer_engine,
    )

    agent = FitzSightAgent(
        planner=planner,
        engine=router,
        verifier=EvidenceClaimVerifier(registry),
        registry=registry,
    )
    return store, registry, agent
