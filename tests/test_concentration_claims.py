from dataclasses import replace
import pytest

from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.investigation.models import Claim
from fitzsight.investigation.concentration_claims import (
    ConcentrationBinding, render_concentration, verify_concentration,
)


def make_claim(registry, amounts=(30, 20, 10)):
    # Customer A has two withdrawals; largest customer is 50 of total 60.
    source = registry.register("read_only_sql", {}, {"rows": [
        {"customer_id": customer, "amount": amount, "currency": "USD"}
        for customer, amount in zip(("A", "A", "B"), amounts)
    ]})
    total = sum(amounts)
    top = sum(amounts[:2])
    value = top / total if total else None
    context = dict(customer_count=1, period_start="2026-08-03 00:00:00",
                   period_end_exclusive="2026-08-10 00:00:00", region="Europe",
                   currency="USD", source_evidence_id=source.evidence_id)
    evidence = registry.register("withdrawal_customer_concentration", context, {
        "customer_count": 1, "top_customer_withdrawal_amount": top,
        "current_total_withdrawals": total, "share_of_current_withdrawals": value,
        "calculation_status": "computed" if total else "unavailable",
        "unavailable_reason": None if total else "nonpositive_total_withdrawals",
    })
    binding = ConcentrationBinding(value=value, numerator=top, denominator=total,
                                    evidence_id=evidence.evidence_id, **context)
    return Claim("N-C3", render_concentration(binding),
                 "supported" if total else "insufficient_evidence", "high",
                 (source.evidence_id, evidence.evidence_id), binding)


@pytest.mark.parametrize("amounts", [(30, 20, 10), (0, 0, 0), ()])
def test_hand_aggregation_and_unavailable(amounts):
    registry = EvidenceRegistry()
    assert verify_concentration(make_claim(registry, amounts), registry)


@pytest.mark.parametrize("field,value", [
    ("value", .99), ("numerator", 59), ("denominator", 99),
    ("value", float("nan")), ("numerator", float("inf")),
    ("denominator", True), ("numerator", "50"),
    ("customer_count", 2), ("customer_count", True), ("customer_count", 0),
    ("unit", "percent"), ("currency", "EUR"), ("region", "Asia"),
    ("period_start", "2026-08-04"), ("period_end_exclusive", "2026-08-09"),
    ("metric_id", "wrong"), ("evidence_field", "other"),
    ("source_evidence_id", "E9999"), ("evidence_id", "E9999"),
])
def test_tampering_rejected(field, value):
    registry = EvidenceRegistry()
    claim = make_claim(registry)
    assert not verify_concentration(replace(claim, numeric_binding=replace(
        claim.numeric_binding, **{field: value})), registry)


def test_self_consistent_wrong_evidence_cannot_override_source():
    registry = EvidenceRegistry()
    claim = make_claim(registry)
    old = registry.get(claim.numeric_binding.evidence_id)
    fake = registry.register(old.tool_name, old.parameters,
        dict(old.result, top_customer_withdrawal_amount=59, share_of_current_withdrawals=59/60))
    binding = replace(claim.numeric_binding, numerator=59, value=59/60, evidence_id=fake.evidence_id)
    assert not verify_concentration(replace(claim, numeric_binding=binding,
        text=render_concentration(binding), evidence_ids=claim.evidence_ids + (fake.evidence_id,)), registry)


@pytest.mark.parametrize("change", ["binding", "source", "text", "status"])
def test_contract_cannot_be_bypassed(change):
    registry = EvidenceRegistry()
    claim = make_claim(registry)
    changed = {
        "binding": replace(claim, numeric_binding=None),
        "source": replace(claim, evidence_ids=claim.evidence_ids[1:]),
        "text": replace(claim, text="占比99%"),
        "status": replace(claim, status="insufficient_evidence"),
    }[change]
    assert not verify_concentration(changed, registry)


def test_zero_denominator_cannot_be_reported_as_zero_percent():
    registry = EvidenceRegistry()
    claim = make_claim(registry, (0, 0, 0))
    binding = replace(claim.numeric_binding, value=0.0)
    assert not verify_concentration(replace(claim, numeric_binding=binding,
        status="supported", text=render_concentration(binding)), registry)
