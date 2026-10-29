"""Request-driven amount stage, not a complete five-claim investigation."""
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.metrics import net_deposit_definitions
from fitzsight.tools.schema import SchemaInspectorTool
from fitzsight.tools.sql import ReadOnlySQLTool
from .inputs import open_net_input_store
from .concentration_claims import ConcentrationBinding, render_concentration, verify_concentration
from .models import Claim
from .net_deposit import NetDepositInvestigationEngine
from .numeric_claims import (
    NetChangeBinding, NetDecompositionBinding, finite_number,
    render_net_change, render_net_decomposition,
    verify_net_change, verify_net_decomposition,
)
from .request import InvestigationRequest


@dataclass(frozen=True)
class NetCashflowResult:
    """Partial result; deliberately not accepted as a full InvestigationResult."""
    request: dict[str, Any]
    snapshot: dict[str, Any]
    metrics: dict[str, Any]
    claims: tuple[Claim, ...]
    evidence: tuple[dict[str, Any], ...]
    scope: str = 'net_cashflow_amounts.v1'

    def to_dict(self):
        return asdict(self)


def execute_net_cashflows(
    request: InvestigationRequest, data_dir: str | Path, *, backend: str,
    top_customers: int | None = None,
) -> NetCashflowResult:
    """Materialize verified inputs, measure approved periods, verify N-C1/N-C2.

    No natural-language routing, model calls, demo generation or root-cause claim.
    Request context is checked separately from mutable evidence metadata.
    """
    if top_customers is not None and (type(top_customers) is not int or top_customers <= 0):
        raise ValueError('top_customers must be a positive integer or None')
    with open_net_input_store(request, data_dir, backend=backend) as session:
        registry = EvidenceRegistry()
        schema = SchemaInspectorTool(session.store, registry)
        engine = NetDepositInvestigationEngine(
            schema_tool=schema, sql_tool=ReadOnlySQLTool(session.store, registry), registry=registry,
        )
        for table, required in (
            ('customers', {'customer_id', 'region', 'assigned_team'}),
            ('deposits', {'customer_id', 'timestamp', 'amount', 'currency', 'status'}),
            ('withdrawals', {'customer_id', 'timestamp', 'amount', 'currency', 'status'}),
        ):
            columns = {c['name'] for c in schema.run(table).data['columns']}
            if missing := sorted(required - columns):
                raise ValueError(f'{table} schema missing required fields: {missing}')
        sources = [engine._money_rows(
            table, region=request.region,
            start=date.fromisoformat(period.start), end=date.fromisoformat(period.end),
        ) for period in (request.baseline, request.current) for table in ('deposits', 'withdrawals')]
        totals = []
        for source in sources:
            values = [r['amount'] for r in source.data['rows']]
            if not all(finite_number(value) for value in values):
                raise ValueError('Cash-flow amounts must be finite numbers')
            totals.append(sum(values))
        bd, bw, cd, cw = totals
        metrics = dict(baseline_net_deposits=bd-bw, current_net_deposits=cd-cw,
                       net_change=(cd-cw)-(bd-bw), deposit_change=cd-bd, withdrawal_change=cw-bw)
        metrics['identity_check'] = metrics['net_change'] - (metrics['deposit_change'] - metrics['withdrawal_change'])
        if not all(finite_number(value) for value in metrics.values()):
            raise ValueError('Cash-flow calculation produced non-finite amounts')
        context = dict(region=request.region, currency=request.currency,
                       baseline_start=request.baseline.start, baseline_end=request.baseline.end,
                       current_start=request.current.start, current_end=request.current.end)
        source_ids = tuple(source.evidence_id for source in sources)
        driver = registry.register('net_deposit_driver_decomposition', {
            **context, 'source_evidence_ids': list(source_ids),
            'metric_definitions': net_deposit_definitions(), 'request': request.to_dict(),
        }, metrics)
        binding = dict(**context, value=metrics['net_change'], evidence_id=driver.evidence_id)
        net = NetChangeBinding(**binding)
        decomposition = NetDecompositionBinding(**binding, deposit_change=metrics['deposit_change'],
                                                 withdrawal_change=metrics['withdrawal_change'])
        claims = (
            Claim('N-C1', render_net_change(net), 'supported', 'high', source_ids + (driver.evidence_id,), numeric_binding=net),
            Claim('N-C2', render_net_decomposition(decomposition), 'supported', 'high', source_ids + (driver.evidence_id,), numeric_binding=decomposition),
        )
        if not (verify_net_change(claims[0], registry, expected_request=request)
                and verify_net_decomposition(claims[1], registry, expected_request=request)):
            raise ValueError('Request-bound cash-flow claim verification failed')
        scope = 'net_cashflow_amounts.v1'
        if top_customers is not None:
            concentration, claim = _concentration(request, registry, sources[3], top_customers)
            metrics = {**metrics, 'customer_concentration': concentration}
            claims += (claim,)
            scope = 'net_cashflow_concentration.v1'
        return NetCashflowResult(request.to_dict(), session.snapshot.to_dict(), metrics,
                                 claims, tuple(registry.to_dicts()), scope=scope)


def _concentration(request, registry, source, top_customers):
    # Reuse the complete, request-filtered current withdrawal rows. No extra CSV/SQL read.
    totals = {}
    for row in source.data['rows']:
        amount, customer = row['amount'], row['customer_id']
        if not finite_number(amount) or amount < 0 or customer is None:
            raise ValueError('Concentration requires nonnegative finite amounts and customer IDs')
        totals[customer] = totals.get(customer, 0.0) + amount
    denominator = sum(totals.values())
    numerator = sum(sorted(totals.values(), reverse=True)[:top_customers])
    if not all(finite_number(v) for v in (numerator, denominator)):
        raise ValueError('Concentration totals must be finite')
    share = numerator / denominator if denominator > 0 else None
    payload = dict(customer_count=top_customers, top_customer_withdrawal_amount=numerator,
                   current_total_withdrawals=denominator, share_of_current_withdrawals=share,
                   calculation_status='computed' if share is not None else 'unavailable',
                   unavailable_reason=None if share is not None else 'nonpositive_total_withdrawals')
    context = dict(region=request.region, currency=request.currency, customer_count=top_customers,
                   period_start=request.current.start,
                   period_end_exclusive=(date.fromisoformat(request.current.end)+timedelta(days=1)).isoformat(),
                   source_evidence_id=source.evidence_id)
    record = registry.register('withdrawal_customer_concentration',
                               {**context, 'request': request.to_dict()}, payload)
    binding = ConcentrationBinding(value=share, numerator=numerator, denominator=denominator,
                                   evidence_id=record.evidence_id, **context)
    claim = Claim('N-C3', render_concentration(binding),
                  'supported' if share is not None else 'insufficient_evidence', 'high',
                  (source.evidence_id, record.evidence_id), numeric_binding=binding)
    if not verify_concentration(claim, registry, expected_request=request, expected_customer_count=top_customers):
        raise ValueError('Request-bound concentration claim verification failed')
    return payload, claim
