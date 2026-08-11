from __future__ import annotations

from dataclasses import dataclass


CRM_INTENT = "crm_routing_ftd_investigation"
NET_DEPOSIT_INTENT = "net_deposit_anomaly_investigation"

CRM_ACTIONS = (
    "inspect_schema",
    "query_affected_cohort",
    "query_control_cohort",
    "statistical_validation",
    "contribution_decomposition",
    "anomaly_scan",
    "event_check",
    "evidence_boundary",
)

NET_DEPOSIT_ACTIONS = (
    "inspect_schema",
    "measure_period_net_deposits",
    "decompose_deposit_withdrawal_drivers",
    "identify_customer_concentration",
    "compare_regional_control",
    "event_check",
    "evidence_boundary",
)

INTENT_ACTIONS = {
    CRM_INTENT: CRM_ACTIONS,
    NET_DEPOSIT_INTENT: NET_DEPOSIT_ACTIONS,
}

ACTION_PURPOSES = {
    "inspect_schema": "Confirm required operational fields exist without using evaluation-only ground-truth columns.",
    "query_affected_cohort": "Measure pre/post FTD conversion and response time for the affected European teams.",
    "query_control_cohort": "Measure the same FTD metrics for the European control teams.",
    "statistical_validation": "Test whether observed conversion and response-time shifts are statistically distinguishable.",
    "contribution_decomposition": "Decompose the aggregate FTD-rate movement by sales team and rank negative contributors.",
    "anomaly_scan": "Compare post-change response-time behavior against a robust pre-change baseline.",
    "measure_period_net_deposits": "Measure deposits, withdrawals, and net deposits in the current and baseline weekly windows.",
    "decompose_deposit_withdrawal_drivers": "Decompose the net-deposit change into deposit-side and withdrawal-side pressure.",
    "identify_customer_concentration": "Measure whether the current withdrawal shock is concentrated in a small number of customers.",
    "compare_regional_control": "Compare Europe's weekly net-deposit movement with other regions as a control.",
    "event_check": "Inspect nearby operational events for context without converting association into unsupported causality.",
    "evidence_boundary": "Separate directly supported findings from hypotheses or causal overclaims.",
}


class UnsupportedIntentCatalogError(ValueError):
    pass


def classify_supported_intent(question: str) -> str:
    """Classify only the two explicitly approved v0.5 intents.

    This is intentionally conservative. The model is not used to expand scope.
    Unsupported questions must be refused before any external model call.
    """

    q = " ".join(question.lower().split())
    europe = any(token in q for token in ("europe", "european", "欧洲"))

    crm = (
        europe
        and any(token in q for token in ("ftd", "conversion", "转化"))
        and any(
            token in q
            for token in ("july", "07-15", "7月15", "7 月 15", "july 15", "after july 15")
        )
    )
    if crm:
        return CRM_INTENT

    net_deposit = (
        europe
        and any(
            token in q
            for token in (
                "net deposit",
                "net deposits",
                "net-deposit",
                "net-deposits",
                "净入金",
                "净存款",
            )
        )
        and any(
            token in q
            for token in (
                "august",
                "aug 3",
                "august 3",
                "2026-08-03",
                "8月",
                "8 月",
                "this week",
                "weekly",
                "week",
                "本周",
                "这周",
            )
        )
    )
    if net_deposit:
        return NET_DEPOSIT_INTENT

    raise UnsupportedIntentCatalogError(
        "Question is outside the approved FitzSight v0.5 intent catalog."
    )


def actions_for_intent(intent: str) -> tuple[str, ...]:
    try:
        return INTENT_ACTIONS[intent]
    except KeyError as exc:
        raise UnsupportedIntentCatalogError(f"Unsupported intent: {intent}") from exc


def purposes_for_intent(intent: str) -> tuple[str, ...]:
    return tuple(ACTION_PURPOSES[action] for action in actions_for_intent(intent))
