from __future__ import annotations


CRM_INTENT = "crm_routing_ftd_investigation"
NET_DEPOSIT_INTENT = "net_deposit_anomaly_investigation"
CUSTOMER_INTELLIGENCE_INTENT = "customer_intelligence_segmentation"
MARKETING_LEAD_QUALITY_INTENT = "marketing_lead_quality_investigation"
FALSE_CORRELATION_INTENT = "false_correlation_guardrail_investigation"

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

CUSTOMER_INTELLIGENCE_ACTIONS = (
    "inspect_customer_schema",
    "build_customer_behavior_features",
    "segment_customer_value",
    "profile_segment_deposits",
    "compare_withdrawal_pressure",
    "evidence_boundary",
)

MARKETING_LEAD_QUALITY_ACTIONS = (
    "inspect_schema",
    "measure_lead_volume",
    "measure_conversion",
    "channel_mix_decomposition",
    "statistical_validation",
    "event_check",
    "evidence_boundary",
)

FALSE_CORRELATION_ACTIONS = (
    "inspect_schema",
    "measure_conversion_shift",
    "channel_decomposition",
    "statistical_validation",
    "nearby_event_check",
    "falsification_check",
    "evidence_boundary",
)

INTENT_ACTIONS = {
    CRM_INTENT: CRM_ACTIONS,
    NET_DEPOSIT_INTENT: NET_DEPOSIT_ACTIONS,
    CUSTOMER_INTELLIGENCE_INTENT: CUSTOMER_INTELLIGENCE_ACTIONS,
    MARKETING_LEAD_QUALITY_INTENT: MARKETING_LEAD_QUALITY_ACTIONS,
    FALSE_CORRELATION_INTENT: FALSE_CORRELATION_ACTIONS,
}

ACTION_PURPOSES = {
    "inspect_schema": "Confirm required operational fields exist without using evaluation-only ground-truth columns.",
    "query_affected_cohort": "Measure pre/post FTD conversion and response time for the affected European teams.",
    "query_control_cohort": "Measure the same FTD metrics for the European control teams.",
    "statistical_validation": "Test whether observed metric shifts are statistically distinguishable.",
    "contribution_decomposition": "Decompose the aggregate FTD-rate movement by sales team and rank negative contributors.",
    "anomaly_scan": "Compare post-change response-time behavior against a robust pre-change baseline.",
    "measure_period_net_deposits": "Measure deposits, withdrawals, and net deposits in the current and baseline weekly windows.",
    "decompose_deposit_withdrawal_drivers": "Decompose the net-deposit change into deposit-side and withdrawal-side pressure.",
    "identify_customer_concentration": "Measure whether the current withdrawal shock is concentrated in a small number of customers.",
    "compare_regional_control": "Compare Europe's weekly net-deposit movement with other regions as a control.",
    "inspect_customer_schema": "Confirm customer, deposit, withdrawal and trading fields needed for descriptive segmentation.",
    "build_customer_behavior_features": "Aggregate observable customer deposit, withdrawal and trading behavior without using hidden benchmark labels.",
    "segment_customer_value": "Apply the approved transparent behavioral-value segmentation policy.",
    "profile_segment_deposits": "Profile customer counts, deposits, net deposits and trading activity across derived value segments.",
    "compare_withdrawal_pressure": "Describe segment-level withdrawal pressure without inferring motives or compliance risk.",
    "measure_lead_volume": "Compare lead volume across equal baseline and current campaign windows.",
    "measure_conversion": "Measure FTD conversion before and after the acquisition shift.",
    "channel_mix_decomposition": "Decompose conversion movement by acquisition channel and identify the dominant negative contributor.",
    "measure_conversion_shift": "Measure the aggregate conversion shift across the approved false-correlation benchmark window.",
    "channel_decomposition": "Decompose the conversion movement by acquisition channel to identify the observed driver pattern.",
    "nearby_event_check": "Inspect nearby operational events without assuming temporal proximity implies causality.",
    "falsification_check": "Compare the observed data pattern against the nearby event's declared scope/effect before any causal attribution.",
    "event_check": "Inspect nearby operational events for context without converting association into unsupported causality.",
    "evidence_boundary": "Separate directly supported findings from hypotheses, causal overclaims or prohibited decision use.",
}


class UnsupportedIntentCatalogError(ValueError):
    pass


def classify_supported_intent(question: str) -> str:
    """Classify only explicitly approved FitzSight v0.7 intents.

    This local classifier is a security/scope boundary. A model cannot expand
    FitzSight into arbitrary financial actions or invent a new workflow.
    """

    q = " ".join(question.lower().split())
    europe = any(token in q for token in ("europe", "european", "欧洲"))
    americas = any(token in q for token in ("americas", "america", "美洲", "美洲区"))
    asia = any(token in q for token in ("asia", "asian", "亚洲"))

    crm = (
        europe
        and any(token in q for token in ("ftd", "conversion", "转化"))
        and any(token in q for token in ("july", "07-15", "7月15", "7 月 15", "july 15", "after july 15"))
    )
    if crm:
        return CRM_INTENT

    net_deposit = (
        europe
        and any(token in q for token in ("net deposit", "net deposits", "net-deposit", "net-deposits", "净入金", "净存款"))
        and any(token in q for token in ("august", "aug 3", "august 3", "2026-08-03", "8月", "8 月", "this week", "weekly", "week", "本周", "这周"))
    )
    if net_deposit:
        return NET_DEPOSIT_INTENT

    customer_intelligence = (
        europe
        and any(token in q for token in ("customer segment", "customer segments", "segmentation", "segment customers", "customer intelligence", "high value customers", "high-value customers", "客户分群", "客户细分", "高价值客户"))
        and any(token in q for token in ("value", "deposit", "deposits", "contribute", "contribution", "价值", "入金", "贡献"))
    )
    if customer_intelligence:
        return CUSTOMER_INTELLIGENCE_INTENT

    marketing_quality = (
        americas
        and any(token in q for token in ("lead volume", "leads", "lead", "线索", "获客"))
        and any(token in q for token in ("conversion", "ftd", "quality", "转化", "质量"))
        and any(token in q for token in ("june", "june 15", "06-15", "2026-06-15", "6月15", "6 月 15", "campaign", "paid media", "paid search"))
    )
    if marketing_quality:
        return MARKETING_LEAD_QUALITY_INTENT

    false_correlation = (
        asia
        and any(token in q for token in ("conversion", "ftd", "转化"))
        and any(token in q for token in ("july 20", "07-20", "2026-07-20", "7月20", "7 月 20", "office", "relocation", "nearby event", "cause", "affiliate", "办公室", "搬迁", "因果"))
    )
    if false_correlation:
        return FALSE_CORRELATION_INTENT

    raise UnsupportedIntentCatalogError(
        "Question is outside the approved FitzSight v0.7 intent catalog."
    )


def actions_for_intent(intent: str) -> tuple[str, ...]:
    try:
        return INTENT_ACTIONS[intent]
    except KeyError as exc:
        raise UnsupportedIntentCatalogError(f"Unsupported intent: {intent}") from exc


def purposes_for_intent(intent: str) -> tuple[str, ...]:
    return tuple(ACTION_PURPOSES[action] for action in actions_for_intent(intent))
