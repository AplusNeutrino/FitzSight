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
        return ("A simulated CRM routing change increases lead-assignment latency for "
                "European Team A and Team B, reducing FTD conversion probability.")

CRM_ROUTING_SCENARIO = CrmRoutingScenario()
