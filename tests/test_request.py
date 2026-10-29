from copy import deepcopy
from dataclasses import FrozenInstanceError
import json
import pytest
from fitzsight.investigation.request import InvestigationRequest, Period


def payload():
    return dict(metric='net_deposits.v1', filters={'region': 'Europe'},
        baseline={'start': '2026-07-27', 'end': '2026-08-02'},
        current={'start': '2026-08-03', 'end': '2026-08-09'},
        timezone='source_naive', currency='USD', data_snapshot='sha256:' + 'a'*64)


@pytest.mark.parametrize('region', ['Europe', 'Asia', 'Americas'])
@pytest.mark.parametrize('month', ['01', '02', '03'])
def test_request_roundtrip_three_regions_and_periods(region, month):
    p = payload(); p['filters']['region'] = region
    p['baseline'] = dict(start=f'2026-{month}-01', end=f'2026-{month}-07')
    p['current'] = dict(start=f'2026-{month}-08', end=f'2026-{month}-14')
    r = InvestigationRequest.from_dict(p)
    assert InvestigationRequest.from_dict(json.loads(json.dumps(r.to_dict()))) == r
    p['filters']['region'] = 'changed'
    assert r.region == region
    with pytest.raises(FrozenInstanceError):
        r.region = 'Asia'


@pytest.mark.parametrize('field,value', [
    ('metric','profit.v1'), ('currency','EUR'), ('timezone','UTC'),
    ('data_snapshot',''), ('data_snapshot','sha256:'+'g'*64),
    ('filters',{'region':"Europe' OR 1=1"}), ('filters',{'region':'Europe','channel':'x'}),
    ('filters',[]), ('baseline',{'start':'2026-07-27'}),
    ('baseline',{'start':'2026-02-30','end':'2026-03-01'}),
    ('baseline',{'start':'2026-08-04','end':'2026-08-02'}),
    ('baseline',{'start':'2026-08-02','end':'2026-08-03'}),
    ('current',{'start':'2026-8-3','end':'2026-08-09'}),
    ('current',{'start':'2026-08-03T00:00:00','end':'2026-08-09'}),
    ('current',{'start':True,'end':'2026-08-09'}),
    ('current',{'start':'9999-12-30','end':'9999-12-31'}),
])
def test_invalid_request_rejected(field, value):
    p = payload(); p[field] = value
    with pytest.raises(ValueError):
        InvestigationRequest.from_dict(p)


@pytest.mark.parametrize('field', list(payload()))
def test_missing_fields_rejected(field):
    p = payload(); del p[field]
    with pytest.raises(ValueError):
        InvestigationRequest.from_dict(p)


def test_extra_fields_and_unvalidated_period_rejected():
    p = payload(); p['sql'] = 'SELECT 1'
    with pytest.raises(ValueError):
        InvestigationRequest.from_dict(p)
    with pytest.raises(ValueError):
        InvestigationRequest('net_deposits.v1','Europe',{},Period('2026-08-03','2026-08-09'),'source_naive','USD','sha256:'+'a'*64)
