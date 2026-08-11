from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class CrmRoutingScenario:
    event_id: str = "EVT_CRM_ROUTING_20260715"
    event_type: str = "CRM_ROUTING_CHANGE"
    change_date: date = date(2026, 7, 15)
    region: str = "Europe"
    affected_teams: tuple[str, ...] = ("Team A", "Team B")
    response_time_multiplier: float = 1.35
    conversion_probability_multiplier: float = 0.72

    @property
    def description(self) -> str:
        return (
            "A simulated CRM routing change increases lead-assignment latency for "
            "European Team A and Team B, reducing FTD conversion probability."
        )


@dataclass(frozen=True)
class NetDepositShockScenario:
    """Second synthetic benchmark: a concentrated high-value withdrawal shock.

    The benchmark is intentionally designed as an *observed financial-operations
    driver*, not a claim about why the customers withdrew. FitzSight should be
    able to decompose the net-deposit movement and identify the concentration
    without inventing customer motives.
    """

    event_id: str = "EVT_EU_HIGH_VALUE_WITHDRAWAL_20260805"
    event_type: str = "HIGH_VALUE_WITHDRAWAL_CLUSTER"
    event_date: date = date(2026, 8, 5)
    region: str = "Europe"
    baseline_start: date = date(2026, 7, 27)
    baseline_end: date = date(2026, 8, 2)
    current_start: date = date(2026, 8, 3)
    current_end: date = date(2026, 8, 9)
    customer_count: int = 11
    withdrawal_fraction_of_lifetime_deposits: float = 0.72

    @property
    def description(self) -> str:
        return (
            "A synthetic cluster of high-value European customer withdrawals is "
            "recorded during the week of 2026-08-03. The benchmark tests whether "
            "FitzSight can identify withdrawal pressure and customer concentration "
            "as observed drivers of a net-deposit decline."
        )


CRM_ROUTING_SCENARIO = CrmRoutingScenario()
NET_DEPOSIT_SCENARIO = NetDepositShockScenario()
