from dataclasses import FrozenInstanceError, replace
import json

import pandas as pd
import pytest

from fitzsight.data.store import AnalyticsStore
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.investigation.event_selection import EventSelection, event_lookup_query
from fitzsight.investigation.request import Period
from fitzsight.tools.sql import ReadOnlySQLTool
from test_net_cashflows import REGIONS, bundle, request

TYPE = 'HIGH_VALUE_WITHDRAWAL_CLUSTER'


def test_selection_roundtrip_immutable_and_no_defaults():
    value = dict(event_type=TYPE, period=dict(start='2026-02-01', end='2026-02-03'))
    selection = EventSelection.from_dict(value)
    assert EventSelection.from_dict(json.loads(json.dumps(selection.to_dict()))) == selection
    value['period']['start'] = 'changed'
    output = selection.to_dict(); output['period']['end'] = 'changed'
    assert selection.period == Period('2026-02-01', '2026-02-03')
    with pytest.raises(FrozenInstanceError):
        selection.event_type = 'OTHER'
    with pytest.raises(TypeError):
        EventSelection()


@pytest.mark.parametrize('value', [None, [], {}, {'event_type': TYPE},
    {'event_type': TYPE, 'period': {'start':'2026-02-01','end':'2026-02-03'}, 'region':'Asia'},
    {'event_type': TYPE, 'period': {'start':'2026-02-01','end':'2026-02-03','extra':True}},
    {'event_type': TYPE, 'period': None}])
def test_strict_fields(value):
    with pytest.raises(ValueError):
        EventSelection.from_dict(value)


@pytest.mark.parametrize('value', ['OTHER', '', None, True, 1, "x' OR 1=1 --"])
def test_unknown_type_rejected(value):
    with pytest.raises(ValueError):
        EventSelection(value, Period('2026-02-01','2026-02-03'))


@pytest.mark.parametrize('start,end', [('2026-02-30','2026-03-01'),
    ('2026-02-03','2026-02-01'), ('2026-2-1','2026-02-03'),
    ('2026-02-01T00:00:00+08:00','2026-02-03'), ('9999-12-31','9999-12-31')])
def test_invalid_dates_rejected(start, end):
    with pytest.raises(ValueError):
        EventSelection.from_dict(dict(event_type=TYPE, period=dict(start=start,end=end)))


@pytest.mark.parametrize('backend', ['sqlite', 'duckdb'])
@pytest.mark.parametrize('region', REGIONS)
@pytest.mark.parametrize('month', [1,2,3])
def test_actual_bound_lookup_regions_windows_and_boundaries(tmp_path, backend, region, month):
    bundle(tmp_path)
    rows = []
    for m in (1,2,3):
        for r in REGIONS:
            for suffix, day, kind in [('before','02 23:59:59',TYPE), ('a','03 00:00:00',TYPE),
                ('b','03 00:00:00',TYPE), ('last','05 23:59:59',TYPE),
                ('after','06 00:00:00',TYPE), ('wrong','04 00:00:00','OTHER')]:
                rows.append(dict(event_id=f'{m}-{r}-{suffix}',date=f'2026-{m:02d}-{day}',
                                 event_type=kind,region=r,affected_team='T',description='context'))
    # Reverse input: tie order must come from the approved ORDER BY, not CSV order.
    pd.DataFrame(rows[::-1]).to_csv(tmp_path/'business_events.csv',index=False)
    req = request(tmp_path,region,month)
    selection = EventSelection(TYPE, req.current)
    sql, params = event_lookup_query(req, selection)
    assert params == (region,TYPE,f'2026-{month:02d}-03',f'2026-{month:02d}-06')
    assert region not in sql and TYPE not in sql and '2026' not in sql
    before = {p.name:p.read_bytes() for p in tmp_path.iterdir()}
    with AnalyticsStore(tmp_path, backend=backend) as store:
        store.load_csv_directory()
        registry = EvidenceRegistry(); tool = ReadOnlySQLTool(store,registry)
        first = tool.run(sql, parameters=params)
        second = tool.run(sql, parameters=params)
        assert [r['event_id'] for r in first.data['rows']] == [f'{month}-{region}-{s}' for s in ('a','b','last')]
        assert first.data == second.data
        assert first.data['truncated'] is False
        assert registry.get(first.evidence_id).parameters['bound_parameters'] == list(params)
        # Deliberately separate event window from the cashflow current period.
        absent = replace(selection, period=Period('2025-01-01','2025-01-01'))
        empty_sql, empty_params = event_lookup_query(req, absent)
        assert tool.run(empty_sql,parameters=empty_params).data['rows'] == []
    assert before == {p.name:p.read_bytes() for p in tmp_path.iterdir()}


@pytest.mark.parametrize('bad_request,bad_selection', [(True,False),(False,True),(True,True)])
def test_query_requires_validated_objects(tmp_path,bad_request,bad_selection):
    bundle(tmp_path); req=request(tmp_path)
    selection=EventSelection(TYPE,req.current)
    with pytest.raises(ValueError):
        event_lookup_query(req.to_dict() if bad_request else req,
                           selection.to_dict() if bad_selection else selection)
