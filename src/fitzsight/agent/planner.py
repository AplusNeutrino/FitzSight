from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable, Protocol

from .catalog import (
    ACTION_PURPOSES,
    CRM_ACTIONS,
    CRM_INTENT,
    CUSTOMER_INTELLIGENCE_ACTIONS,
    CUSTOMER_INTELLIGENCE_INTENT,
    FALSE_CORRELATION_ACTIONS,
    FALSE_CORRELATION_INTENT,
    INTENT_ACTIONS,
    MARKETING_LEAD_QUALITY_ACTIONS,
    MARKETING_LEAD_QUALITY_INTENT,
    NET_DEPOSIT_ACTIONS,
    NET_DEPOSIT_INTENT,
    actions_for_intent,
    classify_supported_intent,
)
from .models import AgentPlan, AgentPlanStep


class PlannerError(ValueError):
    """Base error for constrained FitzSight planning."""


class UnsupportedIntentError(PlannerError):
    """Raised when the question is outside the current Agent scope."""


class PlanValidationError(PlannerError):
    """Raised when planner output violates the constrained plan policy."""


class Planner(Protocol):
    mode: str

    def plan(self, question: str) -> AgentPlan: ...


def _classify(question: str) -> str:
    try:
        return classify_supported_intent(question)
    except ValueError as exc:
        raise UnsupportedIntentError(
            "Question is outside the approved FitzSight v0.7 intent catalog."
        ) from exc


def validate_plan(plan: AgentPlan) -> AgentPlan:
    """Validate planner output against the v0.7 multi-intent policy.

    Planner/model output is untrusted. It may select only one approved intent and
    the exact published high-level action sequence for that intent. It may not
    emit SQL, table names, arbitrary tool parameters, or high-impact actions.
    """

    if plan.plan_version != "0.7":
        raise PlanValidationError("Unsupported plan_version; expected '0.7'")
    if plan.intent not in INTENT_ACTIONS:
        raise UnsupportedIntentError(f"Unsupported intent: {plan.intent}")
    if not plan.question.strip():
        raise PlanValidationError("question must be non-empty")

    expected = actions_for_intent(plan.intent)
    if len(plan.steps) != len(expected):
        raise PlanValidationError(
            f"{plan.intent} requires exactly {len(expected)} constrained steps"
        )

    actions = tuple(step.action for step in plan.steps)
    if actions != expected:
        raise PlanValidationError(
            "Plan actions must match the approved intent-specific action sequence; "
            "arbitrary tool selection is rejected"
        )

    seen_ids: set[str] = set()
    forbidden = (
        "select ",
        "insert ",
        "update ",
        "delete ",
        "drop ",
        "pragma ",
        "execute_trade",
        "send_money",
        "freeze_account",
    )
    for step in plan.steps:
        if not step.step_id or step.step_id in seen_ids:
            raise PlanValidationError("Plan step IDs must be non-empty and unique")
        seen_ids.add(step.step_id)

        if not step.purpose.strip() or len(step.purpose) > 300:
            raise PlanValidationError(
                "Each plan step purpose must contain 1–300 characters"
            )
        lowered = step.purpose.lower()
        if any(token in lowered for token in forbidden):
            raise PlanValidationError(
                "Planner purpose contains executable SQL or a prohibited high-impact action"
            )

    # The deterministic scope classifier is an independent gate. A model cannot
    # relabel an unsupported question as an approved intent.
    classified = _classify(plan.question)
    if classified != plan.intent:
        raise PlanValidationError(
            f"Planner intent {plan.intent!r} conflicts with approved local classifier {classified!r}"
        )

    return plan


@dataclass
class ConstrainedRulePlanner:
    """Deterministic no-API planner used as the reliable competition fallback."""

    mode: str = "deterministic_fallback"

    def plan(self, question: str) -> AgentPlan:
        intent = _classify(question)
        actions = actions_for_intent(intent)
        plan = AgentPlan(
            plan_version="0.7",
            intent=intent,
            question=question,
            planner_mode=self.mode,
            steps=tuple(
                AgentPlanStep(
                    step_id=f"AP{index}",
                    action=action,
                    purpose=ACTION_PURPOSES[action],
                )
                for index, action in enumerate(actions, start=1)
            ),
        )
        return validate_plan(plan)


class StructuredJSONPlanner:
    """Provider-neutral adapter for structured model planner output."""

    mode = "structured_llm_adapter"

    def __init__(self, completion_fn: Callable[[str], str]) -> None:
        self.completion_fn = completion_fn

    @staticmethod
    def prompt(question: str) -> str:
        intent_lines = []
        for intent, actions in INTENT_ACTIONS.items():
            intent_lines.append(f"- {intent}: {', '.join(actions)}")
        catalog = "\n".join(intent_lines)
        return (
            "You are the constrained planning component for FitzSight. "
            "Return JSON only. Do not write SQL, code, table names, numeric results, "
            "tool arguments, investment advice, account actions, or customer-contact actions. "
            "Choose exactly one supported intent and reproduce that intent's required action "
            "sequence exactly. Output object keys: intent, steps. Each step must contain "
            "action and purpose.\nSupported intent catalog:\n"
            f"{catalog}\nQuestion: {question}"
        )

    @staticmethod
    def parse(question: str, raw: str, *, planner_mode: str = "structured_llm_adapter") -> AgentPlan:
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise PlanValidationError(
                f"Planner returned invalid JSON: {exc.msg}"
            ) from exc

        if not isinstance(payload, dict) or set(payload) != {"intent", "steps"}:
            raise PlanValidationError(
                "Planner JSON must contain exactly: intent, steps"
            )
        if not isinstance(payload["intent"], str):
            raise PlanValidationError("intent must be a string")
        if not isinstance(payload["steps"], list):
            raise PlanValidationError("steps must be a list")

        steps: list[AgentPlanStep] = []
        for index, raw_step in enumerate(payload["steps"], start=1):
            if (
                not isinstance(raw_step, dict)
                or set(raw_step) != {"action", "purpose"}
            ):
                raise PlanValidationError(
                    "Each planner step must contain exactly: action, purpose"
                )
            if not isinstance(raw_step["action"], str) or not isinstance(
                raw_step["purpose"], str
            ):
                raise PlanValidationError(
                    "Planner step action/purpose must be strings"
                )
            steps.append(
                AgentPlanStep(
                    step_id=f"AP{index}",
                    action=raw_step["action"],
                    purpose=raw_step["purpose"],
                )
            )

        return validate_plan(
            AgentPlan(
                plan_version="0.7",
                intent=payload["intent"],
                question=question,
                planner_mode=planner_mode,
                steps=tuple(steps),
            )
        )

    def plan(self, question: str) -> AgentPlan:
        _classify(question)  # fail before model invocation
        raw = self.completion_fn(self.prompt(question))
        return self.parse(question, raw)


__all__ = [
    "Planner",
    "PlannerError",
    "UnsupportedIntentError",
    "PlanValidationError",
    "ConstrainedRulePlanner",
    "StructuredJSONPlanner",
    "validate_plan",
    "CRM_INTENT",
    "CRM_ACTIONS",
    "NET_DEPOSIT_INTENT",
    "NET_DEPOSIT_ACTIONS",
    "CUSTOMER_INTELLIGENCE_INTENT",
    "CUSTOMER_INTELLIGENCE_ACTIONS",
]
