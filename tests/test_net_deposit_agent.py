from pathlib import Path

from fitzsight.agent.planner import ConstrainedRulePlanner, NET_DEPOSIT_INTENT
from fitzsight.runtime import build_agent_runtime

QUESTION = "Why did European net deposits fall in the week starting August 3?"


def test_net_deposit_intent_runs_end_to_end_and_verifies(tmp_path: Path):
    store, registry, agent = build_agent_runtime(
        data_dir=tmp_path / "data",
        backend="sqlite",
        planner=ConstrainedRulePlanner(),
    )
    try:
        result = agent.run(QUESTION).to_dict()
        assert result["plan"]["intent"] == NET_DEPOSIT_INTENT
        assert result["verification"]["passed"] is True
        assert result["verification"]["verified_claims"] == 5
        assert result["final_answer"]["status"] == "verified"
        assert result["investigation"]["diagnosis"]["net_deposit_declined"] is True
        assert result["investigation"]["diagnosis"]["withdrawal_pressure_increased"] is True
        assert result["investigation"]["diagnosis"]["withdrawal_concentration_high"] is True
        assert result["investigation"]["diagnosis"]["driver_type"] == "observed_withdrawal_concentration"
        assert (
            result["investigation"]["metrics"]["customer_concentration"][
                "share_of_current_withdrawals"
            ]
            > 0.5
        )
        assert len(result["audit_evidence"]) >= 18

        sql_records = [
            record
            for record in result["audit_evidence"]
            if record["tool_name"] == "read_only_sql"
        ]
        assert sql_records
        assert all("_gt" not in str(record["parameters"].get("sql", "")) for record in sql_records)
    finally:
        store.close()
