from copy import deepcopy
from dataclasses import replace
from statistics import median

import pandas as pd
import pytest

from fitzsight.investigation.net_cashflows import execute_net_cashflows
from fitzsight.investigation.regional_claims import verify_regional, render_regional
from test_net_cashflows import bundle, request, registry_for, REGIONS


def inputs(path):
    bundle(path)
    frame = pd.read_csv(path/'customers.csv')
    dormant = [dict(customer_id=f'{r}-{j}',region=r,assigned_team='T')
               for i,r in enumerate(REGIONS,1) for j in range(i)]
    pd.concat([frame,pd.DataFrame(dormant)]).to_csv(path/'customers.csv',index=False)


@pytest.mark.parametrize('backend',['sqlite','duckdb'])
@pytest.mark.parametrize('region',REGIONS)
@pytest.mark.parametrize('month',[1,2,3])
def test_request_regional_hand_values_and_repeat(tmp_path,backend,region,month):
    inputs(tmp_path)
    req=request(tmp_path,region,month)
    plain=execute_net_cashflows(req,tmp_path,backend=backend,top_customers=1)
    result=execute_net_cashflows(req,tmp_path,backend=backend,top_customers=1,include_regional=True)
    again=execute_net_cashflows(req,tmp_path,backend=backend,top_customers=1,include_regional=True)
    expected={r:-20*i*month/(i+1) for i,r in enumerate(REGIONS,1)}
    p=result.metrics['regional_control']
    assert p['net_deposit_per_customer_change']==pytest.approx(expected)
    assert p['target_change']==pytest.approx(expected[region])
    assert p['other_region_median_change']==pytest.approx(median(v for r,v in expected.items() if r!=region))
    assert p['control_region_count']==2 and p['calculation_status']=='computed'
    assert 'europe_change' not in p
    assert result.scope=='net_cashflow_regional.v1'
    assert result.claims[:3]==plain.claims
    assert result.claims==again.claims and result.metrics==again.metrics
    assert len(result.claims)==4 and result.claims[-1].claim_id=='N-C4'
    assert region in result.claims[-1].text and 'weekly' not in result.claims[-1].text
    assert sum(e['tool_name']=='read_only_sql' for e in result.evidence)==8
    b=result.claims[-1].numeric_binding
    assert {r.region:r.customer_count for r in b.current}==dict(zip(REGIONS,[2,3,4]))
    assert verify_regional(result.claims[-1],registry_for(result),expected_request=req)
    assert not verify_regional(result.claims[-1],registry_for(result))


@pytest.mark.parametrize('backend',['sqlite','duckdb'])
@pytest.mark.parametrize('mode',['missing_target','no_controls','zero','foreign_currency'])
def test_missing_and_true_zero_are_distinct(tmp_path,backend,mode):
    inputs(tmp_path)
    if mode in ('missing_target','no_controls'):
        customers=pd.read_csv(tmp_path/'customers.csv')
        customers=customers[customers.region.ne('Asia') if mode=='missing_target' else customers.region.eq('Asia')]
        customers.to_csv(tmp_path/'customers.csv',index=False)
        for table in ('deposits','withdrawals'):
            f=pd.read_csv(tmp_path/f'{table}.csv'); f=f[f.customer_id.isin(customers.customer_id)]
            f.to_csv(tmp_path/f'{table}.csv',index=False)
    elif mode=='zero':
        for table in ('deposits','withdrawals'):
            f=pd.read_csv(tmp_path/f'{table}.csv'); f['amount']=0
            f.to_csv(tmp_path/f'{table}.csv',index=False)
    else:
        f=pd.read_csv(tmp_path/'deposits.csv'); f.loc[f.customer_id.eq('Europe'),'currency']='EUR'
        f.to_csv(tmp_path/'deposits.csv',index=False)
    req=request(tmp_path)
    if mode=='foreign_currency':
        with pytest.raises(ValueError,match='USD'):
            execute_net_cashflows(req,tmp_path,backend=backend,include_regional=True)
        return
    result=execute_net_cashflows(req,tmp_path,backend=backend,include_regional=True)
    c=result.claims[-1]; p=result.metrics['regional_control']
    assert verify_regional(c,registry_for(result),expected_request=req)
    if mode=='zero':
        assert p['target_change']==0 and p['other_region_median_change']==0
        assert c.status=='supported'
    else:
        assert c.status=='insufficient_evidence'
        assert p['unavailable_reason']==('missing_target_region' if mode=='missing_target' else 'missing_control_regions')
        assert p['target_change' if mode=='missing_target' else 'other_region_median_change'] is None


@pytest.fixture
def executed(tmp_path):
    inputs(tmp_path)
    req=request(tmp_path)
    return req,execute_net_cashflows(req,tmp_path,backend='sqlite',include_regional=True)


@pytest.mark.parametrize('index',range(4))
@pytest.mark.parametrize('change',['sql','start','end','missing','truncated'])
def test_four_source_contexts_fail_independently(executed,index,change):
    req,result=executed; registry=registry_for(result); c=result.claims[-1]; b=c.numeric_binding
    source=registry.get(b.source_evidence_ids[index])
    if change=='sql': source.parameters['sql']=source.parameters['sql'].replace("'completed'","'pending'")
    elif change=='missing': del source.parameters['bound_parameters']
    elif change in ('start','end'): source.parameters['bound_parameters'][0 if change=='start' else 1]='2026-02-02'
    else:
        payload=deepcopy(source.result); payload['truncated']=True
        new=registry.register(source.tool_name,source.parameters,payload)
        ids=list(b.source_evidence_ids);ids[index]=new.evidence_id
        record=registry.get(b.evidence_id);record.parameters['source_evidence_ids']=ids
        b=replace(b,source_evidence_ids=tuple(ids)); c=replace(c,numeric_binding=b,evidence_ids=c.evidence_ids+(new.evidence_id,))
    assert not verify_regional(c,registry,expected_request=req)


@pytest.mark.parametrize('change',['region','baseline','current','snapshot','missing_request','amount'])
def test_claim_and_metadata_cannot_override_original_request(executed,change):
    req,result=executed; registry=registry_for(result); c=result.claims[-1]; b=c.numeric_binding
    record=registry.get(b.evidence_id); params=deepcopy(record.parameters); payload=deepcopy(record.result)
    if change=='region':
        params['region']='Europe';params['request']['filters']['region']='Europe';b=replace(b,region='Europe')
    elif change in ('baseline','current'):
        field=change+'_start';params[field]='2026-02-02';params['request'][change]['start']='2026-02-02'
        b=replace(b,**{field:'2026-02-02'})
    elif change=='snapshot':params['request']['data_snapshot']='sha256:'+'e'*64
    elif change=='missing_request':del params['request']
    else:
        payload['target_change']=999;b=replace(b,value=999)
    new=registry.register(record.tool_name,params,payload);b=replace(b,evidence_id=new.evidence_id)
    c=replace(c,numeric_binding=b,text=render_regional(b),evidence_ids=c.evidence_ids+(new.evidence_id,))
    assert not verify_regional(c,registry,expected_request=req)


@pytest.mark.parametrize('value',[1,0,'yes',None,[]])
def test_flag_requires_bool_before_loading(tmp_path,value):
    with pytest.raises(ValueError,match='include_regional'):
        execute_net_cashflows(None,tmp_path,backend='sqlite',include_regional=value)
