from copy import deepcopy
from dataclasses import replace
import json

import pandas as pd
import pytest

from fitzsight.data.snapshot import fingerprint_net_inputs
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.investigation.net_cashflows import execute_net_cashflows
from fitzsight.investigation.numeric_claims import verify_net_change, verify_net_decomposition, render_net_change
from fitzsight.investigation.request import InvestigationRequest, Period

REGIONS = ('Europe', 'Asia', 'Americas')


def bundle(path):
    pd.DataFrame([dict(customer_id=r, region=r, assigned_team='T') for r in REGIONS]).to_csv(path/'customers.csv', index=False)
    for table in ('deposits', 'withdrawals'):
        rows = []
        for month in (1, 2, 3):
            for i, region in enumerate(REGIONS, 1):
                factor = month * i
                # Unequal windows: two baseline days vs three current days.
                values = (100*factor, 75*factor) if table == 'deposits' else (20*factor, 15*factor)
                for timestamp, amount, status in (
                    (f'2026-{month:02d}-01 00:00:00', values[0], 'completed'),
                    (f'2026-{month:02d}-05 23:59:59', values[1], 'completed'),
                    (f'2026-{month:02d}-06 00:00:00', 99999, 'completed'),
                    (f'2026-{month:02d}-03 00:00:00', 99999, 'pending'),
                ):
                    rows.append(dict(customer_id=region, timestamp=timestamp, amount=amount, currency='USD', status=status))
        pd.DataFrame(rows).to_csv(path/f'{table}.csv', index=False)
    pd.DataFrame(columns=['event_id', 'date', 'event_type', 'region', 'affected_team', 'description']).to_csv(path/'business_events.csv', index=False)


def request(path, region='Asia', month=2):
    return InvestigationRequest('net_deposits.v1', region,
        Period(f'2026-{month:02d}-01', f'2026-{month:02d}-02'),
        Period(f'2026-{month:02d}-03', f'2026-{month:02d}-05'),
        'source_naive', 'USD', fingerprint_net_inputs(path).snapshot_id)


def registry_for(result):
    registry = EvidenceRegistry()
    for record in result.evidence:
        registered = registry.register(record['tool_name'], deepcopy(record['parameters']), deepcopy(record['result']), status=record['status'])
        assert registered.evidence_id == record['evidence_id']
    return registry


@pytest.mark.parametrize('backend', ['sqlite', 'duckdb'])
@pytest.mark.parametrize('region', REGIONS)
@pytest.mark.parametrize('month', [1, 2, 3])
def test_real_request_amounts_three_regions_three_windows_and_repeat(tmp_path, backend, region, month):
    bundle(tmp_path)
    req = request(tmp_path, region, month)
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    result = execute_net_cashflows(req, tmp_path, backend=backend)
    factor = (REGIONS.index(region)+1)*month
    assert result.metrics == dict(baseline_net_deposits=80*factor, current_net_deposits=60*factor,
        net_change=-20*factor, deposit_change=-25*factor, withdrawal_change=-5*factor, identity_check=0)
    assert result.request == req.to_dict()
    assert result.snapshot == fingerprint_net_inputs(tmp_path).to_dict()
    assert [c.claim_id for c in result.claims] == ['N-C1', 'N-C2']
    assert result.scope == 'net_cashflow_amounts.v1'
    assert result.claims[0].text.startswith(region + ' net deposits')
    assert 'week over week' not in result.claims[0].text
    for c, verify in zip(result.claims, (verify_net_change, verify_net_decomposition)):
        assert verify(c, registry_for(result), expected_request=req)
        assert not verify(c, registry_for(result))
    again = execute_net_cashflows(InvestigationRequest.from_dict(json.loads(json.dumps(req.to_dict()))), tmp_path, backend=backend)
    assert again.metrics == result.metrics and again.claims == result.claims
    assert again.request == result.request and again.snapshot == result.snapshot
    assert [(e['parameters'], e['result_digest']) for e in again.evidence] == [(e['parameters'], e['result_digest']) for e in result.evidence]
    assert before == {p.name: p.read_bytes() for p in tmp_path.iterdir()}


@pytest.fixture
def executed(tmp_path):
    bundle(tmp_path)
    req = request(tmp_path)
    return req, execute_net_cashflows(req, tmp_path, backend='sqlite')


@pytest.mark.parametrize('field,value', [('region','Europe'), ('baseline_start','2026-02-02'), ('current_end','2026-02-04'), ('currency','EUR'), ('unit','percentage'), ('value',999)])
def test_bound_amount_or_context_tampering_rejected(executed, field, value):
    req, result = executed
    c = result.claims[0]
    binding = replace(c.numeric_binding, **{field:value})
    c = replace(c, numeric_binding=binding, text=render_net_change(binding))
    assert not verify_net_change(c, registry_for(result), expected_request=req)


@pytest.mark.parametrize('source_index', range(4))
@pytest.mark.parametrize('change', ['region', 'start', 'end', 'sql', 'missing_parameters', 'truncated'])
def test_independent_source_query_checks(executed, source_index, change):
    req, result = executed
    registry = registry_for(result)
    driver = registry.get(result.claims[0].numeric_binding.evidence_id)
    source = registry.get(driver.parameters['source_evidence_ids'][source_index])
    if change == 'sql':
        source.parameters['sql'] = source.parameters['sql'].replace("'completed'", "'pending'")
    elif change == 'missing_parameters':
        del source.parameters['bound_parameters']
    elif change == 'truncated':
        payload = deepcopy(source.result); payload['truncated'] = True
        new = registry.register(source.tool_name, source.parameters, payload)
        driver.parameters['source_evidence_ids'][source_index] = new.evidence_id
        result = replace(result, claims=tuple(replace(c, evidence_ids=c.evidence_ids+(new.evidence_id,)) for c in result.claims))
    else:
        source.parameters['bound_parameters'][{'start':0,'end':1,'region':2}[change]] = 'Europe' if change == 'region' else '2026-02-02'
    for c, verify in zip(result.claims, (verify_net_change, verify_net_decomposition)):
        assert not verify(c, registry, expected_request=req)


@pytest.mark.parametrize('change', ['snapshot', 'timezone', 'metric', 'region', 'period', 'missing'])
def test_driver_metadata_cannot_replace_original_request(executed, change):
    req, result = executed
    registry = registry_for(result)
    driver = registry.get(result.claims[0].numeric_binding.evidence_id)
    context = driver.parameters['request']
    if change == 'missing':
        del driver.parameters['request']
    elif change == 'region':
        context['filters']['region'] = 'Europe'
        driver.parameters['region'] = 'Europe'
    elif change == 'period':
        context['baseline']['start'] = '2026-02-02'
        driver.parameters['baseline_start'] = '2026-02-02'
    else:
        context[{'snapshot':'data_snapshot'}.get(change,change)] = 'changed'
    for c, verify in zip(result.claims, (verify_net_change, verify_net_decomposition)):
        assert not verify(c, registry, expected_request=req)


@pytest.mark.parametrize('backend', ['sqlite', 'duckdb'])
@pytest.mark.parametrize('failure', ['snapshot', 'currency', 'schema', 'nonfinite'])
def test_execution_rejects_bad_inputs_without_success_result(tmp_path, backend, failure):
    bundle(tmp_path)
    req = request(tmp_path)
    frame = pd.read_csv(tmp_path/'deposits.csv')
    if failure == 'currency':
        frame['currency'] = 'EUR'
    elif failure == 'schema':
        frame = frame.drop(columns=['status'])
    elif failure == 'nonfinite':
        frame['amount'] = float('inf')
    else:
        frame['amount'] = 999
    frame.to_csv(tmp_path/'deposits.csv',index=False)
    if failure != 'snapshot':
        req = request(tmp_path)
    with pytest.raises(ValueError):
        execute_net_cashflows(req, tmp_path, backend=backend)
