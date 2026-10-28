"""Real SQLite/DuckDB binding checks, using small hand-authored data."""
from datetime import date

import pandas as pd
import pytest

from fitzsight.data.store import AnalyticsStore
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.investigation.net_deposit import NetDepositInvestigationEngine
from fitzsight.tools.schema import SchemaInspectorTool
from fitzsight.tools.sql import ReadOnlySQLTool, SQLSafetyError


@pytest.fixture(params=['sqlite', 'duckdb'])
def sql_tool(request, tmp_path):
    with AnalyticsStore(tmp_path, backend=request.param) as store:
        yield ReadOnlySQLTool(store, EvidenceRegistry(), max_rows=2)


def test_values_are_bound_and_evidence_is_a_snapshot(sql_tool):
    attack = "Europe'; DROP TABLE customers; --"
    parameters = [attack, None, 12, 1.25, True]
    result = sql_tool.run('SELECT ? AS region, ? AS missing, ? AS n, ? AS amount, ? AS flag', parameters=parameters)
    assert result.data['rows'] == [dict(region=attack, missing=None, n=12, amount=1.25, flag=True)]
    record = sql_tool.registry.get(result.evidence_id)
    parameters[0] = 'changed'
    assert record.parameters['bound_parameters'][0] == attack
    assert attack not in record.parameters['sql']
    assert record.status == 'success'


@pytest.mark.parametrize('parameters', ['Europe', {'region': 'Europe'}, [float('nan')], [float('inf')], [[1]], [date(2026, 8, 3)], [2**63]])
def test_invalid_parameters_never_register_success(sql_tool, parameters):
    with pytest.raises(ValueError):
        sql_tool.run('SELECT ?', parameters=parameters)
    assert not sql_tool.registry.records()


@pytest.mark.parametrize('parameters', [[], [1, 2]])
def test_binding_count_errors_are_recorded_as_errors(sql_tool, parameters):
    with pytest.raises(RuntimeError, match='SQL execution failed'):
        sql_tool.run('SELECT ?', parameters=parameters)
    record, = sql_tool.registry.records()
    assert record.status == 'error'
    assert record.parameters['bound_parameters'] == parameters


def test_binding_does_not_bypass_read_only_policy(sql_tool):
    with pytest.raises(SQLSafetyError):
        sql_tool.run('DELETE FROM customers WHERE region = ?', parameters=['Europe'])
    assert not sql_tool.registry.records()


def test_binding_preserves_limit_compact_evidence_and_cte(sql_tool):
    result = sql_tool.run('WITH x AS (SELECT ? AS n UNION ALL SELECT ? UNION ALL SELECT ?) SELECT n FROM x ORDER BY n;', parameters=[3, 1, 2], compact_evidence=True, evidence_preview_rows=1)
    assert result.data['rows'] == [{'n': 1}, {'n': 2}]
    assert result.data['truncated'] is True
    record = sql_tool.registry.get(result.evidence_id)
    assert record.parameters['bound_parameters'] == [3, 1, 2]
    assert record.result['rows_preview'] == [{'n': 1}]
    assert record.result['full_result_digest'] == EvidenceRegistry.digest(result.data)


def test_cash_flow_query_boundaries_and_literal_region(sql_tool):
    store = sql_tool.store
    attack = "Europe' OR 1=1 --"
    pd.DataFrame([
        {'customer_id': 'A', 'region': 'Europe', 'assigned_team': 'A'},
        {'customer_id': 'B', 'region': attack, 'assigned_team': 'B'},
    ]).to_csv(store.data_dir / 'customers.csv', index=False)
    rows = [
        ('A', '2026-08-02 23:59:59', 100, 'completed'),
        ('A', '2026-08-03 00:00:00', 10, 'completed'),
        ('A', '2026-08-09 23:59:59', 20, 'completed'),
        ('A', '2026-08-10 00:00:00', 100, 'completed'),
        ('A', '2026-08-05 00:00:00', 100, 'pending'),
        ('B', '2026-08-05 00:00:00', 7, 'completed'),
    ]
    frame = pd.DataFrame(rows, columns=['customer_id', 'timestamp', 'amount', 'status'])
    frame['currency'] = 'USD'
    frame.to_csv(store.data_dir / 'deposits.csv', index=False)
    frame.assign(amount=0).to_csv(store.data_dir / 'withdrawals.csv', index=False)
    store.load_csv_directory()
    sql_tool.max_rows = 100
    engine = NetDepositInvestigationEngine(schema_tool=SchemaInspectorTool(store, sql_tool.registry), sql_tool=sql_tool, registry=sql_tool.registry)
    period = dict(start=date(2026, 8, 3), end=date(2026, 8, 9))
    for region, amounts in [('Europe', [10, 20]), (attack, [7]), (None, [10, 7, 20])]:
        result = engine._money_rows('deposits', region=region, **period)
        assert [row['amount'] for row in result.data['rows']] == amounts
        record = sql_tool.registry.get(result.evidence_id)
        assert record.parameters['bound_parameters'] == ['2026-08-03', '2026-08-10'] + ([] if region is None else [region])
    totals, ids = engine._regional_net_per_customer(**period)
    assert totals['Europe']['net_deposits'] == 30
    assert totals[attack]['net_deposits'] == 7
    assert all(sql_tool.registry.get(eid).parameters['bound_parameters'] == ['2026-08-03', '2026-08-10'] for eid in ids)
    count = len(sql_tool.registry.records())
    with pytest.raises(ValueError, match='Unsupported cash-flow table'):
        engine._money_rows('customers', region='Europe', **period)
    assert len(sql_tool.registry.records()) == count
