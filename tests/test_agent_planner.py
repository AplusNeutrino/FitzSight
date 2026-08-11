import json

import pytest

from fitzsight.agent.planner import (
    CRM_ACTIONS,
    CRM_INTENT,
    ConstrainedRulePlanner,
    PlanValidationError,
    StructuredJSONPlanner,
    UnsupportedIntentError,
)

QUESTION = "Why did European FTD conversion deteriorate after July 15?"


def _valid_payload():
    return {
        "intent": CRM_INTENT,
        "steps": [
            {"action": action, "purpose": f"Safely perform {action.replace('_', ' ')}."}
            for action in CRM_ACTIONS
        ],
    }


def test_deterministic_planner_builds_approved_sequence():
    plan = ConstrainedRulePlanner().plan(QUESTION)
    assert plan.intent == CRM_INTENT
    assert tuple(step.action for step in plan.steps) == CRM_ACTIONS
    assert plan.planner_mode == "deterministic_fallback"


def test_deterministic_planner_refuses_unrelated_financial_question():
    with pytest.raises(UnsupportedIntentError):
        ConstrainedRulePlanner().plan("Which stock should I buy tomorrow?")


def test_structured_llm_adapter_accepts_only_valid_json_plan():
    raw = json.dumps(_valid_payload())
    plan = StructuredJSONPlanner(lambda prompt: raw).plan(QUESTION)
    assert plan.intent == CRM_INTENT
    assert plan.planner_mode == "structured_llm_adapter"


def test_structured_llm_adapter_rejects_unknown_action():
    payload = _valid_payload()
    payload["steps"][3]["action"] = "execute_trade"
    with pytest.raises(PlanValidationError):
        StructuredJSONPlanner(lambda prompt: json.dumps(payload)).plan(QUESTION)


def test_structured_llm_adapter_rejects_sql_in_purpose():
    payload = _valid_payload()
    payload["steps"][0]["purpose"] = "SELECT * FROM customers"
    with pytest.raises(PlanValidationError):
        StructuredJSONPlanner(lambda prompt: json.dumps(payload)).plan(QUESTION)


def test_structured_llm_adapter_rejects_malformed_json():
    with pytest.raises(PlanValidationError):
        StructuredJSONPlanner(lambda prompt: "not-json").plan(QUESTION)


def test_structured_llm_adapter_refuses_scope_before_model_call():
    called = False

    def completion(_prompt: str) -> str:
        nonlocal called
        called = True
        return json.dumps(_valid_payload())

    with pytest.raises(UnsupportedIntentError):
        StructuredJSONPlanner(completion).plan("Summarize today's market news")
    assert called is False
