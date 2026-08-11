from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable, Protocol

from fitzsight.investigation.engine import DeterministicInvestigationEngine
from .models import AgentPlan, AgentPlanStep


class PlannerError(ValueError):
    """Base error for constrained FitzSight planning."""


class UnsupportedIntentError(PlannerError):
    """Raised when the question is outside the current Agent MVP scope."""


class PlanValidationError(PlannerError):
    """Raised when planner output violates the constrained plan policy."""


CRM_INTENT = "crm_routing_ftd_investigation"
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


class Planner(Protocol):
    mode: str

    def plan(self, question: str) -> AgentPlan: ...


def validate_plan(plan: AgentPlan) -> AgentPlan:
    """Validate planner output against the v0.4 Agent policy.

    The LLM is never allowed to emit SQL, table names, arbitrary tool arguments,
    or novel actions. For the current benchmark intent it may only select the
    published high-level analysis actions, and all required steps must be present
    exactly once in the safe sequence.
    """

    if plan.plan_version != "0.4":
        raise PlanValidationError("Unsupported plan_version; expected '0.4'")
    if plan.intent != CRM_INTENT:
        raise UnsupportedIntentError(f"Unsupported intent: {plan.intent}")
    if not plan.question.strip():
        raise PlanValidationError("question must be non-empty")
    if len(plan.steps) != len(CRM_ACTIONS):
        raise PlanValidationError(
            f"Current intent requires exactly {len(CRM_ACTIONS)} constrained steps"
        )

    actions = tuple(step.action for step in plan.steps)
    if actions != CRM_ACTIONS:
        raise PlanValidationError(
            "Plan actions must match the approved action sequence; arbitrary tool selection is rejected"
        )

    seen_ids: set[str] = set()
    for step in plan.steps:
        if not step.step_id or step.step_id in seen_ids:
            raise PlanValidationError("Plan step IDs must be non-empty and unique")
        seen_ids.add(step.step_id)
        if not step.purpose.strip() or len(step.purpose) > 300:
            raise PlanValidationError("Each plan step purpose must contain 1–300 characters")
        lowered = step.purpose.lower()
        if any(token in lowered for token in ("select ", "insert ", "update ", "delete ", "drop ", "pragma ")):
            raise PlanValidationError("Planner purpose must not contain executable SQL")

    return plan


@dataclass
class ConstrainedRulePlanner:
    """Deterministic no-API planner used as the reliable competition fallback."""

    mode: str = "deterministic_fallback"

    def plan(self, question: str) -> AgentPlan:
        if not DeterministicInvestigationEngine.supports(question):
            raise UnsupportedIntentError(
                "FitzSight v0.4 currently supports the European FTD conversion / July 15 benchmark intent only."
            )
        base = DeterministicInvestigationEngine.plan(question)
        plan = AgentPlan(
            plan_version="0.4",
            intent=base.intent,
            question=question,
            planner_mode=self.mode,
            steps=tuple(
                AgentPlanStep(step.step_id, step.action, step.purpose) for step in base.steps
            ),
        )
        return validate_plan(plan)


class StructuredJSONPlanner:
    """Provider-neutral adapter for a future LLM planner.

    `completion_fn` receives a strict prompt and must return JSON text. This class
    intentionally has no dependency on a specific model provider. It allows the
    Agent contract and safety policy to be tested before API credentials are added.
    """

    mode = "structured_llm_adapter"

    def __init__(self, completion_fn: Callable[[str], str]) -> None:
        self.completion_fn = completion_fn

    @staticmethod
    def prompt(question: str) -> str:
        actions = ", ".join(CRM_ACTIONS)
        return (
            "You are the constrained planning component for FitzSight. "
            "Return JSON only. Do not write SQL, code, table names, numeric results, or tool arguments. "
            f"The only supported intent is {CRM_INTENT}. "
            f"The required action sequence is exactly: {actions}. "
            "Output object keys: intent, steps. Each step must contain action and purpose. "
            f"Question: {question}"
        )

    @staticmethod
    def parse(question: str, raw: str) -> AgentPlan:
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise PlanValidationError(f"Planner returned invalid JSON: {exc.msg}") from exc

        if not isinstance(payload, dict) or set(payload) != {"intent", "steps"}:
            raise PlanValidationError("Planner JSON must contain exactly: intent, steps")
        if not isinstance(payload["intent"], str):
            raise PlanValidationError("intent must be a string")
        if not isinstance(payload["steps"], list):
            raise PlanValidationError("steps must be a list")

        steps: list[AgentPlanStep] = []
        for index, raw_step in enumerate(payload["steps"], start=1):
            if not isinstance(raw_step, dict) or set(raw_step) != {"action", "purpose"}:
                raise PlanValidationError("Each planner step must contain exactly: action, purpose")
            if not isinstance(raw_step["action"], str) or not isinstance(raw_step["purpose"], str):
                raise PlanValidationError("Planner step action/purpose must be strings")
            steps.append(
                AgentPlanStep(
                    step_id=f"AP{index}",
                    action=raw_step["action"],
                    purpose=raw_step["purpose"],
                )
            )

        return validate_plan(
            AgentPlan(
                plan_version="0.4",
                intent=payload["intent"],
                question=question,
                planner_mode="structured_llm_adapter",
                steps=tuple(steps),
            )
        )

    def plan(self, question: str) -> AgentPlan:
        if not DeterministicInvestigationEngine.supports(question):
            # Do not send unsupported financial questions to a model and hope it
            # invents a workflow. Scope refusal happens before model invocation.
            raise UnsupportedIntentError(
                "Question is outside the currently approved FitzSight Agent intent."
            )
        raw = self.completion_fn(self.prompt(question))
        return self.parse(question, raw)
