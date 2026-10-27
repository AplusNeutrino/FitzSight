from dataclasses import replace

import pytest

from fitzsight.agent.verifier import EvidenceClaimVerifier
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.investigation.models import Claim, InvestigationPlan, InvestigationResult
from fitzsight.investigation.numeric_claims import NetChangeBinding, render_net_change


def fixture():
    registry = EvidenceRegistry()
    sources = [registry.register('read_only_sql', {}, {'rows': [{'amount': amount, 'currency': 'USD'}]})
               for amount in (100.0, 20.0, 75.0, 15.0)]
    context = dict(baseline_start='2026-07-27', baseline_end='2026-08-02',
                   current_start='2026-08-03', current_end='2026-08-09')
    driver = registry.register('net_deposit_driver_decomposition',
        dict(context, region='Europe', currency='USD', source_evidence_ids=[s.evidence_id for s in sources]),
        {'net_change': -20.0})
    binding = NetChangeBinding(value=-20.0, evidence_id=driver.evidence_id, **context)
    claim = Claim('N-C1', render_net_change(binding), 'supported', 'high',
                  tuple(s.evidence_id for s in sources) + (driver.evidence_id,), binding)
    result = InvestigationResult('FitzSight', 'test', 'test',
        InvestigationPlan('net_deposit_anomaly_investigation', 'test', ()),
        (claim,), {}, {}, ())
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
    assert not EvidenceClaimVerifier(registry).verify(replace(result, claims=(changed,))).passed


@pytest.mark.parametrize('text', ['Net deposits changed by $99.00.', '净入金变化为99%。',
                                 'Net deposits changed by €20.00.'])
def test_free_text_number_or_unit_tampering_rejected(text):
    registry, result = fixture()
    claim = replace(result.claims[0], text=text)
    assert not EvidenceClaimVerifier(registry).verify(replace(result, claims=(claim,))).passed


def test_consistently_wrong_value_and_rendering_still_rejected():
    registry, result = fixture()
    b = replace(result.claims[0].numeric_binding, value=99.0)
    c = replace(result.claims[0], numeric_binding=b, text=render_net_change(b))
    assert not EvidenceClaimVerifier(registry).verify(replace(result, claims=(c,))).passed


@pytest.mark.parametrize('change', ['binding', 'claim', 'duplicate', 'source_reference'])
def test_contract_cannot_be_removed_or_duplicated(change):
    registry, result = fixture()
    c = result.claims[0]
    claims = {'binding': (replace(c, numeric_binding=None),), 'claim': (),
              'duplicate': (c, c), 'source_reference': (replace(c, evidence_ids=c.evidence_ids[1:]),)}[change]
    assert not EvidenceClaimVerifier(registry).verify(replace(result, claims=claims)).passed


def test_internally_consistent_but_wrong_driver_rejected_by_source_recalculation():
    registry, result = fixture()
    original = registry.get(result.claims[0].numeric_binding.evidence_id)
    fake = registry.register(original.tool_name, original.parameters, {'net_change': 99.0})
    b = replace(result.claims[0].numeric_binding, value=99.0, evidence_id=fake.evidence_id)
    c = replace(result.claims[0], numeric_binding=b, text=render_net_change(b),
                evidence_ids=result.claims[0].evidence_ids + (fake.evidence_id,))
    assert not EvidenceClaimVerifier(registry).verify(replace(result, claims=(c,))).passed


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
