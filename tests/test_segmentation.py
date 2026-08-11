from pathlib import Path

from fitzsight.agent.planner import ConstrainedRulePlanner
from fitzsight.runtime import build_agent_runtime
from fitzsight.tools.segmentation import CustomerSegmentationTool

QUESTION = (
    "How are European customer segments distributed by behavioral value, "
    "and which segment contributes most to deposits?"
)


def test_customer_segmentation_tool_uses_observable_features_only(tmp_path: Path):
    store, registry, agent = build_agent_runtime(
        data_dir=tmp_path / "data",
        backend="sqlite",
        planner=ConstrainedRulePlanner(),
    )
    try:
        # Reuse the runtime's SQL/store through the Agent path; an end-to-end run
        # proves the segmentation result is registered and verifier-compatible.
        result = agent.run(QUESTION).to_dict()
        segmentation = result["investigation"]["metrics"]["segmentation"]

        assert segmentation["method"] == "behavioral_value_score_v1"
        assert segmentation["coverage"] == 1.0
        assert segmentation["customer_count"] > 1000
        assert segmentation["segment_count"] >= 4
        assert segmentation["top_deposit_segment"] == "High Value"
        assert segmentation["high_value_avg_deposits"] > segmentation["low_activity_avg_deposits"]

        sql_records = [
            record for record in result["audit_evidence"]
            if record["tool_name"] == "read_only_sql"
        ]
        assert sql_records
        assert all(
            "_gt" not in str(record["parameters"].get("sql", "")).lower()
            for record in sql_records
        )
    finally:
        store.close()
