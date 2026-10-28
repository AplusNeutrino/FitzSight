"""Definitions of the existing cash-flow implementation, including its limits.

The catalog describes the current row-sum contract. Declared source keys are not
an assertion that the import pipeline enforces uniqueness or deduplicates rows.
Changing a formula or data policy requires a new version and executor tests.
"""
from dataclasses import asdict, dataclass, replace
import json
from types import MappingProxyType
from typing import Any


@dataclass(frozen=True)
class MetricDefinition:
    metric_id: str
    version: str
    numerator: str
    denominator: str | None
    components: tuple[str, ...]
    source_keys: tuple[tuple[str, str], ...]
    deduplication_policy: str
    time_fields: tuple[tuple[str, str], ...]
    window_semantics: str
    timezone_policy: str
    status_filter: tuple[str, ...]
    region_attribution: str
    unit: str
    currency: str
    limitations: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return an independent JSON-compatible snapshot (no mutable aliases)."""
        return json.loads(json.dumps(asdict(self), ensure_ascii=False))


_NET = MetricDefinition(
    metric_id='net_deposits.v1',
    version='1',
    numerator='sum(deposits.amount) - sum(withdrawals.amount)',
    denominator=None,
    components=('deposits', 'withdrawals'),
    source_keys=(('deposits', 'deposit_id'), ('withdrawals', 'withdrawal_id')),
    deduplication_policy='none: sum joined rows; source-key uniqueness is not enforced',
    time_fields=(('deposits', 'timestamp'), ('withdrawals', 'timestamp')),
    window_semantics='start day inclusive; day after end day exclusive',
    timezone_policy='naive source timestamps; no timezone conversion',
    status_filter=('completed',),
    region_attribution='current customers.region via inner join on customer_id',
    unit='currency_amount',
    currency='USD',
    limitations=(
        'Cash flow is not investment profit, balance, or liquidity.',
        'Internal transfers are not separately identified by the current schema.',
        'No FX conversion; selected non-USD flows must be rejected.',
        'No historical customer snapshot or customer-key uniqueness enforcement.',
        'Floating-point sums; fixed-point money and import quality gates remain pending.',
        'SQL execution, completeness and row limits remain upstream trust boundaries.',
    ),
)
_CHANGE = replace(
    _NET, metric_id='net_deposit_change.v1',
    numerator='current.net_deposits - baseline.net_deposits',
    components=('net_deposits.v1',),
)
_DECOMPOSITION = replace(
    _NET, metric_id='net_deposit_decomposition.v1',
    numerator='(current.deposits - baseline.deposits) - (current.withdrawals - baseline.withdrawals)',
    components=('deposit_change', 'withdrawal_change'),
)
_CATALOG = MappingProxyType({m.metric_id: m for m in (_NET, _CHANGE, _DECOMPOSITION)})
NET_DEPOSIT_METRIC_IDS = tuple(_CATALOG)


def get_metric(metric_id: str) -> MetricDefinition:
    """Only exact, versioned catalog IDs are accepted; never choose a fallback."""
    if type(metric_id) is not str or metric_id not in _CATALOG:
        raise ValueError('Unsupported versioned metric ID')
    return _CATALOG[metric_id]


def net_deposit_definitions() -> list[dict[str, Any]]:
    return [get_metric(metric_id).to_dict() for metric_id in NET_DEPOSIT_METRIC_IDS]
