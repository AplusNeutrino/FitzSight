"""N-C4 recomputation from SQL aggregates, not independent source-system audit."""
from dataclasses import dataclass
import math
from statistics import median
from .numeric_claims import complete_sql_rows, finite_number


@dataclass(frozen=True)
class RegionAmounts:
    region: str
    customer_count: int
    deposits: float
    withdrawals: float


@dataclass(frozen=True)
class RegionalBinding:
    value: float | None
    control_value: float | None
    baseline: tuple[RegionAmounts, ...]
    current: tuple[RegionAmounts, ...]
    baseline_start: str
    baseline_end: str
    current_start: str
    current_end: str
    evidence_id: str
    source_evidence_ids: tuple[str, ...]
    metric_id: str = "regional_net_per_customer_change.v1"
    unit: str = "currency_amount_per_customer"
    currency: str = "USD"
    region: str = "Europe"


def render_regional(b: RegionalBinding) -> str:
    if b.value is None or b.control_value is None:
        return ("Regional net-deposit comparison is unavailable because the target region "
                "or comparable control regions have no calculable per-customer change.")
    return (f"Europe's weekly net-deposit movement per registered customer was "
            f"${b.value:,.2f}, versus a median of "
            f"${b.control_value:,.2f} across the other regions.")


def _close(a, b):
    return a is None and b is None or (
        finite_number(a) and finite_number(b) and math.isclose(a, b, rel_tol=0, abs_tol=1e-8))


def _period(deposits, withdrawals):
    dep = {r["region"]: r for r in deposits}
    wd = {r["region"]: r for r in withdrawals}
    if len(dep) != len(deposits) or len(wd) != len(withdrawals) or dep.keys() != wd.keys():
        raise ValueError("Duplicate or mismatched regional aggregates")
    output = []
    for region in sorted(dep):
        d, w = dep[region], wd[region]
        if not isinstance(region, str) or not region:
            raise ValueError("Missing region")
        count = d["customer_count"]
        if type(count) is not int or count < 0:
            raise ValueError("Invalid customer count")
        if d["invalid_currency_count"] != 0 or w["invalid_currency_count"] != 0:
            raise ValueError("Regional comparison requires USD")
        if not finite_number(d["deposits"]) or not finite_number(w["withdrawals"]):
            raise ValueError("Nonfinite amount")
        output.append(RegionAmounts(region, count, d["deposits"], w["withdrawals"]))
    return tuple(output)


def verify_regional(claim, registry) -> bool:
    b = claim.numeric_binding
    if type(b) is not RegionalBinding or (b.metric_id, b.unit, b.currency, b.region) != (
        "regional_net_per_customer_change.v1", "currency_amount_per_customer", "USD", "Europe"
    ):
        return False
    try:
        record = registry.get(b.evidence_id)
        if record.tool_name != "regional_net_deposit_control":
            return False
        for field in ("baseline_start", "baseline_end", "current_start", "current_end", "currency", "region"):
            if record.parameters[field] != getattr(b, field):
                return False
        ids = b.source_evidence_ids
        if len(ids) != 4 or len(set(ids)) != 4 or tuple(record.parameters["source_evidence_ids"]) != ids:
            return False
        sources = [registry.get(eid) for eid in ids]
        for item in [record, *sources]:
            if (item.evidence_id not in claim.evidence_ids or item.status != "success"
                    or registry.digest(item.result) != item.result_digest):
                return False
        if any(item.tool_name != "read_only_sql" for item in sources):
            return False
        if not all(complete_sql_rows(item.result) for item in sources):
            return False
        baseline = _period(sources[0].result["rows"], sources[1].result["rows"])
        current = _period(sources[2].result["rows"], sources[3].result["rows"])
        for bound, computed in ((b.baseline, baseline), (b.current, current)):
            if len(bound) != len(computed):
                return False
            for a, c in zip(bound, computed):
                if (type(a) is not RegionAmounts or a.region != c.region
                        or type(a.customer_count) is not int or a.customer_count != c.customer_count
                        or not _close(a.deposits, c.deposits) or not _close(a.withdrawals, c.withdrawals)):
                    return False
        before = {r.region: (r.deposits-r.withdrawals)/r.customer_count if r.customer_count else None for r in baseline}
        after = {r.region: (r.deposits-r.withdrawals)/r.customer_count if r.customer_count else None for r in current}
        changes = {r: after[r]-before[r] if before.get(r) is not None and after.get(r) is not None else None
                   for r in before.keys() | after.keys()}
        target = changes.get(b.region)
        controls = [v for r, v in changes.items() if r != b.region and v is not None]
        control = median(controls) if controls else None
        result = record.result
        recorded_changes = result["net_deposit_per_customer_change"]
        if recorded_changes.keys() != changes.keys() or any(not _close(v, recorded_changes[r]) for r, v in changes.items()):
            return False
        if not all((_close(b.value, target), _close(b.control_value, control),
                    _close(result["europe_change"], target), _close(result["other_region_median_change"], control))):
            return False
        available = target is not None and control is not None
        reason = "missing_target_region" if target is None else "missing_control_regions" if control is None else None
        return (type(result["control_region_count"]) is int and result["control_region_count"] == len(controls)
                and result["calculation_status"] == ("computed" if available else "unavailable")
                and result["unavailable_reason"] == reason
                and claim.status == ("supported" if available else "insufficient_evidence")
                and claim.text == render_regional(b))
    except (KeyError, TypeError, ValueError, AttributeError, OverflowError, ZeroDivisionError):
        return False
