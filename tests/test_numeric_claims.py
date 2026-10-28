from dataclasses import replace

import pytest
from test_concentration_claims import make_claim
from test_regional_claims import make_regional
from test_event_claims import make_event

from fitzsight.agent.verifier import EvidenceClaimVerifier
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.investigation.models import Claim, InvestigationPlan, InvestigationResult
from fitzsight.investigation.numeric_claims import NetChangeBinding, NetDecompositionBinding, render_net_change, render_net_decomposition


def fixture():
    registry = EvidenceRegistry()
    sources = [registry.register('read_only_sql', {}, {'rows': [{'amount': amount, 'currency': 'USD'}]})
               for amount in (100.0, 20.0, 75.0, 15.0)]
    context = dict(baseline_start='2026-07-27', baseline_end='2026-08-02',
                   current_start='2026-08-03', current_end='2026-08-09')
    driver = registry.register('net_deposit_driver_decomposition',
        dict(context, region='Europe', currency='USD', source_evidence_ids=[s.evidence_id for s in sources]),
        {'net_change': -20.0, 'deposit_change': -25.0, 'withdrawal_change': -5.0})
    binding = NetChangeBinding(value=-20.0, evidence_id=driver.evidence_id, **context)
    claim = Claim('N-C1', render_net_change(binding), 'supported', 'high',
                  tuple(s.evidence_id for s in sources) + (driver.evidence_id,), binding)
    decomposition = NetDecompositionBinding(value=-20.0, deposit_change=-25.0,
        withdrawal_change=-5.0, evidence_id=driver.evidence_id, **context)
    second = Claim('N-C2', render_net_decomposition(decomposition), 'supported', 'high',
                   claim.evidence_ids, decomposition)
    result = InvestigationResult('FitzSight', 'test', 'test',
        InvestigationPlan('net_deposit_anomaly_investigation', 'test', ()),
        (claim, second, make_claim(registry), make_regional(registry), make_event(registry)), {}, {}, ())
    return registry, result


def test_hand_calculated_net_change_accepts_and_serializes_binding():
    registry, result = fixture()
    assert EvidenceClaimVerifier(registry).verify(result).passed
    assert result.to_dict()['claims'][0]['numeric_binding']['value'] == -20


@pytest.mark.parametrize('field,value', [
    ('value', 99.0), ('value', float('nan')), ('value', float('inf')), ('value', True), ('value', '99'), ('value', 10**1000),
    ('unit', 'percent'), ('currency', 'EUR'), ('metric_id', 'conversion_rate'),
    ('evidence_field', 'deposit_change'), ('region', 'Asia'),
    ('baseline_start', '2026-07-28'), ('baseline_end', '2026-08-01'),
    ('current_start', '2026-08-04'), ('current_end', '2026-08-10'),
    ('evidence_id', 'E0001'), ('evidence_id', 'E9999'),
])
def test_binding_tampering_rejected_even_with_original_valid_evidence(field, value):
    registry, result = fixture()
    claim = result.claims[0]
    changed = replace(claim, numeric_binding=replace(claim.numeric_binding, **{field: value}))
    assert not EvidenceClaimVerifier(registry).verify(replace(result, claims=(changed, result.claims[1], result.claims[2], result.claims[3], result.claims[4]))).passed


@pytest.mark.parametrize('text', ['Net deposits changed by $99.00.', '净入金变化为99%。',
                                 'Net deposits changed by €20.00.'])
def test_free_text_number_or_unit_tampering_rejected(text):
    registry, result = fixture()
    claim = replace(result.claims[0], text=text)
    assert not EvidenceClaimVerifier(registry).verify(replace(result, claims=(claim, result.claims[1], result.claims[2], result.claims[3], result.claims[4]))).passed


def test_consistently_wrong_value_and_rendering_still_rejected():
    registry, result = fixture()
    b = replace(result.claims[0].numeric_binding, value=99.0)
    c = replace(result.claims[0], numeric_binding=b, text=render_net_change(b))
    assert not EvidenceClaimVerifier(registry).verify(replace(result, claims=(c, result.claims[1], result.claims[2], result.claims[3], result.claims[4]))).passed


@pytest.mark.parametrize('change', ['binding', 'claim', 'duplicate', 'source_reference'])
def test_contract_cannot_be_removed_or_duplicated(change):
    registry, result = fixture()
    c = result.claims[0]
    claims = {'binding': (replace(c, numeric_binding=None),), 'claim': (),
              'duplicate': (c, c), 'source_reference': (replace(c, evidence_ids=c.evidence_ids[1:]),)}[change]
    assert not EvidenceClaimVerifier(registry).verify(replace(result, claims=claims + (result.claims[1], result.claims[2], result.claims[3], result.claims[4]))).passed


def test_internally_consistent_but_wrong_driver_rejected_by_source_recalculation():
    registry, result = fixture()
    original = registry.get(result.claims[0].numeric_binding.evidence_id)
    fake = registry.register(original.tool_name, original.parameters, {'net_change': 99.0})
    b = replace(result.claims[0].numeric_binding, value=99.0, evidence_id=fake.evidence_id)
    c = replace(result.claims[0], numeric_binding=b, text=render_net_change(b),
                evidence_ids=result.claims[0].evidence_ids + (fake.evidence_id,))
    assert not EvidenceClaimVerifier(registry).verify(replace(result, claims=(c, result.claims[1], result.claims[2], result.claims[3], result.claims[4]))).passed


def test_net_engine_refuses_non_usd_source_instead_of_labeling_it_dollars():
    from datetime import date
    from types import SimpleNamespace
    from fitzsight.investigation.net_deposit import NetDepositInvestigationEngine
    class SQL:
        def run(self, sql):
            return SimpleNamespace(data={'rows': [{'amount': 100, 'currency': 'EUR'}]})
    engine = NetDepositInvestigationEngine(schema_tool=None, sql_tool=SQL(), registry=EvidenceRegistry())
    with pytest.raises(ValueError, match='requires USD'):
        engine._money_rows('deposits', region='Europe', start=date(2026, 7, 27), end=date(2026, 8, 2))


@pytest.mark.parametrize('field,value', [
    ('deposit_change', 99.0), ('withdrawal_change', 99.0),
    ('deposit_change', float('nan')), ('withdrawal_change', float('inf')),
    ('deposit_change', True), ('withdrawal_change', '99'),
    ('deposit_change', 10**1000), ('value', 0),
    ('unit', 'percent'), ('currency', 'EUR'), ('region', 'Asia'),
    ('baseline_start', '2026-07-28'), ('current_end', '2026-08-10'),
    ('metric_id', 'net_deposit_change.v1'), ('evidence_field', 'deposit_change'),
    ('evidence_id', 'E9999'),
])
def test_decomposition_binding_tampering_fails_specific_check(field, value):
    registry, result = fixture()
    c = result.claims[1]
    changed = replace(c, numeric_binding=replace(c.numeric_binding, **{field: value}))
    report = EvidenceClaimVerifier(registry).verify(replace(result, claims=(result.claims[0], changed, result.claims[2], result.claims[3], result.claims[4])))
    assert not report.passed
    assert any(c.check_id == 'numeric_binding:N-C2' and not c.passed for c in report.checks)


def test_compensating_wrong_components_with_matching_text_and_driver_rejected():
    registry, result = fixture()
    c = result.claims[1]
    original = registry.get(c.numeric_binding.evidence_id)
    # The net remains -20, so checking only the net or driver digest would miss this.
    fake = registry.register(original.tool_name, original.parameters,
                             dict(net_change=-20.0, deposit_change=75.0, withdrawal_change=95.0))
    b = replace(c.numeric_binding, deposit_change=75.0, withdrawal_change=95.0,
                evidence_id=fake.evidence_id)
    changed = replace(c, numeric_binding=b, text=render_net_decomposition(b),
                      evidence_ids=c.evidence_ids + (fake.evidence_id,))
    report = EvidenceClaimVerifier(registry).verify(replace(result, claims=(result.claims[0], changed, result.claims[2], result.claims[3], result.claims[4])))
    assert not report.passed
    assert any(c.check_id == 'numeric_binding:N-C2' and not c.passed for c in report.checks)


@pytest.mark.parametrize('change', ['binding', 'claim', 'duplicate', 'source_reference', 'text', 'wrong_type'])
def test_decomposition_contract_cannot_be_bypassed(change):
    registry, result = fixture()
    c = result.claims[1]
    replacements = {
        'binding': (replace(c, numeric_binding=None),),
        'claim': (), 'duplicate': (c, c),
        'source_reference': (replace(c, evidence_ids=c.evidence_ids[1:]),),
        'text': (replace(c, text='存款增加99%，提款减少。'),),
        'wrong_type': (replace(c, numeric_binding=result.claims[0].numeric_binding),),
    }
    assert not EvidenceClaimVerifier(registry).verify(
        replace(result, claims=(result.claims[0], result.claims[2], result.claims[3], result.claims[4]) + replacements[change])).passed


def test_decomposition_hand_calculation_and_serialization():
    registry, result = fixture()
    assert EvidenceClaimVerifier(registry).verify(result).passed
    binding = result.to_dict()['claims'][1]['numeric_binding']
    assert binding['deposit_change'] == 75 - 100
    assert binding['withdrawal_change'] == 15 - 20
    assert binding['value'] == -25 - (-5)


@pytest.mark.parametrize("mode", ["remove", "duplicate"])
def test_required_concentration_claim(mode):
    registry, result = fixture()
    claims = (result.claims[:2] + result.claims[3:]) if mode == "remove" else result.claims + (result.claims[2],)
    report = EvidenceClaimVerifier(registry).verify(replace(result, claims=claims))
    assert not report.passed
    assert any(c.check_id == "concentration_required" and not c.passed for c in report.checks)


@pytest.mark.parametrize("mode", ["remove", "duplicate"])
def test_required_regional_claim(mode):
    registry, result = fixture()
    claims = result.claims[:3] + result.claims[4:] if mode == "remove" else result.claims + (result.claims[3],)
    report = EvidenceClaimVerifier(registry).verify(replace(result, claims=claims))
    assert not report.passed
    assert any(c.check_id == "regional_required" and not c.passed for c in report.checks)
