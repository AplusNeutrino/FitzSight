from pathlib import Path

from fitzsight.agent.catalog import (
    FALSE_CORRELATION_ACTIONS,
    FALSE_CORRELATION_INTENT,
    MARKETING_LEAD_QUALITY_ACTIONS,
    MARKETING_LEAD_QUALITY_INTENT,
)
from fitzsight.agent.planner import ConstrainedRulePlanner
from fitzsight.runtime import build_agent_runtime

MARKETING_Q = "Why did Americas lead volume rise while FTD conversion fell after June 15?"
FALSE_Q = "Why did Asia FTD conversion fall after July 20, and is the nearby office relocation the cause?"


def test_v07_rule_planner_routes_new_intents():
    planner = ConstrainedRulePlanner()
    marketing = planner.plan(MARKETING_Q)
    false_corr = planner.plan(FALSE_Q)
    assert marketing.plan_version == "0.7"
    assert marketing.intent == MARKETING_LEAD_QUALITY_INTENT
    assert tuple(step.action for step in marketing.steps) == MARKETING_LEAD_QUALITY_ACTIONS
    assert false_corr.plan_version == "0.7"
    assert false_corr.intent == FALSE_CORRELATION_INTENT
    assert tuple(step.action for step in false_corr.steps) == FALSE_CORRELATION_ACTIONS


def test_marketing_and_false_correlation_intents_run_end_to_end(tmp_path: Path):
    data_dir = tmp_path / "data"

    store, _registry, agent = build_agent_runtime(
        data_dir=data_dir,
        backend="sqlite",
        planner=ConstrainedRulePlanner(),
    )
    try:
        marketing = agent.run(MARKETING_Q).to_dict()
        assert marketing["plan"]["intent"] == MARKETING_LEAD_QUALITY_INTENT
        assert marketing["verification"]["passed"] is True
        assert marketing["final_answer"]["status"] == "verified"
        diagnosis = marketing["investigation"]["diagnosis"]
        assert diagnosis["lead_volume_increased"] is True
        assert diagnosis["conversion_declined"] is True
        assert diagnosis["paid_search_share_increased"] is True
        assert diagnosis["top_negative_channel_performance_effect"] == "Paid Search"
        assert diagnosis["paid_search_shift_significant"] is True
        assert diagnosis["root_cause_status"] == "supported_candidate"
    finally:
        store.close()

    store, _registry, agent = build_agent_runtime(
        data_dir=data_dir,
        backend="sqlite",
        planner=ConstrainedRulePlanner(),
    )
    try:
        false_corr = agent.run(FALSE_Q).to_dict()
        assert false_corr["plan"]["intent"] == FALSE_CORRELATION_INTENT
        assert false_corr["verification"]["passed"] is True
        assert false_corr["final_answer"]["status"] == "verified"
        diagnosis = false_corr["investigation"]["diagnosis"]
        assert diagnosis["top_negative_channel_performance_effect"] == "Affiliate"
        assert diagnosis["affiliate_shift_significant"] is True
        assert diagnosis["nearby_event_found"] is True
        assert diagnosis["nearby_event_cause_supported"] is False
        assert diagnosis["false_correlation_rejected"] is True
        assert diagnosis["root_cause_status"] == "supported_candidate"
    finally:
        store.close()
