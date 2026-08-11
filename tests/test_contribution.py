from pathlib import Path

from fitzsight.data.generator import GeneratorConfig, write_csv_bundle
from fitzsight.data.store import AnalyticsStore
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.tools.contribution import ContributionAnalysisTool
from fitzsight.tools.sql import ReadOnlySQLTool


def test_rate_decomposition_reconstructs_aggregate_change(tmp_path: Path):
    data_dir = tmp_path / "data"
    write_csv_bundle(data_dir, GeneratorConfig(seed=20260811, n_customers=10_000, n_salespeople=50))
    registry = EvidenceRegistry()

    with AnalyticsStore(data_dir, backend="sqlite") as store:
        store.load_csv_directory()
        sql = ReadOnlySQLTool(store, registry, max_rows=5000)
        tool = ContributionAnalysisTool(sql, registry)
        result = tool.binary_rate_by_dimension(
            table="sales_activity",
            dimension="assigned_team",
            outcome_column="converted_ftd",
            baseline_where="region = 'Europe' AND lead_created_at < '2026-07-15'",
            current_where="region = 'Europe' AND lead_created_at >= '2026-07-15'",
        )

    data = result.data
    assert abs(data["reconstruction_error_pp"]) < 1e-9
    assert len(data["segments"]) >= 2
    assert data["source_evidence_ids"]
    assert result.evidence_id.startswith("E")
    negative = {row["segment"] for row in data["segments"] if row["total_contribution_pp"] < 0}
    assert {"Team A", "Team B"} & negative
