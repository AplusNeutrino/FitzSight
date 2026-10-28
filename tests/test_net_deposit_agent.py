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


@pytest.mark.parametrize("backend", ["sqlite", "duckdb"])
@pytest.mark.parametrize("selection", ["target_only", "controls_only"])
def test_missing_regional_comparison_is_not_filled_with_zero(tmp_path, backend, selection):
    data_dir = tmp_path / "data"
    store, _, _ = build_agent_runtime(data_mode="demo", data_dir=data_dir,
                                      backend=backend, planner=ConstrainedRulePlanner())
    store.close()
    path = data_dir / "customers.csv"
    customers = pd.read_csv(path)
    mask = customers["region"].eq("Europe")
    customers[mask if selection == "target_only" else ~mask].to_csv(path, index=False)
    store, _, agent = build_agent_runtime(data_mode="import", data_dir=data_dir,
                                          backend=backend, planner=ConstrainedRulePlanner())
    try:
        result = agent.run(QUESTION).to_dict()
        investigation = result["investigation"]
        regional = investigation["metrics"]["regional_control"]
        assert regional["calculation_status"] == "unavailable"
        if selection == "target_only":
            assert regional["other_region_median_change"] is None
            assert regional["control_region_count"] == 0
            assert regional["europe_change"] is not None
            assert regional["unavailable_reason"] == "missing_control_regions"
        else:
            assert regional["europe_change"] is None
            assert regional["other_region_median_change"] is not None
            assert regional["unavailable_reason"] == "missing_target_region"
        assert investigation["diagnosis"]["europe_worse_than_other_region_median"] is None
        claim = next(c for c in investigation["claims"] if c["claim_id"] == "N-C4")
        assert claim["status"] == "insufficient_evidence"
        assert "unavailable" in claim["text"] and "$" not in claim["text"]
        assert result["verification"]["passed"] is True
        json.dumps(regional, allow_nan=False)
    finally:
        store.close()


@pytest.mark.parametrize("backend", ["sqlite", "duckdb"])
def test_real_zero_regional_change_remains_computable(tmp_path, backend):
    data_dir = tmp_path / "data"
    store, _, _ = build_agent_runtime(data_mode="demo", data_dir=data_dir,
                                      backend=backend, planner=ConstrainedRulePlanner())
    store.close()
    for table in ("deposits", "withdrawals"):
        path = data_dir / f"{table}.csv"
        rows = pd.read_csv(path)
        rows["amount"] = 0.0
        rows.to_csv(path, index=False)
    store, _, agent = build_agent_runtime(data_mode="import", data_dir=data_dir,
                                          backend=backend, planner=ConstrainedRulePlanner())
    try:
        result = agent.run(QUESTION).to_dict()
        investigation = result["investigation"]
        regional = investigation["metrics"]["regional_control"]
        assert regional["europe_change"] == 0
        assert regional["other_region_median_change"] == 0
        assert regional["calculation_status"] == "computed"
        assert regional["unavailable_reason"] is None
        assert regional["control_region_count"] > 0
        claim = next(c for c in investigation["claims"] if c["claim_id"] == "N-C4")
        assert claim["status"] == "supported" and "$0.00" in claim["text"]
        assert investigation["diagnosis"]["europe_worse_than_other_region_median"] is False
        assert result["verification"]["passed"] is True
    finally:
        store.close()


@pytest.mark.parametrize("backend", ["sqlite", "duckdb"])
def test_non_usd_control_region_cannot_be_labeled_dollars(tmp_path, backend):
    data_dir = tmp_path / "data"
    store, _, _ = build_agent_runtime(data_mode="demo", data_dir=data_dir,
                                      backend=backend, planner=ConstrainedRulePlanner())
    store.close()
    customers = pd.read_csv(data_dir / "customers.csv")
    controls = set(customers.loc[customers["region"] != "Europe", "customer_id"])
    path = data_dir / "deposits.csv"
    deposits = pd.read_csv(path)
    mask = deposits["customer_id"].isin(controls)
    assert mask.any()
    deposits.loc[mask, "currency"] = "EUR"
    deposits.to_csv(path, index=False)
    store, _, agent = build_agent_runtime(data_mode="import", data_dir=data_dir,
                                          backend=backend, planner=ConstrainedRulePlanner())
    try:
        with pytest.raises(ValueError, match="Regional.*requires USD"):
            agent.run(QUESTION)
    finally:
        store.close()


@pytest.mark.parametrize("backend", ["sqlite", "duckdb"])
@pytest.mark.parametrize("event_case", ["empty", "wrong_type", "wrong_region", "outside_window", "present_zero_cashflow"])
def test_event_claim_matches_imported_log_without_driver_overclaim(tmp_path, backend, event_case):
    data_dir = tmp_path / "data"
    store, _, _ = build_agent_runtime(data_mode="demo", data_dir=data_dir,
                                      backend=backend, planner=ConstrainedRulePlanner())
    store.close()
    path = data_dir / "business_events.csv"
    events = pd.read_csv(path)
    # Retain a valid schema and use one controlled event for each counterexample.
    events = events.iloc[:1].copy()
    events["region"] = "Europe"
    events["event_type"] = "HIGH_VALUE_WITHDRAWAL_CLUSTER"
    events["date"] = "2026-08-05"
    if event_case == "empty":
        events = events.iloc[:0]
    elif event_case == "wrong_type":
        events["event_type"] = "UNRELATED_EVENT"
    elif event_case == "wrong_region":
        events["region"] = "Asia"
    elif event_case == "outside_window":
        events["date"] = "2026-08-08"  # Exclusive upper boundary.
    else:
        for table in ("deposits", "withdrawals"):
            cash_path = data_dir / f"{table}.csv"
            cash = pd.read_csv(cash_path)
            cash["amount"] = 0.0
            cash.to_csv(cash_path, index=False)
    events.to_csv(path, index=False)
    store, _, agent = build_agent_runtime(data_mode="import", data_dir=data_dir,
                                          backend=backend, planner=ConstrainedRulePlanner())
    try:
        result = agent.run(QUESTION).to_dict()
        investigation = result["investigation"]
        claim = next(c for c in investigation["claims"] if c["claim_id"] == "N-C5")
        present = event_case == "present_zero_cashflow"
        assert investigation["diagnosis"]["matching_operational_event_found"] is present
        assert bool(investigation["metrics"]["nearby_business_events"]) is present
        assert claim["status"] == ("supported_with_guardrail" if present else "insufficient_evidence")
        assert claim["confidence"] == ("high" if present else "low")
        assert "supported observed driver" not in claim["text"]
        if present:
            assert "event is present" in claim["text"]
            assert investigation["diagnosis"]["root_cause_status"] == "insufficient_evidence"
        else:
            assert "No matching" in claim["text"]
            assert "event is present" not in claim["text"]
            assert "does not establish that no event occurred" in claim["text"]
        assert result["verification"]["passed"] is True
    finally:
        store.close()
