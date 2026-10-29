"""Bounded USD withdrawal concentration contract; source SQL remains trusted."""
from dataclasses import dataclass
import math
from datetime import date, timedelta

from .request import InvestigationRequest
from .cashflow_queries import cashflow_sql

from .numeric_claims import complete_sql_rows, finite_number


@dataclass(frozen=True)
class ConcentrationBinding:
    value: float | None
    numerator: float
    denominator: float
    customer_count: int
    period_start: str
    period_end_exclusive: str
    evidence_id: str
    source_evidence_id: str
    metric_id: str = "withdrawal_concentration.v1"
    evidence_field: str = "share_of_current_withdrawals"
    unit: str = "ratio"
    currency: str = "USD"
    region: str = "Europe"


def render_concentration(b: ConcentrationBinding) -> str:
    if b.value is None:
        return f"Withdrawal concentration is unavailable because {b.region} total withdrawals in the selected period are not positive."
    return (f"The largest {b.customer_count} customer withdrawal totals in {b.region} account for "
            f"{b.value:.1%} of withdrawals in the selected period ({b.period_start} to {b.period_end_exclusive}, end exclusive).")


def verify_concentration(claim, registry, *, expected_request=None, expected_customer_count=None) -> bool:
    if expected_request is not None:
        if (type(expected_request) is not InvestigationRequest
                or type(expected_customer_count) is not int or expected_customer_count <= 0):
            return False
    region = expected_request.region if expected_request is not None else 'Europe'
    b = claim.numeric_binding
    if type(b) is not ConcentrationBinding:
        return False
    if (b.metric_id, b.evidence_field, b.unit, b.currency, b.region) != (
        "withdrawal_concentration.v1", "share_of_current_withdrawals", "ratio", "USD", region
    ) or type(b.customer_count) is not int or b.customer_count <= 0:
        return False
    try:
        record = registry.get(b.evidence_id)
        source = registry.get(b.source_evidence_id)
        for item, tool in ((record, "withdrawal_customer_concentration"), (source, "read_only_sql")):
            if (item.evidence_id not in claim.evidence_ids or item.tool_name != tool
                    or item.status != "success" or registry.digest(item.result) != item.result_digest):
                return False
        for field in ("period_start", "period_end_exclusive", "currency", "region",
                      "customer_count", "source_evidence_id"):
            if record.parameters[field] != getattr(b, field):
                return False
        if 'request' in record.parameters and expected_request is None:
            return False
        if expected_request is not None:
            start = expected_request.current.start
            end = (date.fromisoformat(expected_request.current.end) + timedelta(days=1)).isoformat()
            if (record.parameters.get('request') != expected_request.to_dict()
                    or b.customer_count != expected_customer_count
                    or (b.period_start, b.period_end_exclusive) != (start, end)
                    or source.parameters.get('sql') != cashflow_sql('withdrawals')
                    or source.parameters.get('bound_parameters') != [start, end, region]):
                return False
        if not complete_sql_rows(source.result):
            return False
        # Aggregate the same current-period raw rows independently of ranking SQL.
        totals = {}
        for row in source.result["rows"]:
            amount = row["amount"]
            if not finite_number(amount) or amount < 0 or row["currency"] != b.currency:
                return False
            customer = row["customer_id"]
            if customer is None:
                return False
            totals[customer] = totals.get(customer, 0.0) + amount
        denominator = sum(totals.values())
        numerator = sum(sorted(totals.values(), reverse=True)[:b.customer_count])
        for bound, recorded, computed in (
            (b.numerator, record.result["top_customer_withdrawal_amount"], numerator),
            (b.denominator, record.result["current_total_withdrawals"], denominator),
        ):
            if not all(finite_number(x) for x in (bound, recorded, computed)):
                return False
            if not (math.isclose(bound, recorded, rel_tol=0, abs_tol=1e-8)
                    and math.isclose(bound, computed, rel_tol=0, abs_tol=1e-8)):
                return False
        if record.result["customer_count"] != b.customer_count:
            return False
        value = numerator / denominator if denominator > 0 else None
        if value is None:
            if (b.value is not None or record.result[b.evidence_field] is not None
                    or claim.status != "insufficient_evidence"
                    or record.result["calculation_status"] != "unavailable"
                    or record.result["unavailable_reason"] != "nonpositive_total_withdrawals"):
                return False
        else:
            if (claim.status != "supported" or record.result["calculation_status"] != "computed"
                    or record.result["unavailable_reason"] is not None):
                return False
            for candidate in (b.value, record.result[b.evidence_field]):
                if not finite_number(candidate) or not math.isclose(candidate, value, rel_tol=0, abs_tol=1e-12):
                    return False
        return claim.text == render_concentration(b)
    except (KeyError, TypeError, ValueError, AttributeError, OverflowError):
        return False
