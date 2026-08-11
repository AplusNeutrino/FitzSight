import json

import pytest

from fitzsight.agent.planner import (
    CRM_ACTIONS,
    CRM_INTENT,
    NET_DEPOSIT_ACTIONS,
    NET_DEPOSIT_INTENT,
    ConstrainedRulePlanner,
    PlanValidationError,
    StructuredJSONPlanner,
)

CRM_QUESTION = "Why did European FTD conversion deteriorate after July 15?"
NET_QUESTION = "Why did European net deposits fall in the week starting August 3?"


def test_rule_planner_routes_second_business_intent():
    plan = ConstrainedRulePlanner().plan(NET_QUESTION)
    assert plan.plan_version == "0.5"
    assert plan.intent == NET_DEPOSIT_INTENT
    assert tuple(step.action for step in plan.steps) == NET_DEPOSIT_ACTIONS


def test_structured_planner_accepts_second_intent_exact_sequence():
    raw = json.dumps(
        {
            "intent": NET_DEPOSIT_INTENT,
            "steps": [
                {"action": action, "purpose": f"Safely perform {action}."}
                for action in NET_DEPOSIT_ACTIONS
            ],
        }
    )
    plan = StructuredJSONPlanner(lambda _prompt: raw).plan(NET_QUESTION)
    assert plan.intent == NET_DEPOSIT_INTENT
    assert plan.plan_version == "0.5"


def test_model_cannot_relabel_crm_question_as_net_deposit_intent():
    raw = json.dumps(
        {
            "intent": NET_DEPOSIT_INTENT,
            "steps": [
                {"action": action, "purpose": f"Safely perform {action}."}
                for action in NET_DEPOSIT_ACTIONS
            ],
        }
    )
    with pytest.raises(PlanValidationError):
        StructuredJSONPlanner(lambda _prompt: raw).plan(CRM_QUESTION)


def test_rule_planner_keeps_original_crm_intent():
    plan = ConstrainedRulePlanner().plan(CRM_QUESTION)
    assert plan.intent == CRM_INTENT
    assert tuple(step.action for step in plan.steps) == CRM_ACTIONS
