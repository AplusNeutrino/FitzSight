"""Bounded numeric contracts: the legacy synthetic USD net-change claim.

N-C1/N-C2 require the approved metric-definition snapshot. Other claims still
need catalog migration; matching metadata does not validate upstream semantics.
"""
from dataclasses import dataclass
import math
from numbers import Real

from fitzsight.metrics import get_metric, net_deposit_definitions


@dataclass(frozen=True)
class NetChangeBinding:
    value: float
    evidence_id: str
    baseline_start: str
    baseline_end: str
    current_start: str
    current_end: str
    metric_id: str = 'net_deposit_change.v1'
    evidence_field: str = 'net_change'
    unit: str = 'currency_amount'
    currency: str = 'USD'
    region: str = 'Europe'



@dataclass(frozen=True, kw_only=True)
class NetDecompositionBinding(NetChangeBinding):
    deposit_change: float
    withdrawal_change: float
    metric_id: str = 'net_deposit_decomposition.v1'


def render_net_decomposition(binding: NetDecompositionBinding) -> str:
    return (
        f"Deposits changed by ${binding.deposit_change:,.2f}, while withdrawals changed by "
        f"${binding.withdrawal_change:,.2f}; the decomposition exactly reconstructs the net-deposit movement."
    )


def render_net_change(binding: NetChangeBinding) -> str:
    return (
        f"European net deposits changed by ${binding.value:,.2f} week over week "
        f"({binding.baseline_start}–{binding.baseline_end} versus "
        f"{binding.current_start}–{binding.current_end})."
    )


def finite_number(value):
    try:
        return isinstance(value, Real) and not isinstance(value, bool) and math.isfinite(value)
    except (TypeError, ValueError, OverflowError):
        return False


def complete_sql_rows(payload) -> bool:
    """Require explicit full-result metadata; absent flags are not proof of completeness."""
    return (
        type(payload) is dict
        and payload.get('truncated') is False
        and 'evidence_mode' not in payload
        and 'rows_preview' not in payload
        and type(payload.get('rows')) is list
        and type(payload.get('row_count')) is int
        and payload['row_count'] == len(payload['rows'])
        and all(type(row) is dict for row in payload['rows'])
    )


def verify_net_change(claim, registry) -> bool:
    return _verify_cashflow(claim, registry, decomposition=False)


def verify_net_decomposition(claim, registry) -> bool:
    return _verify_cashflow(claim, registry, decomposition=True)


def _verify_cashflow(claim, registry, *, decomposition: bool) -> bool:
    """Fail closed; both components must match sources, not merely cancel out."""
    b = claim.numeric_binding
    expected_type = NetDecompositionBinding if decomposition else NetChangeBinding
    if type(b) is not expected_type:
        return False
    metric = get_metric('net_deposit_decomposition.v1' if decomposition else 'net_deposit_change.v1')
    if (b.metric_id, b.evidence_field, b.unit, b.currency, b.region) != (
        metric.metric_id, 'net_change', metric.unit, metric.currency, 'Europe'
    ) or not finite_number(b.value):
        return False
    try:
        record = registry.get(b.evidence_id)
        if b.evidence_id not in claim.evidence_ids or record.tool_name != 'net_deposit_driver_decomposition':
            return False
        if record.status != 'success' or registry.digest(record.result) != record.result_digest:
            return False
        for field in ('baseline_start', 'baseline_end', 'current_start', 'current_end', 'region', 'currency'):
            if getattr(b, field) != record.parameters[field]:
                return False
        if record.parameters['metric_definitions'] != net_deposit_definitions():
            return False
        expected = record.result[b.evidence_field]
        if not finite_number(expected) or not math.isclose(b.value, expected, rel_tol=0, abs_tol=1e-8):
            return False
        # Recompute from the four source SQL results in their declared order.
        source_ids = record.parameters['source_evidence_ids']
        if len(source_ids) != 4 or len(set(source_ids)) != 4:
            return False
        sums = []
        for eid in source_ids:
            source = registry.get(eid)
            if eid not in claim.evidence_ids or source.tool_name != 'read_only_sql' or source.status != 'success':
                return False
            if registry.digest(source.result) != source.result_digest:
                return False
            if not complete_sql_rows(source.result):
                return False
            rows = source.result['rows']
            if any(not finite_number(r['amount']) or r['currency'] != 'USD' for r in rows):
                return False
            sums.append(sum(r['amount'] for r in rows))
        recomputed = (sums[2] - sums[3]) - (sums[0] - sums[1])
        if not math.isclose(b.value, recomputed, rel_tol=0, abs_tol=1e-8):
            return False
        if decomposition:
            for field, value in (('deposit_change', sums[2] - sums[0]),
                                 ('withdrawal_change', sums[3] - sums[1])):
                bound = getattr(b, field)
                recorded = record.result[field]
                if not (finite_number(bound) and finite_number(recorded)
                        and math.isclose(bound, recorded, rel_tol=0, abs_tol=1e-8)
                        and math.isclose(bound, value, rel_tol=0, abs_tol=1e-8)):
                    return False
            return claim.text == render_net_decomposition(b)
        return claim.text == render_net_change(b)
    except (KeyError, TypeError, ValueError, AttributeError, OverflowError):
        return False
