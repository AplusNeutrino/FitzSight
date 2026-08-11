from __future__ import annotations

from typing import Protocol

from fitzsight.evidence.registry import EvidenceRegistry
from .models import AgentRunResult
from .planner import Planner, validate_plan
from .renderer import render_verified_answer
from .verifier import EvidenceClaimVerifier


class InvestigationExecutor(Protocol):
    def investigate(self, question: str): ...


class FitzSightAgent:
    """Constrained v0.5 multi-intent Agent orchestration layer.

    The planner may be deterministic, a structured JSON adapter, or the optional
    OpenAI Responses provider. Execution remains inside deterministic audited
    engines; planner/model output never contains executable SQL or arbitrary
    tool parameters.
    """

    def __init__(
        self,
        *,
        planner: Planner,
        engine: InvestigationExecutor,
        verifier: EvidenceClaimVerifier,
        registry: EvidenceRegistry,
    ) -> None:
        self.planner = planner
        self.engine = engine
        self.verifier = verifier
        self.registry = registry

    def run(self, question: str) -> AgentRunResult:
        plan = validate_plan(self.planner.plan(question))
        plan_record = self.registry.register(
            "agent.plan",
            {
                "planner_mode": plan.planner_mode,
                "intent": plan.intent,
                "plan_version": plan.plan_version,
            },
            plan.to_dict(),
        )

        investigation = self.engine.investigate(question)
        if investigation.plan.intent != plan.intent:
            raise RuntimeError(
                f"Planner/executor intent mismatch: {plan.intent} != {investigation.plan.intent}"
            )

        verification = self.verifier.verify(investigation)
        final_answer = render_verified_answer(investigation, verification)
        final_record = self.registry.register(
            "agent.final_answer",
            {
                "verification_evidence_id": verification.evidence_id,
                "status": final_answer.status,
                "intent": plan.intent,
            },
            final_answer.to_dict(),
            status="success" if verification.passed else "error",
        )

        return AgentRunResult(
            product="FitzSight",
            mode="agent_v0.5_multi_intent",
            question=question,
            planner_mode=plan.planner_mode,
            plan=plan,
            plan_evidence_id=plan_record.evidence_id,
            investigation=investigation.to_dict(),
            verification=verification,
            final_answer=final_answer,
            final_answer_evidence_id=final_record.evidence_id,
            audit_evidence=tuple(self.registry.to_dicts()),
        )
