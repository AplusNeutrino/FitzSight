from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .scenarios import CRM_ROUTING_SCENARIO, NET_DEPOSIT_SCENARIO


REGIONS = ("Europe", "Asia", "Middle East", "Americas", "Oceania")
CHANNELS = ("Organic", "Paid Search", "Referral", "Affiliate", "Events")
TEAMS = ("Team A", "Team B", "Team C", "Team D", "Team E")


@dataclass(frozen=True)
class GeneratorConfig:
    seed: int = 20260811
    n_customers: int = 20_000
    n_salespeople: int = 50
    start_date: str = "2026-01-01"
    end_date: str = "2026-08-10"


def _dates(rng, n, start, end):
    days = (end.normalize() - start.normalize()).days
    return (
        start
        + pd.to_timedelta(rng.integers(0, days + 1, n), unit="D")
        + pd.to_timedelta(rng.integers(0, 86400, n), unit="s")
    )


def generate_salespeople(cfg, rng):
    ids = [f"SP{i:03d}" for i in range(1, cfg.n_salespeople + 1)]
    combinations = [(team, region) for region in REGIONS for team in TEAMS]
    repeated = [combinations[i % len(combinations)] for i in range(cfg.n_salespeople)]
    teams = np.array([x[0] for x in repeated])
    regions = np.array([x[1] for x in repeated])
    return pd.DataFrame(
        {
            "salesperson_id": ids,
            "team_id": teams,
            "region": regions,
            "tenure_months": rng.integers(2, 61, cfg.n_salespeople),
        }
    )


def generate_customers(cfg, rng, sp):
    reg_dates = _dates(
        rng, cfg.n_customers, pd.Timestamp(cfg.start_date), pd.Timestamp(cfg.end_date)
    )
    regions = rng.choice(REGIONS, cfg.n_customers, p=[0.34, 0.20, 0.16, 0.20, 0.10])
    channels = rng.choice(
        CHANNELS, cfg.n_customers, p=[0.28, 0.24, 0.18, 0.20, 0.10]
    )
    assigned, teams = [], []
    for region in regions:
        pool = sp[sp.region == region]
        row = (
            pool.iloc[int(rng.integers(0, len(pool)))]
            if len(pool)
            else sp.iloc[int(rng.integers(0, len(sp)))]
        )
        assigned.append(row.salesperson_id)
        teams.append(row.team_id)

    value = rng.lognormal(7.3, 0.9, cfg.n_customers)
    segment = pd.cut(
        value,
        [-np.inf, 900, 1800, 4000, np.inf],
        labels=["Low", "Core", "Growth", "High Value"],
    ).astype(str)

    return pd.DataFrame(
        {
            "customer_id": [f"C{i:06d}" for i in range(1, cfg.n_customers + 1)],
            "registration_date": reg_dates,
            "region": regions,
            "country": [f"{r} Market" for r in regions],
            "acquisition_channel": channels,
            "assigned_salesperson": assigned,
            "assigned_team": teams,
            "customer_segment_gt": segment,
        }
    )


def generate_sales_activity(cfg, rng, customers):
    scenario = CRM_ROUTING_SCENARIO
    data = customers[
        [
            "customer_id",
            "registration_date",
            "region",
            "assigned_salesperson",
            "assigned_team",
            "acquisition_channel",
        ]
    ].copy()
    data["lead_created_at"] = data.registration_date

    response = rng.lognormal(np.log(95), 0.55, len(data))
    affected = (
        data.region.eq(scenario.region)
        & data.assigned_team.isin(scenario.affected_teams)
        & (data.registration_date.dt.date >= scenario.change_date)
    )
    response[affected.to_numpy()] *= scenario.response_time_multiplier
    data["response_time_minutes"] = np.round(response, 1)

    bonus = data.acquisition_channel.map(
        {
            "Organic": 0.03,
            "Paid Search": -0.02,
            "Referral": 0.06,
            "Affiliate": -0.01,
            "Events": 0.02,
        }
    ).to_numpy()
    penalty = np.clip((data.response_time_minutes.to_numpy() - 90) / 900, -0.02, 0.18)
    probability = np.clip(0.24 + bonus - penalty, 0.04, 0.48)
    probability[affected.to_numpy()] *= scenario.conversion_probability_multiplier

    data["converted_ftd"] = rng.random(len(data)) < probability
    data["contacted"] = rng.random(len(data)) < np.clip(
        0.93 - data.response_time_minutes.to_numpy() / 1500, 0.65, 0.95
    )
    data["qualified"] = data.contacted & (rng.random(len(data)) < 0.58)
    data["affected_by_crm_change_gt"] = affected
    data["activity_id"] = [f"A{i:06d}" for i in range(1, len(data) + 1)]

    return data[
        [
            "activity_id",
            "customer_id",
            "lead_created_at",
            "region",
            "assigned_salesperson",
            "assigned_team",
            "acquisition_channel",
            "response_time_minutes",
            "contacted",
            "qualified",
            "converted_ftd",
            "affected_by_crm_change_gt",
        ]
    ]


def generate_deposits(cfg, rng, customers, activity):
    joined = customers[
        ["customer_id", "registration_date", "customer_segment_gt"]
    ].merge(activity[["customer_id", "converted_ftd"]], on="customer_id")

    scale = {"Low": 250.0, "Core": 650.0, "Growth": 1500.0, "High Value": 5000.0}
    rows = []
    deposit_id = 1

    for row in joined[joined.converted_ftd].itertuples(index=False):
        for _ in range(int(rng.integers(1, 5))):
            timestamp = pd.Timestamp(row.registration_date) + pd.Timedelta(
                days=int(rng.integers(0, 75))
            )
            if timestamp > pd.Timestamp(cfg.end_date) + pd.Timedelta(days=1):
                continue
            rows.append(
                {
                    "deposit_id": f"D{deposit_id:07d}",
                    "customer_id": row.customer_id,
                    "timestamp": timestamp,
                    "amount": round(
                        float(
                            rng.lognormal(
                                np.log(scale[str(row.customer_segment_gt)]), 0.55
                            )
                        ),
                        2,
                    ),
                    "currency": "USD",
                    "method": rng.choice(
                        ["Card", "Bank Transfer", "E-wallet"],
                        p=[0.45, 0.35, 0.20],
                    ),
                    "status": "completed",
                }
            )
            deposit_id += 1

    return pd.DataFrame(rows)


def _inject_net_deposit_shock(cfg, customers, deposits, rows, next_id):
    """Inject the second benchmark without exposing an evaluation flag to the Agent.

    Selection is deterministic from synthetic data: the European customers with
    the largest historical completed deposits receive an additional withdrawal
    during the current benchmark week.
    """

    scenario = NET_DEPOSIT_SCENARIO
    if deposits.empty:
        return next_id

    european_ids = set(
        customers.loc[customers.region.eq(scenario.region), "customer_id"].astype(str)
    )
    totals = (
        deposits[deposits.customer_id.astype(str).isin(european_ids)]
        .groupby("customer_id", as_index=False)["amount"]
        .sum()
        .sort_values(["amount", "customer_id"], ascending=[False, True])
        .head(scenario.customer_count)
    )

    for rank, row in enumerate(totals.itertuples(index=False)):
        # Keep injected withdrawals below the customer's cumulative synthetic
        # deposits while making the weekly shock clearly measurable.
        amount = float(row.amount) * scenario.withdrawal_fraction_of_lifetime_deposits
        timestamp = pd.Timestamp(scenario.event_date) + pd.Timedelta(
            hours=9 + rank, minutes=(rank * 7) % 60
        )
        rows.append(
            {
                "withdrawal_id": f"W{next_id:07d}",
                "customer_id": row.customer_id,
                "timestamp": timestamp,
                "amount": round(amount, 2),
                "currency": "USD",
                "status": "completed",
            }
        )
        next_id += 1

    return next_id


def generate_withdrawals(cfg, rng, customers, deposits):
    columns = [
        "withdrawal_id",
        "customer_id",
        "timestamp",
        "amount",
        "currency",
        "status",
    ]
    if deposits.empty:
        return pd.DataFrame(columns=columns)

    totals = deposits.groupby("customer_id", as_index=False).amount.sum()
    rows = []
    withdrawal_id = 1
    max_day = (pd.Timestamp(cfg.end_date) - pd.Timestamp(cfg.start_date)).days

    for row in totals.itertuples(index=False):
        if rng.random() > 0.48:
            continue
        for _ in range(int(rng.integers(1, 3))):
            rows.append(
                {
                    "withdrawal_id": f"W{withdrawal_id:07d}",
                    "customer_id": row.customer_id,
                    "timestamp": pd.Timestamp(cfg.start_date)
                    + pd.Timedelta(days=int(rng.integers(30, max_day + 1))),
                    "amount": round(float(row.amount * rng.uniform(0.05, 0.35)), 2),
                    "currency": "USD",
                    "status": "completed",
                }
            )
            withdrawal_id += 1

    _inject_net_deposit_shock(
        cfg, customers, deposits, rows, withdrawal_id
    )
    return pd.DataFrame(rows, columns=columns)


def generate_trades(cfg, rng, customers, activity):
    joined = activity[activity.converted_ftd][["customer_id"]].merge(
        customers[["customer_id", "registration_date", "customer_segment_gt"]],
        on="customer_id",
    )
    scale = {"Low": 0.8, "Core": 1.5, "Growth": 3.0, "High Value": 7.0}
    rows = []
    trade_id = 1

    for row in joined.itertuples(index=False):
        for _ in range(int(rng.integers(1, 12))):
            timestamp = pd.Timestamp(row.registration_date) + pd.Timedelta(
                days=int(rng.integers(1, 100))
            )
            if timestamp > pd.Timestamp(cfg.end_date) + pd.Timedelta(days=1):
                continue
            volume = float(
                rng.lognormal(np.log(scale[str(row.customer_segment_gt)]), 0.7)
            )
            rows.append(
                {
                    "trade_id": f"T{trade_id:08d}",
                    "customer_id": row.customer_id,
                    "timestamp": timestamp,
                    "instrument_group": rng.choice(
                        ["FX", "Index", "Commodity", "Crypto CFD"]
                    ),
                    "volume": round(volume, 4),
                    "pnl_mock": round(float(rng.normal(0, 75 * volume)), 2),
                }
            )
            trade_id += 1

    return pd.DataFrame(rows)


def generate_business_events():
    crm = CRM_ROUTING_SCENARIO
    net = NET_DEPOSIT_SCENARIO
    return pd.DataFrame(
        [
            {
                "event_id": crm.event_id,
                "date": pd.Timestamp(crm.change_date),
                "event_type": crm.event_type,
                "region": crm.region,
                "affected_team": ",".join(crm.affected_teams),
                "description": crm.description,
                "expected_effect": "response_time_up;ftd_conversion_down",
                "ground_truth_tag": "root_cause",
            },
            {
                "event_id": "EVT_EU_CAMPAIGN_20260620",
                "date": pd.Timestamp("2026-06-20"),
                "event_type": "MARKETING_CAMPAIGN",
                "region": "Europe",
                "affected_team": "All",
                "description": "Benign campaign increases lead volume.",
                "expected_effect": "lead_volume_up",
                "ground_truth_tag": "background_event",
            },
            {
                "event_id": net.event_id,
                "date": pd.Timestamp(net.event_date),
                "event_type": net.event_type,
                "region": net.region,
                "affected_team": "All",
                "description": net.description,
                "expected_effect": "withdrawals_up;net_deposit_down;customer_concentration_up",
                "ground_truth_tag": "observed_driver",
            },
        ]
    )


def generate_all(cfg=None):
    cfg = cfg or GeneratorConfig()
    rng = np.random.default_rng(cfg.seed)
    salespeople = generate_salespeople(cfg, rng)
    customers = generate_customers(cfg, rng, salespeople)
    activity = generate_sales_activity(cfg, rng, customers)
    deposits = generate_deposits(cfg, rng, customers, activity)
    withdrawals = generate_withdrawals(cfg, rng, customers, deposits)
    trades = generate_trades(cfg, rng, customers, activity)

    return {
        "salespeople": salespeople,
        "customers": customers,
        "sales_activity": activity,
        "deposits": deposits,
        "withdrawals": withdrawals,
        "trades": trades,
        "business_events": generate_business_events(),
    }


def write_csv_bundle(output_dir, cfg=None):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, dataframe in generate_all(cfg).items():
        path = output / f"{name}.csv"
        dataframe.to_csv(path, index=False)
        paths[name] = path
    return paths
