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
from fitzsight.investigation.lead_quality import FalseCorrelationInvestigationEngine, MarketingLeadQualityInvestigationEngine
from fitzsight.investigation.net_deposit import NetDepositInvestigationEngine
from fitzsight.investigation.router import MultiIntentInvestigationEngine
from fitzsight.tools.contribution import ContributionAnalysisTool
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
    data_mode: str = "import",
):
    """Build a runtime; imports never generate or overwrite source data.

    Demo generation is explicitly opt-in and only allowed in an empty directory.
    Existing complete bundles are read as-is in either mode.
    """
    if data_mode not in {"demo", "import"}:
        raise ValueError("data_mode must be 'demo' or 'import'")
    if data_mode == "import" and generator_config is not None:
        raise ValueError("generator_config is only valid in demo mode")
    data_dir = Path(data_dir)
    required_names = (
        "customers.csv", "sales_activity.csv", "deposits.csv",
        "withdrawals.csv", "trades.csv", "business_events.csv",
    )
    missing = [name for name in required_names if not (data_dir / name).is_file()]
    if missing:
        if data_mode == "import":
            raise FileNotFoundError("Import data is incomplete; missing files: " + ", ".join(missing))
        if data_dir.exists() and (not data_dir.is_dir() or any(data_dir.iterdir())):
            raise ValueError("Demo generation requires an empty directory; existing files will not be overwritten")
        write_csv_bundle(data_dir, generator_config or GeneratorConfig())

    registry = EvidenceRegistry()
    store = AnalyticsStore(data_dir, backend=backend)
    try:
        store.load_csv_directory()
    except Exception:
        store.close()
        raise

    schema_tool = SchemaInspectorTool(store, registry)
    sql_tool = ReadOnlySQLTool(store, registry, max_rows=25_000)
    stats_tool = StatisticalTestTool(registry)
    segmentation_tool = CustomerSegmentationTool(sql_tool, registry)
    contribution_tool = ContributionAnalysisTool(sql_tool, registry)

    crm_engine = DeterministicInvestigationEngine(
        schema_tool=schema_tool,
        sql_tool=sql_tool,
        stats_tool=stats_tool,
        registry=registry,
        contribution_tool=contribution_tool,
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
    marketing_engine = MarketingLeadQualityInvestigationEngine(
        schema_tool=schema_tool,
        sql_tool=sql_tool,
        stats_tool=stats_tool,
        contribution_tool=contribution_tool,
        registry=registry,
    )
    false_corr_engine = FalseCorrelationInvestigationEngine(
        schema_tool=schema_tool,
        sql_tool=sql_tool,
        stats_tool=stats_tool,
        contribution_tool=contribution_tool,
        registry=registry,
    )
    router = MultiIntentInvestigationEngine(
        crm_engine=crm_engine,
        net_deposit_engine=net_engine,
        customer_intelligence_engine=customer_engine,
        marketing_lead_quality_engine=marketing_engine,
        false_correlation_engine=false_corr_engine,
    )

    agent = FitzSightAgent(
        planner=planner,
        engine=router,
        verifier=EvidenceClaimVerifier(registry),
        registry=registry,
    )
    return store, registry, agent
