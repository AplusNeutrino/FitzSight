from __future__ import annotations

from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.investigation.engine import DeterministicInvestigationEngine
from .models import AgentRunResult
from .planner import Planner, validate_plan
from .renderer import render_verified_answer
from .verifier import EvidenceClaimVerifier


class FitzSightAgent:
    """Constrained v0.4 Agent orchestration layer.

    Planning may be deterministic or supplied by a structured LLM adapter, but
    execution stays inside the audited deterministic investigation engine. The
    planner never emits SQL or arbitrary tool arguments.
    """

    def __init__(
        self,
        *,
        planner: Planner,
        engine: DeterministicInvestigationEngine,
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
            {"planner_mode": plan.planner_mode, "intent": plan.intent},
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
            },
            final_answer.to_dict(),
            status="success" if verification.passed else "error",
        )

        return AgentRunResult(
            product="FitzSight",
            mode="agent_v0.4_constrained",
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
