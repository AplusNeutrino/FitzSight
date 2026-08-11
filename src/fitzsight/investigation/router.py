from __future__ import annotations

from fitzsight.agent.catalog import (
    CRM_INTENT,
    CUSTOMER_INTELLIGENCE_INTENT,
    NET_DEPOSIT_INTENT,
    classify_supported_intent,
)
from .customer_intelligence import CustomerIntelligenceInvestigationEngine
from .engine import DeterministicInvestigationEngine
from .net_deposit import NetDepositInvestigationEngine


class MultiIntentInvestigationEngine:
    """Routes only approved intents to deterministic executors."""

    def __init__(
        self,
        *,
        crm_engine: DeterministicInvestigationEngine,
        net_deposit_engine: NetDepositInvestigationEngine,
        customer_intelligence_engine: CustomerIntelligenceInvestigationEngine,
    ) -> None:
        self.crm_engine = crm_engine
        self.net_deposit_engine = net_deposit_engine
        self.customer_intelligence_engine = customer_intelligence_engine

    @staticmethod
    def supports(question: str) -> bool:
        try:
            classify_supported_intent(question)
            return True
        except ValueError:
            return False

    def plan(self, question: str):
        intent = classify_supported_intent(question)
        if intent == CRM_INTENT:
            return self.crm_engine.plan(question)
        if intent == NET_DEPOSIT_INTENT:
            return self.net_deposit_engine.plan(question)
        if intent == CUSTOMER_INTELLIGENCE_INTENT:
            return self.customer_intelligence_engine.plan(question)
        raise ValueError(f"Unsupported intent: {intent}")

    def investigate(self, question: str):
        intent = classify_supported_intent(question)
        if intent == CRM_INTENT:
            return self.crm_engine.investigate(question)
        if intent == NET_DEPOSIT_INTENT:
            return self.net_deposit_engine.investigate(question)
        if intent == CUSTOMER_INTELLIGENCE_INTENT:
            return self.customer_intelligence_engine.investigate(question)
        raise ValueError(f"Unsupported intent: {intent}")
