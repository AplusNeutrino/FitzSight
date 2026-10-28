import pandas as pd
import pytest

from fitzsight.data.store import AnalyticsStore
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.investigation.net_deposit import NetDepositInvestigationEngine
from fitzsight.tools.schema import SchemaInspectorTool
from fitzsight.tools.sql import ReadOnlySQLTool


@pytest.mark.parametrize('backend', ['sqlite', 'duckdb'])
@pytest.mark.parametrize('missing', ['event_id', 'date', 'event_type', 'region', 'affected_team', 'description'])
def test_event_missing_column_stops_before_any_analysis_sql(tmp_path, backend, missing):
    columns = {
        'customers': ['customer_id', 'region', 'assigned_team'],
        'deposits': ['customer_id', 'timestamp', 'amount', 'currency', 'status'],
        'withdrawals': ['customer_id', 'timestamp', 'amount', 'currency', 'status'],
        'business_events': ['event_id', 'date', 'event_type', 'region', 'affected_team', 'description'],
    }
    columns['business_events'].remove(missing)
    for table, fields in columns.items():
        pd.DataFrame(columns=fields).to_csv(tmp_path / (table + '.csv'), index=False)
    with AnalyticsStore(tmp_path, backend=backend) as store:
        store.load_csv_directory()
        registry = EvidenceRegistry()
        engine = NetDepositInvestigationEngine(schema_tool=SchemaInspectorTool(store, registry),
            sql_tool=ReadOnlySQLTool(store, registry), registry=registry)
        with pytest.raises(RuntimeError, match='business_events schema missing required fields') as exc:
            engine.investigate('Why did European net deposits decline this week?')
        assert str(exc.value) == f"business_events schema missing required fields: ['{missing}']"
        records = registry.records()
        assert len(records) == 4
        assert all(r.tool_name == 'schema_inspector' for r in records)
        assert records[-1].parameters['table'] == 'business_events'
