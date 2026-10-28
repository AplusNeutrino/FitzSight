from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
import json

import pandas as pd
import pytest

from fitzsight.agent.verifier import EvidenceClaimVerifier
from fitzsight.data.store import AnalyticsStore
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.investigation.net_deposit import NetDepositInvestigationEngine
from fitzsight.metrics import get_metric, net_deposit_definitions
from fitzsight.tools.schema import SchemaInspectorTool
from fitzsight.tools.sql import ReadOnlySQLTool
from test_numeric_claims import fixture


def test_catalog_is_versioned_immutable_and_json_snapshot_has_no_aliases():
    metric = get_metric('net_deposits.v1')
    assert metric.version == '1'
    assert metric.numerator == 'sum(deposits.amount) - sum(withdrawals.amount)'
    assert metric.denominator is None  # Amount, not a percentage or per-customer value.
    assert metric.status_filter == ('completed',)
    assert metric.source_keys == (('deposits', 'deposit_id'), ('withdrawals', 'withdrawal_id'))
    assert metric.unit == 'currency_amount' and metric.currency == 'USD'
    with pytest.raises(FrozenInstanceError):
        metric.currency = 'EUR'
    snapshot = net_deposit_definitions()
    assert json.loads(json.dumps(snapshot)) == snapshot
    snapshot[0]['source_keys'][0][1] = 'customer_id'
    snapshot[1]['currency'] = 'EUR'
    assert net_deposit_definitions()[0]['source_keys'][0][1] == 'deposit_id'
    assert get_metric('net_deposit_change.v1').currency == 'USD'


@pytest.mark.parametrize('metric_id', ['net_deposits', 'net_deposits.v2', 'conversion_rate.v1', '', None, [], 1])
def test_unknown_or_unversioned_metric_is_not_silently_substituted(metric_id):
    with pytest.raises(ValueError, match='Unsupported versioned metric'):
        get_metric(metric_id)


@pytest.mark.parametrize('field,value', [
    ('metric_id', 'profit.v1'), ('version', '2'),
    ('numerator', 'sum(deposits.amount) + sum(withdrawals.amount)'),
    ('denominator', 'customer_count'), ('components', ['balance']),
    ('source_keys', [['deposits', 'customer_id']]),
    ('deduplication_policy', 'deduplicate all rows'),
    ('time_fields', [['deposits', 'registration_date']]),
    ('window_semantics', 'end day exclusive'), ('timezone_policy', 'UTC converted'),
    ('status_filter', ['completed', 'pending']), ('region_attribution', 'historical snapshot'),
    ('unit', 'percent'), ('currency', 'EUR'), ('limitations', []),
])
def test_replaced_definition_fails_both_cashflow_checks(field, value):
    registry, result = fixture()
    original = registry.get(result.claims[0].numeric_binding.evidence_id)
    parameters = deepcopy(original.parameters)
    parameters['metric_definitions'][0][field] = value
    changed = registry.register(original.tool_name, parameters, original.result)
    claims = []
    for claim in result.claims[:2]:
        claims.append(replace(claim,
            numeric_binding=replace(claim.numeric_binding, evidence_id=changed.evidence_id),
            evidence_ids=claim.evidence_ids + (changed.evidence_id,)))
    report = EvidenceClaimVerifier(registry).verify(replace(result, claims=tuple(claims) + result.claims[2:]))
    assert not report.passed
    assert {c.check_id for c in report.checks if not c.passed} >= {'numeric_binding:N-C1', 'numeric_binding:N-C2'}


@pytest.mark.parametrize('change', ['delete', 'empty', 'duplicate', 'missing_change', 'missing_decomposition'])
def test_catalog_snapshot_cannot_be_removed_or_duplicated(change):
    registry, result = fixture()
    record = registry.get(result.claims[0].numeric_binding.evidence_id)
    # The registry's parameters are not signed; verify must still reject this mutation.
    if change == 'delete':
        del record.parameters['metric_definitions']
    elif change == 'empty':
        record.parameters['metric_definitions'] = []
    elif change == 'duplicate':
        record.parameters['metric_definitions'].append(record.parameters['metric_definitions'][0])
    else:
        record.parameters['metric_definitions'].pop(1 if change == 'missing_change' else 2)
    report = EvidenceClaimVerifier(registry).verify(result)
    assert not report.passed
    assert {c.check_id for c in report.checks if not c.passed} >= {'numeric_binding:N-C1', 'numeric_binding:N-C2'}


@pytest.mark.parametrize('backend', ['sqlite', 'duckdb'])
def test_actual_engine_records_definitions_and_matches_independent_cashflow_arithmetic(tmp_path, backend):
    pd.DataFrame([
        {'customer_id': 'A', 'region': 'Europe', 'assigned_team': 'Team A'},
        {'customer_id': 'B', 'region': 'Asia', 'assigned_team': 'Team B'},
    ]).to_csv(tmp_path / 'customers.csv', index=False)
    for table, amounts in [('deposits', [100, 75]), ('withdrawals', [20, 15])]:
        rows = []
        for i, (timestamp, amount) in enumerate(zip(['2026-07-27', '2026-08-03'], amounts)):
            rows.append({table[:-1] + '_id': str(i), 'customer_id': 'A', 'timestamp': timestamp,
                         'amount': amount, 'currency': 'USD', 'status': 'completed'})
        rows.append({table[:-1] + '_id': 'excluded', 'customer_id': 'A', 'timestamp': '2026-08-03',
                     'amount': 1000, 'currency': 'USD', 'status': 'pending'})
        pd.DataFrame(rows).to_csv(tmp_path / (table + '.csv'), index=False)
    pd.DataFrame(columns=['event_id', 'date', 'event_type', 'region', 'affected_team', 'description']).to_csv(tmp_path / 'business_events.csv', index=False)
    with AnalyticsStore(tmp_path, backend=backend) as store:
        store.load_csv_directory()
        registry = EvidenceRegistry()
        engine = NetDepositInvestigationEngine(schema_tool=SchemaInspectorTool(store, registry),
            sql_tool=ReadOnlySQLTool(store, registry), registry=registry)
        result = engine.investigate('Why did European net deposits decline this week?')
        assert EvidenceClaimVerifier(registry).verify(result).passed
        assert result.metrics['periods']['baseline']['net_deposits'] == 80
        assert result.metrics['periods']['current']['net_deposits'] == 60
        assert result.claims[0].numeric_binding.value == -20
        assert result.claims[1].numeric_binding.deposit_change == -25
        assert result.claims[1].numeric_binding.withdrawal_change == -5
        record = registry.get(result.claims[0].numeric_binding.evidence_id)
        assert record.parameters['metric_definitions'] == net_deposit_definitions()
        exported = next(e for e in result.to_dict()['evidence'] if e['evidence_id'] == record.evidence_id)
        assert exported['parameters']['metric_definitions'][0]['denominator'] is None
        assert exported['parameters']['metric_definitions'][0]['deduplication_policy'].startswith('none:')
