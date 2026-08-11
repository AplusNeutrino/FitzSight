from dataclasses import replace

import pytest

from fitzsight.agent.models import AgentPlanStep
from fitzsight.agent.planner import (
    ConstrainedRulePlanner,
    PlanValidationError,
    UnsupportedIntentError,
    validate_plan,
)

CRM_Q = "Why did European FTD conversion deteriorate after July 15?"


def test_scope_gate_refuses_trade_and_aml_actions():
    planner = ConstrainedRulePlanner()
    with pytest.raises(UnsupportedIntentError):
        planner.plan("Execute a EURUSD trade for the highest-value customer.")
    with pytest.raises(UnsupportedIntentError):
        planner.plan("Which customers are suspicious and should have their accounts frozen?")


def test_plan_validator_catches_sql_and_high_impact_action():
    plan = ConstrainedRulePlanner().plan(CRM_Q)
    sql_steps = list(plan.steps)
    sql_steps[0] = replace(sql_steps[0], purpose="SELECT * FROM sales_activity")
    with pytest.raises(PlanValidationError):
        validate_plan(replace(plan, steps=tuple(sql_steps)))

    unsafe_steps = list(plan.steps)
    unsafe_steps[0] = AgentPlanStep(unsafe_steps[0].step_id, "execute_trade", "Execute a trade.")
    with pytest.raises(PlanValidationError):
        validate_plan(replace(plan, steps=tuple(unsafe_steps)))
