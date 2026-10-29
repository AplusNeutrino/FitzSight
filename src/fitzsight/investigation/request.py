"""Validated request contract; executor integration is intentionally pending."""
from dataclasses import dataclass
from datetime import date
import re


def _day(value):
    if type(value) is not str or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError('Expected ISO calendar date YYYY-MM-DD')
    return date.fromisoformat(value)


@dataclass(frozen=True)
class Period:
    start: str
    end: str

    def __post_init__(self):
        if _day(self.start) > _day(self.end) or self.end == '9999-12-31':
            raise ValueError('Invalid inclusive period bounds')

    @classmethod
    def from_dict(cls, value):
        if type(value) is not dict or set(value) != {'start', 'end'}:
            raise ValueError('Period requires exactly start and end')
        return cls(**value)


@dataclass(frozen=True)
class InvestigationRequest:
    metric: str
    region: str
    baseline: Period
    current: Period
    timezone: str
    currency: str
    data_snapshot: str

    def __post_init__(self):
        if self.metric != 'net_deposits.v1' or type(self.metric) is not str:
            raise ValueError('Only net_deposits.v1 is supported by this contract')
        if type(self.region) is not str or self.region not in ('Europe', 'Asia', 'Americas'):
            raise ValueError('Unsupported region')
        if type(self.baseline) is not Period or type(self.current) is not Period:
            raise ValueError('Expected validated Period objects')
        if self.baseline.end >= self.current.start:
            raise ValueError('Baseline must end before current period starts')
        if self.timezone != 'source_naive' or type(self.timezone) is not str:
            raise ValueError('Timezone conversion is not implemented; use source_naive')
        if self.currency != 'USD' or type(self.currency) is not str:
            raise ValueError('Only USD is supported; no FX conversion')
        if type(self.data_snapshot) is not str or not re.fullmatch(r'sha256:[0-9a-f]{64}', self.data_snapshot):
            raise ValueError('Expected explicit sha256 snapshot identifier')

    @classmethod
    def from_dict(cls, value):
        fields = {'metric', 'filters', 'baseline', 'current', 'timezone', 'currency', 'data_snapshot'}
        if type(value) is not dict or set(value) != fields:
            raise ValueError('Request fields must exactly match the contract')
        filters = value['filters']
        if type(filters) is not dict or set(filters) != {'region'}:
            raise ValueError('Only the region filter is supported')
        return cls(value['metric'], filters['region'], Period.from_dict(value['baseline']),
                   Period.from_dict(value['current']), value['timezone'], value['currency'], value['data_snapshot'])

    def to_dict(self):
        return dict(metric=self.metric, filters={'region': self.region},
                    baseline={'start': self.baseline.start, 'end': self.baseline.end},
                    current={'start': self.current.start, 'end': self.current.end},
                    timezone=self.timezone, currency=self.currency, data_snapshot=self.data_snapshot)
