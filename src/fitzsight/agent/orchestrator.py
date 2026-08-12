from __future__ import annotations

from typing import Protocol

from fitzsight.evidence.registry import EvidenceRegistry
from .models import AgentRunResult, FollowUpAnswer
from .planner import Planner, validate_plan
from .renderer import render_verified_answer
from .verifier import EvidenceClaimVerifier


class InvestigationExecutor(Protocol):
    def investigate(self, question: str): ...


class FitzSightAgent:
    """Constrained v0.12 five-intent Agent orchestration layer.

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
            mode="agent_v0.12_bounded_adaptive",
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

    def answer_follow_up(self, previous: AgentRunResult, question: str) -> FollowUpAnswer:
        """Answer a small approved follow-up from an already verified hero run.

        This is deliberately not an unrestricted conversational analytics path.
        It does not run new SQL or accept model-generated tool parameters; it can
        only summarize evidence already verified in the CRM/FTD hero result.
        """

        if previous.verification.passed is not True:
            raise ValueError("Follow-up requires a previously verified Agent run")
        if previous.plan.intent != "crm_routing_ftd_investigation":
            raise ValueError("v0.12 follow-up is limited to the CRM/FTD hero workflow")

        normalized = " ".join(question.lower().split())
        investigation = previous.investigation
        metrics = investigation["metrics"]
        diagnosis = investigation["diagnosis"]

        if any(token in normalized for token in ("which team", "largest contributor", "哪个团队", "贡献最大")):
            rows = metrics["team_contribution_analysis"]["segments"]
            if not rows:
                answer = "The verified run does not contain enough team-contribution evidence to answer that follow-up."
                evidence_ids: tuple[str, ...] = ()
                status = "insufficient_evidence"
            else:
                top = rows[0]
                contribution_records = [
                    row
                    for row in previous.audit_evidence
                    if row["tool_name"] == "contribution_analysis"
                ]
                evidence_ids = tuple(row["evidence_id"] for row in contribution_records[-1:])
                answer = (
                    f"{top['segment']} is the largest negative team contributor in the verified decomposition "
                    f"({float(top['total_contribution_pp']):.2f} pp)."
                )
                status = "verified"
        elif any(token in normalized for token in ("what evidence", "why crm", "routing change", "什么证据", "为什么是 crm", "证据")):
            source = metrics.get("document_evidence")
            if diagnosis.get("root_cause_status") != "supported_candidate" or not source:
                answer = (
                    "The current verified evidence is insufficient to support the CRM routing change as a root-cause candidate. "
                    "FitzSight withholds the attribution rather than filling the gap."
                )
                evidence_ids = tuple(previous.final_answer.evidence_ids)
                status = "insufficient_evidence"
            else:
                answer = (
                    "The candidate is supported by the affected-vs-control FTD movement, statistical validation, response-latency signal, "
                    f"nearby operational event evidence, and synthetic document source {source['source_ref']}. "
                    "It remains a supported candidate rather than a proven real-world causal conclusion."
                )
                evidence_ids = tuple(previous.final_answer.evidence_ids)
                status = "verified_with_guardrail"
        else:
            raise ValueError(
                "Unsupported follow-up. Approved v0.12 follow-ups ask for the largest team contributor or the evidence behind the CRM routing candidate."
            )

        record = self.registry.register(
            "agent.follow_up",
            {
                "intent": previous.plan.intent,
                "follow_up_question": question,
                "source_final_answer_evidence_id": previous.final_answer_evidence_id,
            },
            {"status": status, "answer": answer, "evidence_ids": list(evidence_ids)},
        )
        return FollowUpAnswer(
            status=status,
            question=question,
            answer=answer,
            evidence_ids=evidence_ids,
            evidence_record_id=record.evidence_id,
        )
