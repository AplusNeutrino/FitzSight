"""Incomplete SQL results must never certify net-deposit totals."""
from copy import deepcopy
from dataclasses import replace

import pytest

from fitzsight.agent.verifier import EvidenceClaimVerifier
from fitzsight.data.store import AnalyticsStore
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.investigation.net_deposit import NetDepositInvestigationEngine
from fitzsight.investigation.numeric_claims import verify_net_change, verify_net_decomposition
from fitzsight.tools.schema import SchemaInspectorTool
from fitzsight.tools.sql import ReadOnlySQLTool
from test_numeric_claims import fixture


@pytest.mark.parametrize('source_index', range(4))
@pytest.mark.parametrize('defect', ['truncated', 'missing_flag', 'false_string', 'false_integer',
                                  'missing_count', 'wrong_count', 'boolean_count', 'preview'])
def test_incomplete_source_rejects_both_cashflow_claims(source_index, defect):
    registry, result = fixture()
    driver = registry.get(result.claims[0].numeric_binding.evidence_id)
    old_id = driver.parameters['source_evidence_ids'][source_index]
    original = registry.get(old_id)
    payload = deepcopy(original.result)
    if defect == 'truncated': payload['truncated'] = True
    elif defect == 'missing_flag': del payload['truncated']
    elif defect == 'false_string': payload['truncated'] = 'false'
    elif defect == 'false_integer': payload['truncated'] = 0
    elif defect == 'missing_count': del payload['row_count']
    elif defect == 'wrong_count': payload['row_count'] = 2
    elif defect == 'boolean_count': payload['row_count'] = True
    else:
        payload['evidence_mode'] = 'compact_preview'
        payload['rows_preview'] = payload['rows']
    changed = registry.register(original.tool_name, original.parameters, payload)
    # Correct digest, valid ID and unchanged numbers: rejection must be completeness.
    driver.parameters['source_evidence_ids'][source_index] = changed.evidence_id
    claims = tuple(replace(c, evidence_ids=c.evidence_ids + (changed.evidence_id,))
                   for c in result.claims[:2])
    assert not verify_net_change(claims[0], registry)
    assert not verify_net_decomposition(claims[1], registry)
    report = EvidenceClaimVerifier(registry).verify(replace(result, claims=claims + result.claims[2:]))
    assert {c.check_id for c in report.checks if not c.passed} >= {
        'numeric_binding:N-C1', 'numeric_binding:N-C2'}


def write_bundle(root, extra_source):
    (root / 'customers.csv').write_text('customer_id,region,assigned_team\nA,Europe,Team A\nB,Asia,Team B\n')
    for table in ('deposits', 'withdrawals'):
        rows = ['customer_id,timestamp,amount,currency,status']
        for period, day, amount in [('baseline', '2026-07-27', 10), ('current', '2026-08-03', 20)]:
            rows.append(f'A,{day},{amount},USD,completed')
            if (table, period) == extra_source:
                rows.append(f'A,{day},5,USD,completed')
        (root / (table + '.csv')).write_text('\n'.join(rows) + '\n')
    (root / 'business_events.csv').write_text('event_id,date,event_type,region,affected_team,description\n')


@pytest.mark.parametrize('backend', ['sqlite', 'duckdb'])
@pytest.mark.parametrize('source', [('deposits', 'baseline'), ('withdrawals', 'baseline'),
                                  ('deposits', 'current'), ('withdrawals', 'current')])
def test_actual_over_limit_query_stops_before_driver_evidence(tmp_path, backend, source):
    write_bundle(tmp_path, source)
    with AnalyticsStore(tmp_path, backend=backend) as store:
        store.load_csv_directory()
        registry = EvidenceRegistry()
        engine = NetDepositInvestigationEngine(schema_tool=SchemaInspectorTool(store, registry),
            sql_tool=ReadOnlySQLTool(store, registry, max_rows=1), registry=registry)
        with pytest.raises(ValueError, match='require complete SQL rows'):
            engine.investigate('Why did European net deposits decline this week?')
        assert not any(r.tool_name == 'net_deposit_driver_decomposition' for r in registry.records())
        query = registry.records()[-1]
        assert query.tool_name == 'read_only_sql'
        assert query.result['truncated'] is True
        assert query.result['row_count'] == 1


@pytest.mark.parametrize('backend', ['sqlite', 'duckdb'])
def test_exact_limit_and_empty_cashflow_still_verify(tmp_path, backend):
    write_bundle(tmp_path, ('deposits', 'baseline'))
    # Current withdrawals legitimately empty; absence is not truncation.
    (tmp_path / 'withdrawals.csv').write_text('customer_id,timestamp,amount,currency,status\nA,2026-07-27,10,USD,completed\n')
    with AnalyticsStore(tmp_path, backend=backend) as store:
        store.load_csv_directory()
        registry = EvidenceRegistry()
        engine = NetDepositInvestigationEngine(schema_tool=SchemaInspectorTool(store, registry),
            sql_tool=ReadOnlySQLTool(store, registry, max_rows=2), registry=registry)
        result = engine.investigate('Why did European net deposits decline this week?')
        assert EvidenceClaimVerifier(registry).verify(result).passed
        assert result.claims[0].numeric_binding.value == 15  # (20-0)-(15-10)
        sources = registry.get(result.claims[0].numeric_binding.evidence_id).parameters['source_evidence_ids']
        assert registry.get(sources[0]).result['row_count'] == 2
        assert registry.get(sources[3]).result['row_count'] == 0
