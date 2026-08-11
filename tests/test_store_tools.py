from pathlib import Path

import pytest

from fitzsight.data.generator import GeneratorConfig, write_csv_bundle
from fitzsight.data.store import AnalyticsStore
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.tools.schema import SchemaInspectorTool
from fitzsight.tools.sql import ReadOnlySQLTool


def _data(tmp_path: Path) -> Path:
    data_dir = tmp_path / "data"
    write_csv_bundle(data_dir, GeneratorConfig(seed=7, n_customers=1000, n_salespeople=25))
    return data_dir


def test_sqlite_fallback_loads_schema_and_executes_read_only_query(tmp_path):
    data_dir = _data(tmp_path)
    registry = EvidenceRegistry()
    with AnalyticsStore(data_dir, backend="sqlite") as store:
        info = store.load_csv_directory()
        assert "sales_activity" in info.tables
        schema = SchemaInspectorTool(store, registry).run("sales_activity")
        names = {column["name"] for column in schema.data["columns"]}
        assert {"lead_created_at", "converted_ftd", "assigned_team"} <= names

        result = ReadOnlySQLTool(store, registry, max_rows=10).run(
            "SELECT region, COUNT(*) AS n FROM sales_activity GROUP BY region ORDER BY region"
        )
        assert result.data["row_count"] > 0
        assert result.evidence_id.startswith("E")


@pytest.mark.skipif(not AnalyticsStore.duckdb_available(), reason="DuckDB package unavailable in build environment")
def test_duckdb_backend_loads_and_queries(tmp_path):
    data_dir = _data(tmp_path)
    registry = EvidenceRegistry()
    with AnalyticsStore(data_dir, backend="duckdb") as store:
        store.load_csv_directory()
        result = ReadOnlySQLTool(store, registry).run("SELECT COUNT(*) AS n FROM customers")
        assert int(result.data["rows"][0]["n"]) == 1000
