from copy import deepcopy
from dataclasses import replace

import pandas as pd
import pytest

from fitzsight.investigation.net_cashflows import execute_net_cashflows
from fitzsight.investigation.concentration_claims import verify_concentration, render_concentration
from test_net_cashflows import bundle, request, registry_for, REGIONS


def inputs(path, *, zero=False):
    bundle(path)
    customers = pd.read_csv(path/'customers.csv')
    extra = [dict(customer_id=r+'-B', region=r, assigned_team='T') for r in REGIONS]
    pd.concat([customers, pd.DataFrame(extra)]).to_csv(path/'customers.csv', index=False)
    rows = []
    for month in (1, 2, 3):
        for i, region in enumerate(REGIONS, 1):
            factor = month*i
            for customer, amount in ((region,30), (region,20), (region+'-B',10)):
                rows.append(dict(customer_id=customer, timestamp=f'2026-{month:02d}-05 23:59:59',
                    amount=0 if zero else amount*factor, currency='USD', status='completed'))
            for timestamp, status in ((f'2026-{month:02d}-06 00:00:00','completed'),
                                      (f'2026-{month:02d}-04 00:00:00','pending')):
                rows.append(dict(customer_id=region+'-B', timestamp=timestamp, amount=99999,
                                 currency='USD', status=status))
    pd.DataFrame(rows).to_csv(path/'withdrawals.csv', index=False)


@pytest.mark.parametrize('backend', ['sqlite','duckdb'])
@pytest.mark.parametrize('region', REGIONS)
@pytest.mark.parametrize('month', [1,2,3])
def test_three_regions_periods_and_backends(tmp_path, backend, region, month):
    inputs(tmp_path)
    req = request(tmp_path,region,month)
    plain = execute_net_cashflows(req,tmp_path,backend=backend)
    result = execute_net_cashflows(req,tmp_path,backend=backend,top_customers=1)
    again = execute_net_cashflows(req,tmp_path,backend=backend,top_customers=1)
    factor = month*(REGIONS.index(region)+1)
    p = result.metrics['customer_concentration']
    assert p['top_customer_withdrawal_amount'] == 50*factor
    assert p['current_total_withdrawals'] == 60*factor
    assert p['share_of_current_withdrawals'] == pytest.approx(5/6)
    assert result.claims[:2] == plain.claims
    assert {k:v for k,v in result.metrics.items() if k!='customer_concentration'} == plain.metrics
    assert result.scope == 'net_cashflow_concentration.v1'
    assert result.claims[-1].claim_id == 'N-C3'
    assert region in result.claims[-1].text and 'week' not in result.claims[-1].text
    assert result.claims == again.claims and result.metrics == again.metrics
    registry = registry_for(result)
    assert verify_concentration(result.claims[-1],registry,expected_request=req,expected_customer_count=1)
    assert not verify_concentration(result.claims[-1],registry)
    assert sum(e['tool_name']=='read_only_sql' for e in result.evidence)==4


@pytest.mark.parametrize('backend',['sqlite','duckdb'])
@pytest.mark.parametrize('mode',['zero','empty','top_exceeds_customers'])
def test_unavailable_and_top_n_limit(tmp_path,backend,mode):
    inputs(tmp_path,zero=mode=='zero')
    if mode=='empty':
        df=pd.read_csv(tmp_path/'withdrawals.csv').iloc[:0]
        df.to_csv(tmp_path/'withdrawals.csv',index=False)
    req=request(tmp_path)
    result=execute_net_cashflows(req,tmp_path,backend=backend,top_customers=11)
    c=result.claims[-1]
    if mode=='top_exceeds_customers':
        assert c.numeric_binding.value==1
    else:
        assert c.numeric_binding.value is None
        assert c.status=='insufficient_evidence'
    assert verify_concentration(c,registry_for(result),expected_request=req,expected_customer_count=11)


@pytest.mark.parametrize('value',[0,-1,True,1.0,'1',[],{}])
def test_invalid_top_n_rejected_before_loading(tmp_path,value):
    with pytest.raises(ValueError,match='top_customers'):
        execute_net_cashflows(None,tmp_path,backend='sqlite',top_customers=value)


@pytest.fixture
def executed(tmp_path):
    inputs(tmp_path)
    req=request(tmp_path)
    return req, execute_net_cashflows(req,tmp_path,backend='sqlite',top_customers=1)


@pytest.mark.parametrize('change',['region','start','end','snapshot','count','sql','parameters','missing_request','ratio'])
def test_self_consistent_metadata_and_claim_cannot_replace_trusted_inputs(executed,change):
    req,result=executed
    registry=registry_for(result)
    c=result.claims[-1]; b=c.numeric_binding
    old=registry.get(b.evidence_id)
    params=deepcopy(old.parameters); payload=deepcopy(old.result)
    if change=='region':
        params['region']='Europe'; params['request']['filters']['region']='Europe'; b=replace(b,region='Europe')
    elif change in ('start','end'):
        field='period_start' if change=='start' else 'period_end_exclusive'
        params[field]='2026-02-04'; b=replace(b,**{field:params[field]})
    elif change=='snapshot':
        params['request']['data_snapshot']='sha256:'+'f'*64
    elif change=='count':
        params['customer_count']=2; payload['customer_count']=2
        payload.update(top_customer_withdrawal_amount=b.denominator,share_of_current_withdrawals=1)
        b=replace(b,customer_count=2,numerator=b.denominator,value=1)
    elif change=='missing_request':
        del params['request']
    elif change=='ratio':
        payload.update(top_customer_withdrawal_amount=59*4,share_of_current_withdrawals=59/60)
        b=replace(b,numerator=59*4,value=59/60)
    else:
        source=registry.get(b.source_evidence_id)
        if change=='sql': source.parameters['sql']=source.parameters['sql'].replace("'completed'","'pending'")
        else: source.parameters['bound_parameters'][2]='Europe'
    new=registry.register(old.tool_name,params,payload)
    b=replace(b,evidence_id=new.evidence_id)
    c=replace(c,numeric_binding=b,text=render_concentration(b),evidence_ids=c.evidence_ids+(new.evidence_id,))
    assert not verify_concentration(c,registry,expected_request=req,expected_customer_count=1)


@pytest.mark.parametrize('backend',['sqlite','duckdb'])
def test_negative_withdrawals_do_not_emit_concentration(tmp_path,backend):
    inputs(tmp_path)
    df=pd.read_csv(tmp_path/'withdrawals.csv'); df['amount']=-df['amount']
    df.to_csv(tmp_path/'withdrawals.csv',index=False)
    with pytest.raises(ValueError,match='nonnegative'):
        execute_net_cashflows(request(tmp_path),tmp_path,backend=backend,top_customers=1)
