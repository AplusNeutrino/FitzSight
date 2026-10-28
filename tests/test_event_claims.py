from dataclasses import replace
from datetime import date, datetime
import pytest
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.investigation.models import Claim
from fitzsight.investigation.event_claims import EventBinding, event_query, render_event, verify_event


def make_event(registry, rows=None):
    rows = [] if rows is None else rows
    source = registry.register('read_only_sql', {'sql': event_query('2026-08-03', '2026-08-08')},
                               {'rows': rows, 'truncated': False, 'row_count': len(rows)})
    ids = tuple(sorted(r['event_id'] for r in rows if r['region'] == 'Europe'
        and r['event_type'] == 'HIGH_VALUE_WITHDRAWAL_CLUSTER'
        and '2026-08-03' <= str(r['date']) < '2026-08-08'))
    b = EventBinding(source.evidence_id, ids)
    return Claim('N-C5', render_event(b), 'supported_with_guardrail' if ids else 'insufficient_evidence',
                 'high' if ids else 'low', (source.evidence_id,), event_binding=b)


def row(**changes):
    return dict(dict(event_id='event-a', date='2026-08-05', region='Europe',
                     event_type='HIGH_VALUE_WITHDRAWAL_CLUSTER'), **changes)


@pytest.mark.parametrize('rows', [[], [row()], [row(date=date(2026,8,3))], [row(date="2026-08-05 00:00:00")],
    [row(date=datetime(2026,8,5,12))],
    [row(date='2026-08-08')], [row(region='Asia')], [row(event_type='OTHER')],
    [row(), row(event_id='event-b')]])
def test_recompute_matches_from_full_rows(rows):
    registry = EvidenceRegistry()
    assert verify_event(make_event(registry, rows), registry)


@pytest.mark.parametrize('field,value', [('region','Asia'), ('event_type','OTHER'),
    ('period_start','2026-08-04'), ('period_end_exclusive','2026-08-09'),
    ('metric_id','other'), ('evidence_id','E9999'), ('matched_event_ids',('fake',)),
    ('matched_event_ids',()), ('matched_event_ids',('event-a','event-a')),
    ('matched_event_ids',True)])
def test_binding_tampering_rejected(field, value):
    registry = EvidenceRegistry(); c = make_event(registry, [row()])
    b = replace(c.event_binding, **{field:value})
    assert not verify_event(replace(c, event_binding=b), registry)


@pytest.mark.parametrize('changes', [dict(text='事件肯定导致提款'), dict(status='supported'),
    dict(confidence='low'), dict(event_binding=None), dict(evidence_ids=()), dict(claim_id='OTHER')])
def test_claim_tampering_rejected(changes):
    registry = EvidenceRegistry(); c = make_event(registry, [row()])
    assert not verify_event(replace(c, **changes), registry)


@pytest.mark.parametrize('mode', ['truncated','count','compact','duplicate','bad_date','timezone','missing_field','wrong_tool','wrong_sql','failed','digest'])
def test_invalid_source_fails_closed(mode):
    registry = EvidenceRegistry(); c = make_event(registry, [row()])
    original = registry.get(c.event_binding.evidence_id)
    payload = dict(original.result); params = dict(original.parameters)
    if mode == 'truncated': payload['truncated'] = True
    if mode == 'count': payload['row_count'] = 100
    if mode == 'compact': del payload['rows']
    if mode == 'duplicate': payload.update(rows=[row(),row()],row_count=2)
    if mode == 'timezone': payload['rows'] = [row(date='2026-08-05T00:00:00+08:00')]
    if mode == 'bad_date': payload['rows'] = [row(date='invalid')]
    if mode == 'missing_field': payload['rows'] = [{}]
    if mode == 'wrong_sql': params['sql'] = 'SELECT * FROM business_events'
    source = registry.register('other' if mode == 'wrong_tool' else 'read_only_sql', params, payload,
                               status='error' if mode == 'failed' else 'success')
    if mode == 'digest': payload['rows'] = []
    b = replace(c.event_binding, evidence_id=source.evidence_id)
    assert not verify_event(replace(c,event_binding=b,evidence_ids=(source.evidence_id,)),registry)


def test_consistent_false_absence_and_text_rejected_by_source():
    registry = EvidenceRegistry(); c = make_event(registry, [row()])
    b = replace(c.event_binding, matched_event_ids=())
    assert not verify_event(replace(c,event_binding=b,text=render_event(b),
                                    status='insufficient_evidence',confidence='low'),registry)


@pytest.mark.parametrize('mode', ['delete','duplicate','binding','text'])
def test_net_investigation_requires_one_valid_event_claim(mode):
    from test_numeric_claims import fixture
    from fitzsight.agent.verifier import EvidenceClaimVerifier
    registry,result = fixture()
    assert EvidenceClaimVerifier(registry).verify(result).passed
    c = result.claims[-1]
    replacements = {'delete': (), 'duplicate': (c,c),
                    'binding': (replace(c,event_binding=None),), 'text': (replace(c,text='事件存在'),)}
    report = EvidenceClaimVerifier(registry).verify(replace(result,claims=result.claims[:-1]+replacements[mode]))
    assert not report.passed
    check = 'event_required' if mode in ('delete','duplicate') else 'event_binding:N-C5'
    assert any(x.check_id == check and not x.passed for x in report.checks)
