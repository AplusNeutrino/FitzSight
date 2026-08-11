import json
from pathlib import Path

from fitzsight.agent.planner import (
    CUSTOMER_INTELLIGENCE_ACTIONS,
    CUSTOMER_INTELLIGENCE_INTENT,
    ConstrainedRulePlanner,
    StructuredJSONPlanner,
)
from fitzsight.runtime import build_agent_runtime

QUESTION = (
    "How are European customer segments distributed by behavioral value, "
    "and which segment contributes most to deposits?"
)


def test_rule_planner_routes_customer_intelligence_intent():
    plan = ConstrainedRulePlanner().plan(QUESTION)
    assert plan.plan_version == "0.7"
    assert plan.intent == CUSTOMER_INTELLIGENCE_INTENT
    assert tuple(step.action for step in plan.steps) == CUSTOMER_INTELLIGENCE_ACTIONS


def test_structured_planner_accepts_customer_intelligence_intent():
    raw = json.dumps(
        {
            "intent": CUSTOMER_INTELLIGENCE_INTENT,
            "steps": [
                {"action": action, "purpose": f"Safely perform {action}."}
                for action in CUSTOMER_INTELLIGENCE_ACTIONS
            ],
        }
    )
    plan = StructuredJSONPlanner(lambda _prompt: raw).plan(QUESTION)
    assert plan.intent == CUSTOMER_INTELLIGENCE_INTENT
    assert plan.plan_version == "0.7"


def test_customer_intelligence_agent_runs_and_verifies(tmp_path: Path):
    store, registry, agent = build_agent_runtime(
        data_dir=tmp_path / "data",
        backend="sqlite",
        planner=ConstrainedRulePlanner(),
    )
    try:
        result = agent.run(QUESTION).to_dict()
        assert result["plan"]["intent"] == CUSTOMER_INTELLIGENCE_INTENT
        assert result["verification"]["passed"] is True
        assert result["verification"]["verified_claims"] == 5
        assert result["final_answer"]["status"] == "verified"
        assert result["final_answer"]["headline"] == (
            "A verified customer-value segmentation profile was generated."
        )
        assert result["investigation"]["diagnosis"]["analysis_type"] == (
            "customer_intelligence_segmentation"
        )
        assert result["investigation"]["diagnosis"]["segmentation_coverage"] == 1.0
    finally:
        store.close()
