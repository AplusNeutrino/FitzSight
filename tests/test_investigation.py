from pathlib import Path

from fitzsight.data.generator import GeneratorConfig, write_csv_bundle
from fitzsight.data.store import AnalyticsStore
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.investigation.engine import DeterministicInvestigationEngine
from fitzsight.tools.schema import SchemaInspectorTool
from fitzsight.tools.sql import ReadOnlySQLTool
from fitzsight.tools.statistics import StatisticalTestTool


def test_deterministic_investigation_recovers_supported_candidate(tmp_path: Path):
    data_dir = tmp_path / "generated"
    write_csv_bundle(data_dir, GeneratorConfig(seed=20260811, n_customers=10_000, n_salespeople=50))

    registry = EvidenceRegistry()
    with AnalyticsStore(data_dir, backend="sqlite") as store:
        store.load_csv_directory()
        sql = ReadOnlySQLTool(store, registry, max_rows=5000)
        engine = DeterministicInvestigationEngine(
            schema_tool=SchemaInspectorTool(store, registry),
            sql_tool=sql,
            stats_tool=StatisticalTestTool(registry),
            registry=registry,
        )
        result = engine.investigate(
            "Why did European FTD conversion deteriorate after July 15?"
        )

    payload = result.to_dict()
    assert payload["product"] == "FitzSight"
    assert payload["mode"] == "deterministic_v0.12_bounded_adaptive"
    assert payload["diagnosis"]["root_cause_status"] == "supported_candidate"
    assert payload["metrics"]["affected"]["conversion_change_pp"] < -5
    assert payload["metrics"]["affected_response_median_change_minutes"] > 15
    assert payload["metrics"]["conversion_test"]["p_value"] < 0.05
    assert abs(payload["metrics"]["team_contribution_analysis"]["reconstruction_error_pp"]) < 1e-9
    assert payload["metrics"]["post_change_response_anomalies"]["current_n"] > 0
    assert len(payload["evidence"]) >= 10
    assert len(payload["claims"]) >= 6
    assert payload["metrics"]["document_evidence"]["source_ref"] == "CRM-CHANGE-2026-0715#p1"
    assert len(payload["execution_trace"]) == 9
    assert payload["metrics"]["bounded_branching"]["event_check_status"] == "executed"
    # Normal investigation must not query the evaluation-only ground-truth flag.
    sql_evidence = [e for e in payload["evidence"] if e["tool_name"] == "read_only_sql"]
    assert all("_gt" not in e["parameters"]["sql"] for e in sql_evidence)


import pandas as pd
import pytest


@pytest.mark.parametrize("backend", ["sqlite","duckdb"])
def test_constant_response_import_preserves_unknown_significance(tmp_path, backend):
    data_dir = tmp_path / "data"
    write_csv_bundle(data_dir, GeneratorConfig(seed=20260811,n_customers=10000,n_salespeople=50))
    path = data_dir / "sales_activity.csv"
    rows = pd.read_csv(path)
    rows["response_time_minutes"] = 5.0
    rows.to_csv(path,index=False)
    registry = EvidenceRegistry()
    with AnalyticsStore(data_dir,backend=backend) as store:
        store.load_csv_directory()
        engine = DeterministicInvestigationEngine(schema_tool=SchemaInspectorTool(store,registry),
            sql_tool=ReadOnlySQLTool(store,registry,max_rows=5000),
            stats_tool=StatisticalTestTool(registry),registry=registry)
        result = engine.investigate("Why did European FTD conversion deteriorate after July 15?")
    assert result.metrics["response_test"]["unavailable_reason"] == "constant_samples"
    assert result.diagnosis["response_shift_significant"] is None
    assert result.diagnosis["root_cause_status"] == "insufficient_evidence"
    assert result.metrics["bounded_branching"]["event_check_status"] != "executed"
