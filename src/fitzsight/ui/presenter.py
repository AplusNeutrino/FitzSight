from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class MetricCard:
    label: str
    value: str


@dataclass(frozen=True)
class ChartSeries:
    label: str
    values: tuple[float, ...]


@dataclass(frozen=True)
class ChartSpec:
    title: str
    caption: str
    categories: tuple[str, ...]
    series: tuple[ChartSeries, ...]


@dataclass(frozen=True)
class TraceRow:
    step: str
    action: str
    purpose: str
    policy: str = "approved"


@dataclass(frozen=True)
class EvidenceCard:
    evidence_id: str
    tool_name: str
    status: str
    result_digest: str
    parameters: dict[str, Any]
    result: Any


@dataclass(frozen=True)
class PresentationView:
    product: str
    intent: str
    backend: str
    status: str
    headline: str
    kpis: tuple[MetricCard, ...]
    chart: ChartSpec
    findings: tuple[str, ...]
    guardrail: str
    trace: tuple[TraceRow, ...]
    evidence_cards: tuple[EvidenceCard, ...]
    verification_passed: bool
    verified_claims: int
    total_claims: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _money(value: float) -> str:
    sign = "-" if value < 0 else ""
    return f"{sign}${abs(value):,.0f}"


def _verified_claim_card(verification: dict[str, Any]) -> MetricCard:
    return MetricCard(
        "Verified claims",
        f"{verification['verified_claims']}/{verification['total_claims']}",
    )


def _crm(metrics: dict[str, Any], verification: dict[str, Any]) -> tuple[tuple[MetricCard, ...], ChartSpec]:
    rows = metrics["team_contribution_analysis"]["segments"]
    kpis = (
        MetricCard("FTD change", f"{metrics['affected']['conversion_change_pp']:.2f} pp"),
        MetricCard("Europe control", f"{metrics['control']['conversion_change_pp']:.2f} pp"),
        MetricCard("Response median", f"{metrics['affected_response_median_change_minutes']:+.2f} min"),
        MetricCard("Anomaly days", str(metrics["post_change_response_anomalies"]["anomaly_count"])),
        _verified_claim_card(verification),
    )
    chart = ChartSpec(
        title="Europe FTD contribution by team",
        caption="Symmetric team-level decomposition of the Europe-wide FTD-rate movement.",
        categories=tuple(str(row["segment"]) for row in rows),
        series=(
            ChartSeries(
                "FTD contribution (pp)",
                tuple(float(row["total_contribution_pp"]) for row in rows),
            ),
        ),
    )
    return kpis, chart


def _net_deposit(metrics: dict[str, Any], verification: dict[str, Any]) -> tuple[tuple[MetricCard, ...], ChartSpec]:
    driver = metrics["driver_decomposition"]
    concentration = metrics["customer_concentration"]
    periods = metrics["periods"]
    kpis = (
        MetricCard("Net-deposit change", _money(float(driver["net_change"]))),
        MetricCard("Deposit change", _money(float(driver["deposit_change"]))),
        MetricCard("Withdrawal change", _money(float(driver["withdrawal_change"]))),
        MetricCard("Top-11 withdrawal share", f"{float(concentration['share_of_current_withdrawals']):.1%}"),
        _verified_claim_card(verification),
    )
    chart = ChartSpec(
        title="Weekly money-flow comparison",
        caption="Baseline vs current weekly money-flow totals from verified tool output.",
        categories=("Deposits", "Withdrawals", "Net deposits"),
        series=(
            ChartSeries(
                "Baseline",
                (
                    float(periods["baseline"]["deposits"]),
                    float(periods["baseline"]["withdrawals"]),
                    float(periods["baseline"]["net_deposits"]),
                ),
            ),
            ChartSeries(
                "Current",
                (
                    float(periods["current"]["deposits"]),
                    float(periods["current"]["withdrawals"]),
                    float(periods["current"]["net_deposits"]),
                ),
            ),
        ),
    )
    return kpis, chart


def _customer_intelligence(metrics: dict[str, Any], verification: dict[str, Any]) -> tuple[tuple[MetricCard, ...], ChartSpec]:
    segmentation = metrics["segmentation"]
    rows = segmentation["profiles"]
    kpis = (
        MetricCard("Customers segmented", f"{int(segmentation['customer_count']):,}"),
        MetricCard("Coverage", f"{float(segmentation['coverage']):.0%}"),
        MetricCard("Value groups", str(segmentation["segment_count"])),
        MetricCard("Top deposit segment", str(segmentation["top_deposit_segment"])),
        MetricCard("Top segment deposit share", f"{float(segmentation['top_deposit_segment_share']):.1%}"),
    )
    chart = ChartSpec(
        title="Behavioral-value segment shares",
        caption="Descriptive customer grouping only; not a credit, AML, suitability or eligibility score.",
        categories=tuple(str(row["segment"]) for row in rows),
        series=(
            ChartSeries("Deposit share", tuple(float(row["deposit_share"]) for row in rows)),
            ChartSeries("Withdrawal share", tuple(float(row["withdrawal_share"]) for row in rows)),
        ),
    )
    return kpis, chart


def _marketing(metrics: dict[str, Any], verification: dict[str, Any]) -> tuple[tuple[MetricCard, ...], ChartSpec]:
    rows = metrics["channel_contribution_analysis"]["segments"]
    kpis = (
        MetricCard("Lead volume", f"{float(metrics['lead_volume_change_pct']):+.1f}%"),
        MetricCard("FTD conversion", f"{float(metrics['conversion_change_pp']):+.2f} pp"),
        MetricCard("Paid Search mix", f"{float(metrics['paid_search_share_change_pp']):+.2f} pp"),
        MetricCard("Paid Search p", f"{float(metrics['paid_search_conversion_test']['p_value']):.3g}"),
        _verified_claim_card(verification),
    )
    chart = ChartSpec(
        title="Acquisition-channel performance effect",
        caption="Separates channel mix from within-channel performance in the synthetic acquisition benchmark.",
        categories=tuple(str(row["segment"]) for row in rows),
        series=(
            ChartSeries(
                "Within-channel performance effect (pp)",
                tuple(float(row["performance_effect_pp"]) for row in rows),
            ),
        ),
    )
    return kpis, chart


def _false_correlation(metrics: dict[str, Any], verification: dict[str, Any]) -> tuple[tuple[MetricCard, ...], ChartSpec]:
    rows = metrics["channel_contribution_analysis"]["segments"]
    affiliate = metrics["affiliate_conversion_test"]
    kpis = (
        MetricCard("Asia conversion", f"{float(metrics['conversion_change_pp']):+.2f} pp"),
        MetricCard("Affiliate conversion", f"{float(affiliate['difference_pp_b_minus_a']):+.2f} pp"),
        MetricCard("Affiliate p", f"{float(affiliate['p_value']):.3g}"),
        MetricCard("Nearby event causal?", "No"),
        _verified_claim_card(verification),
    )
    chart = ChartSpec(
        title="Channel conversion-rate movement",
        caption="The nearby office event is context only; the verified channel pattern drives the conclusion.",
        categories=tuple(str(row["segment"]) for row in rows),
        series=(
            ChartSeries(
                "Conversion-rate change (pp)",
                tuple(float(row["rate_change_pp"]) for row in rows),
            ),
        ),
    )
    return kpis, chart


_PRESENTERS = {
    "crm_routing_ftd_investigation": _crm,
    "net_deposit_anomaly_investigation": _net_deposit,
    "customer_intelligence_segmentation": _customer_intelligence,
    "marketing_lead_quality_investigation": _marketing,
    "false_correlation_guardrail_investigation": _false_correlation,
}


def build_presentation(result: dict[str, Any], *, backend: str) -> PresentationView:
    """Convert an already verified Agent result into presentation-only data.

    This layer does not execute SQL, statistics, segmentation, or business rules.
    It only formats values that already exist in the verified result and therefore
    can be tested without importing Streamlit.
    """

    final = result["final_answer"]
    verification = result["verification"]
    investigation = result["investigation"]
    intent = result["plan"]["intent"]
    if intent not in _PRESENTERS:
        raise ValueError(f"Unsupported presentation intent: {intent}")

    kpis, chart = _PRESENTERS[intent](investigation["metrics"], verification)
    trace = tuple(
        TraceRow(
            step=str(step["step_id"]),
            action=str(step["action"]),
            purpose=str(step["purpose"]),
        )
        for step in result["plan"]["steps"]
    )
    evidence_cards = tuple(
        EvidenceCard(
            evidence_id=str(record["evidence_id"]),
            tool_name=str(record["tool_name"]),
            status=str(record["status"]),
            result_digest=str(record["result_digest"]),
            parameters=dict(record.get("parameters") or {}),
            result=record.get("result"),
        )
        for record in result["audit_evidence"]
    )

    return PresentationView(
        product="FitzSight",
        intent=intent,
        backend=backend,
        status=str(final["status"]),
        headline=str(final["headline"]),
        kpis=kpis,
        chart=chart,
        findings=tuple(str(item) for item in final["findings"]),
        guardrail=str(final.get("guardrail") or ""),
        trace=trace,
        evidence_cards=evidence_cards,
        verification_passed=bool(verification["passed"]),
        verified_claims=int(verification["verified_claims"]),
        total_claims=int(verification["total_claims"]),
    )
