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
    """Synthetic benchmark: concentrated high-value withdrawal pressure."""

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


@dataclass(frozen=True)
class MarketingLeadQualityScenario:
    """Synthetic benchmark: more Americas leads but lower acquisition quality."""

    event_id: str = "EVT_AM_PAID_MEDIA_EXPANSION_20260615"
    event_type: str = "PAID_MEDIA_EXPANSION"
    event_date: date = date(2026, 6, 15)
    region: str = "Americas"
    acquisition_channel: str = "Paid Search"
    baseline_start: date = date(2026, 6, 1)
    baseline_end: date = date(2026, 6, 14)
    current_start: date = date(2026, 6, 15)
    current_end: date = date(2026, 6, 28)
    reassigned_leads: int = 850
    conversion_probability_multiplier: float = 0.48

    @property
    def description(self) -> str:
        return (
            "A synthetic paid-media expansion increases Americas Paid Search lead volume "
            "during 2026-06-15 to 2026-06-28, while the incoming cohort has materially "
            "lower FTD conversion quality."
        )


@dataclass(frozen=True)
class FalseCorrelationScenario:
    """Synthetic benchmark designed to punish post-hoc event attribution.

    An unrelated office relocation appears near an Asia conversion deterioration.
    The measurable deterioration is concentrated in Affiliate leads; FitzSight should
    surface that observed driver and explicitly withhold causal attribution to the
    nearby office event.
    """

    event_id: str = "EVT_ASIA_OFFICE_RELOCATION_20260720"
    event_type: str = "OFFICE_RELOCATION"
    event_date: date = date(2026, 7, 20)
    region: str = "Asia"
    driver_channel: str = "Affiliate"
    baseline_start: date = date(2026, 7, 6)
    baseline_end: date = date(2026, 7, 19)
    current_start: date = date(2026, 7, 20)
    current_end: date = date(2026, 8, 2)
    conversion_probability_multiplier: float = 0.38

    @property
    def description(self) -> str:
        return (
            "A synthetic Asia office relocation is logged on 2026-07-20 but is not "
            "configured to affect lead conversion. In the same period, Affiliate lead "
            "conversion quality deteriorates. The benchmark tests whether FitzSight "
            "rejects a nearby-but-unrelated event as a causal explanation."
        )


CRM_ROUTING_SCENARIO = CrmRoutingScenario()
NET_DEPOSIT_SCENARIO = NetDepositShockScenario()
MARKETING_LEAD_QUALITY_SCENARIO = MarketingLeadQualityScenario()
FALSE_CORRELATION_SCENARIO = FalseCorrelationScenario()
