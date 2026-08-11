from pathlib import Path

from fitzsight.agent.planner import ConstrainedRulePlanner
from fitzsight.demo import DEMO_QUESTIONS
from fitzsight.runtime import build_agent_runtime
from fitzsight.ui.presenter import build_presentation


def test_presenter_builds_kpi_chart_trace_and_evidence_for_all_intents(tmp_path: Path):
    for _label, question in DEMO_QUESTIONS.items():
        store, _registry, agent = build_agent_runtime(
            data_dir=tmp_path,
            backend="sqlite",
            planner=ConstrainedRulePlanner(),
        )
        try:
            result = agent.run(question).to_dict()
            view = build_presentation(result, backend=store.backend)
        finally:
            store.close()

        assert view.status == "verified"
        assert view.verification_passed is True
        assert len(view.kpis) == 5
        assert len(view.chart.categories) >= 1
        assert len(view.chart.series) >= 1
        assert len(view.trace) >= 1
        assert len(view.evidence_cards) >= 1
        assert all(card.status == "success" for card in view.evidence_cards)
        assert view.verified_claims == view.total_claims


def test_presenter_is_json_safe_for_submission_assets(tmp_path: Path):
    question = next(iter(DEMO_QUESTIONS.values()))
    store, _registry, agent = build_agent_runtime(
        data_dir=tmp_path,
        backend="sqlite",
        planner=ConstrainedRulePlanner(),
    )
    try:
        view = build_presentation(agent.run(question).to_dict(), backend=store.backend)
    finally:
        store.close()
    payload = view.to_dict()
    assert payload["product"] == "FitzSight"
    assert payload["kpis"][0]["label"]
    assert payload["chart"]["series"][0]["values"]
