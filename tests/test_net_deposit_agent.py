from pathlib import Path

from fitzsight.agent.planner import ConstrainedRulePlanner, NET_DEPOSIT_INTENT
from fitzsight.runtime import build_agent_runtime

QUESTION = "Why did European net deposits fall in the week starting August 3?"


def test_net_deposit_intent_runs_end_to_end_and_verifies(tmp_path: Path):
    store, registry, agent = build_agent_runtime(
        data_mode="demo",
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


import json
import pandas as pd
import pytest


@pytest.mark.parametrize("backend", ["sqlite", "duckdb"])
@pytest.mark.parametrize("empty", [False, True])
def test_zero_withdrawal_denominator_is_unavailable_not_zero_percent(tmp_path, backend, empty):
    data_dir = tmp_path / "data"
    store, _, _ = build_agent_runtime(data_mode="demo", data_dir=data_dir, backend=backend, planner=ConstrainedRulePlanner())
    store.close()
    # Modify actual synthetic CSVs, then exercise import, SQL, engine and verifier.
    path = data_dir / "withdrawals.csv"
    withdrawals = pd.read_csv(path)
    if empty:
        withdrawals = withdrawals.iloc[:0]
    else:
        withdrawals["amount"] = 0.0
    withdrawals.to_csv(path, index=False)
    store, _, agent = build_agent_runtime(data_mode="import", data_dir=data_dir, backend=backend, planner=ConstrainedRulePlanner())
    try:
        result = agent.run(QUESTION).to_dict()
        investigation = result["investigation"]
        concentration = investigation["metrics"]["customer_concentration"]
        assert concentration["current_total_withdrawals"] == 0
        assert concentration["share_of_current_withdrawals"] is None
        assert concentration["calculation_status"] == "unavailable"
        assert concentration["unavailable_reason"] == "nonpositive_total_withdrawals"
        claim = next(c for c in investigation["claims"] if c["claim_id"] == "N-C3")
        assert claim["status"] == "insufficient_evidence"
        assert "unavailable" in claim["text"] and "%" not in claim["text"]
        assert investigation["diagnosis"]["withdrawal_concentration_high"] is None
        assert investigation["diagnosis"]["driver_type"] == "undetermined"
        assert result["verification"]["passed"] is True
        json.dumps(concentration, allow_nan=False)
    finally:
        store.close()
