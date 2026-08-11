from pathlib import Path

from fitzsight.data.generator import GeneratorConfig, write_csv_bundle
from fitzsight.data.store import AnalyticsStore
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.tools.comparison import PeriodComparisonTool
from fitzsight.tools.kpi import KPITool
from fitzsight.tools.sql import ReadOnlySQLTool


def test_kpi_and_period_comparison_are_evidence_linked(tmp_path: Path):
    data_dir = tmp_path / "generated"
    write_csv_bundle(data_dir, GeneratorConfig(seed=20260811, n_customers=3_000, n_salespeople=50))
    registry = EvidenceRegistry()

    with AnalyticsStore(data_dir, backend="sqlite") as store:
        store.load_csv_directory()
        sql = ReadOnlySQLTool(store, registry)
        kpi = KPITool(sql, registry)
        comparison = PeriodComparisonTool(kpi, registry)

        affected = "region = 'Europe' AND assigned_team IN ('Team A','Team B')"
        pre = affected + " AND lead_created_at < '2026-07-15'"
        post = affected + " AND lead_created_at >= '2026-07-15'"

        result = comparison.run(
            "ftd_conversion_rate",
            current_where=post,
            baseline_where=pre,
            current_label="post",
            baseline_label="pre",
        )

    assert isinstance(result.data["absolute_change"], float)
    assert len(result.data["source_evidence_ids"]) == 2
    assert registry.get(result.evidence_id).tool_name == "period_comparison"
