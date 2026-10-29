"""Explicit event lookup configuration for the request-driven net-deposit path.

This is a query contract, not an event claim or causal explanation. The legacy
fixed-scenario executor remains unchanged until request-bound verification lands.
"""
from dataclasses import dataclass
from datetime import date, timedelta

from .request import InvestigationRequest, Period


@dataclass(frozen=True)
class EventSelection:
    event_type: str
    period: Period

    def __post_init__(self):
        if type(self.event_type) is not str or self.event_type != 'HIGH_VALUE_WITHDRAWAL_CLUSTER':
            raise ValueError('Unsupported event type')
        if type(self.period) is not Period:
            raise ValueError('Expected validated event Period')

    @classmethod
    def from_dict(cls, value):
        if type(value) is not dict or set(value) != {'event_type', 'period'}:
            raise ValueError('Event selection requires exactly event_type and period')
        return cls(value['event_type'], Period.from_dict(value['period']))

    def to_dict(self):
        return dict(event_type=self.event_type,
                    period=dict(start=self.period.start, end=self.period.end))


def event_lookup_query(request: InvestigationRequest, selection: EventSelection):
    """Return approved SQL and bound values; no I/O or implicit scenario defaults.

    Dates use the request's source_naive convention, including the entire final
    calendar day. The event window is explicit and independent of cashflow periods.
    A caller must retain the original request AND selection for later verification.
    """
    if type(request) is not InvestigationRequest or type(selection) is not EventSelection:
        raise ValueError('Expected validated request and event selection')
    end = (date.fromisoformat(selection.period.end) + timedelta(days=1)).isoformat()
    sql = ('SELECT event_id, date, event_type, region, affected_team, description '
           'FROM business_events WHERE region = ? AND event_type = ? '
           'AND date >= ? AND date < ? ORDER BY date, event_id')
    return sql, (request.region, selection.event_type, selection.period.start, end)
