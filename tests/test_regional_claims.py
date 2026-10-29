from dataclasses import replace
import pytest
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.investigation.models import Claim
from fitzsight.investigation.regional_claims import RegionAmounts, RegionalBinding, render_regional, verify_regional


def make_regional(registry, missing=None):
    before = (RegionAmounts("Africa", 1, 10, 0), RegionAmounts("Asia", 1, 10, 0),
              RegionAmounts("Europe", 2, 100, 20))
    after = (RegionAmounts("Africa", 1, 40, 0), RegionAmounts("Asia", 1, 20, 0),
             RegionAmounts("Europe", 3, 90, 30))
    if missing == "target":
        before, after = before[:2], after[:2]
    elif missing == "controls":
        before, after = before[2:], after[2:]
    sources = []
    for period in (before, after):
        sources.append(registry.register("read_only_sql", {}, {"rows": [
            dict(region=r.region, customer_count=r.customer_count, deposits=r.deposits, invalid_currency_count=0)
            for r in period], "truncated": False, "row_count": len(period)}))
        sources.append(registry.register("read_only_sql", {}, {"rows": [
            dict(region=r.region, withdrawals=r.withdrawals, invalid_currency_count=0) for r in period], "truncated": False, "row_count": len(period)}))
    ids = tuple(s.evidence_id for s in sources)
    changes = {r.region: change for r, change in zip(before, (30, 10, -20))}
    if missing == "controls":
        changes = {"Europe": -20}
    target = None if missing == "target" else -20
    control = None if missing == "controls" else 20
    reason = {"target": "missing_target_region", "controls": "missing_control_regions"}.get(missing)
    context = dict(baseline_start="2026-07-27", baseline_end="2026-08-02",
                   current_start="2026-08-03", current_end="2026-08-09")
    record = registry.register("regional_net_deposit_control",
        dict(context, region="Europe", currency="USD", source_evidence_ids=ids),
        dict(net_deposit_per_customer_change=changes, europe_change=target,
             other_region_median_change=control, control_region_count=0 if missing == "controls" else 2,
             calculation_status="computed" if missing is None else "unavailable", unavailable_reason=reason))
    binding = RegionalBinding(value=target, control_value=control, baseline=before, current=after,
                              evidence_id=record.evidence_id, source_evidence_ids=ids, **context)
    return Claim("N-C4", render_regional(binding), "supported" if missing is None else "insufficient_evidence",
                 "medium", ids + (record.evidence_id,), binding)


@pytest.mark.parametrize("missing", [None, "target", "controls"])
def test_hand_calculation_with_different_period_denominators_and_missing(missing):
    registry = EvidenceRegistry()
    claim = make_regional(registry, missing)
    assert verify_regional(claim, registry)
    if missing is None:
        assert claim.numeric_binding.value == (90-30)/3 - (100-20)/2
        assert claim.numeric_binding.control_value == (10+30)/2


@pytest.mark.parametrize("field,value", [
    ("value", 99), ("control_value", 99), ("value", True), ("value", float("nan")),
    ("control_value", float("inf")), ("unit", "percent"), ("currency", "EUR"),
    ("region", "Asia"), ("metric_id", "other"), ("baseline_start", "2026-07-28"),
    ("baseline_end", "2026-08-01"), ("current_start", "2026-08-04"), ("current_end", "2026-08-10"),
    ("source_evidence_ids", ("E0001",)*4), ("evidence_id", "E9999"),
])
def test_binding_tampering(field, value):
    registry = EvidenceRegistry()
    c = make_regional(registry)
    assert not verify_regional(replace(c, numeric_binding=replace(c.numeric_binding, **{field: value})), registry)


@pytest.mark.parametrize("field,value", [
    ("customer_count", 1), ("customer_count", True), ("deposits", 999),
    ("withdrawals", float("nan")), ("deposits", "100"), ("region", "Other"),
])
def test_period_amount_or_denominator_tampering(field, value):
    registry = EvidenceRegistry()
    c = make_regional(registry)
    b = c.numeric_binding
    baseline = b.baseline[:2] + (replace(b.baseline[2], **{field: value}),)
    assert not verify_regional(replace(c, numeric_binding=replace(b, baseline=baseline)), registry)


@pytest.mark.parametrize("change", ["text", "binding", "reference", "status"])
def test_bypass_rejected(change):
    registry = EvidenceRegistry()
    c = make_regional(registry)
    c = {"text": replace(c, text="欧洲人均变化99美元"),
         "binding": replace(c, numeric_binding=None),
         "reference": replace(c, evidence_ids=c.evidence_ids[1:]),
         "status": replace(c, status="insufficient_evidence")}[change]
    assert not verify_regional(c, registry)


def test_fake_self_consistent_derived_result_rejected():
    registry = EvidenceRegistry()
    c = make_regional(registry)
    old = registry.get(c.numeric_binding.evidence_id)
    fake = registry.register(old.tool_name, old.parameters, dict(old.result, europe_change=99,
        net_deposit_per_customer_change=dict(old.result["net_deposit_per_customer_change"], Europe=99)))
    b = replace(c.numeric_binding, value=99, evidence_id=fake.evidence_id)
    assert not verify_regional(replace(c, numeric_binding=b, text=render_regional(b),
        evidence_ids=c.evidence_ids + (fake.evidence_id,)), registry)
