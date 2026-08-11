from __future__ import annotations

from fitzsight.agent.catalog import (
    CRM_INTENT,
    CUSTOMER_INTELLIGENCE_INTENT,
    FALSE_CORRELATION_INTENT,
    MARKETING_LEAD_QUALITY_INTENT,
    NET_DEPOSIT_INTENT,
    classify_supported_intent,
)
from .customer_intelligence import CustomerIntelligenceInvestigationEngine
from .engine import DeterministicInvestigationEngine
from .lead_quality import FalseCorrelationInvestigationEngine, MarketingLeadQualityInvestigationEngine
from .net_deposit import NetDepositInvestigationEngine


class MultiIntentInvestigationEngine:
    """Routes only approved v0.7 intents to deterministic executors."""

    def __init__(
        self,
        *,
        crm_engine: DeterministicInvestigationEngine,
        net_deposit_engine: NetDepositInvestigationEngine,
        customer_intelligence_engine: CustomerIntelligenceInvestigationEngine,
        marketing_lead_quality_engine: MarketingLeadQualityInvestigationEngine,
        false_correlation_engine: FalseCorrelationInvestigationEngine,
    ) -> None:
        self.crm_engine = crm_engine
        self.net_deposit_engine = net_deposit_engine
        self.customer_intelligence_engine = customer_intelligence_engine
        self.marketing_lead_quality_engine = marketing_lead_quality_engine
        self.false_correlation_engine = false_correlation_engine

    @staticmethod
    def supports(question: str) -> bool:
        try:
            classify_supported_intent(question)
            return True
        except ValueError:
            return False

    def _engine(self, question: str):
        intent = classify_supported_intent(question)
        if intent == CRM_INTENT:
            return self.crm_engine
        if intent == NET_DEPOSIT_INTENT:
            return self.net_deposit_engine
        if intent == CUSTOMER_INTELLIGENCE_INTENT:
            return self.customer_intelligence_engine
        if intent == MARKETING_LEAD_QUALITY_INTENT:
            return self.marketing_lead_quality_engine
        if intent == FALSE_CORRELATION_INTENT:
            return self.false_correlation_engine
        raise ValueError(f"Unsupported intent: {intent}")

    def plan(self, question: str):
        return self._engine(question).plan(question)

    def investigate(self, question: str):
        return self._engine(question).investigate(question)
