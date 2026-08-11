from fitzsight.data.generator import GeneratorConfig, generate_all
from fitzsight.data.scenarios import NET_DEPOSIT_SCENARIO


def _period_sum(df, customers, start, end):
    joined = df.merge(customers[["customer_id", "region"]], on="customer_id")
    mask = (
        joined["region"].eq(NET_DEPOSIT_SCENARIO.region)
        & (joined["timestamp"].dt.date >= start)
        & (joined["timestamp"].dt.date <= end)
    )
    return float(joined.loc[mask, "amount"].sum())


def test_injected_net_deposit_scenario_creates_detectable_european_weekly_decline():
    tables = generate_all(
        GeneratorConfig(seed=20260811, n_customers=20_000, n_salespeople=50)
    )
    customers = tables["customers"]
    deposits = tables["deposits"]
    withdrawals = tables["withdrawals"]
    s = NET_DEPOSIT_SCENARIO

    baseline_dep = _period_sum(
        deposits, customers, s.baseline_start, s.baseline_end
    )
    baseline_wd = _period_sum(
        withdrawals, customers, s.baseline_start, s.baseline_end
    )
    current_dep = _period_sum(
        deposits, customers, s.current_start, s.current_end
    )
    current_wd = _period_sum(
        withdrawals, customers, s.current_start, s.current_end
    )

    baseline_net = baseline_dep - baseline_wd
    current_net = current_dep - current_wd

    assert current_net < baseline_net
    assert current_wd > baseline_wd
    assert (baseline_net - current_net) > 100_000
