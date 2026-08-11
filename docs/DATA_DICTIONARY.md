# Data Dictionary

All data is synthetic.

## Tables

### `salespeople`
Synthetic salesperson, team, region, and tenure.

### `customers`
Synthetic customer registration, region, acquisition channel, salesperson/team assignment, and hidden evaluation fields.

### `sales_activity`
Lead-level response time, contacted/qualified flags, FTD conversion, and hidden benchmark flags.

Observable Agent fields include:

```text
activity_id
customer_id
lead_created_at
region
assigned_salesperson
assigned_team
acquisition_channel
response_time_minutes
contacted
qualified
converted_ftd
```

Evaluation-only fields include:

```text
affected_by_crm_change_gt
affected_by_marketing_shift_gt
affected_by_affiliate_quality_gt
```

### `deposits`
Completed synthetic deposits.

### `withdrawals`
Completed synthetic withdrawals.

### `trades`
Synthetic trading-volume activity. `pnl_mock` exists only for data richness and must not be treated as investment advice.

### `business_events`
Synthetic operating events used for root-cause/falsification benchmarks.

## Benchmark isolation rule

Normal Agent code must not read fields ending in `_gt`. They exist only for synthetic benchmark construction/evaluation. The verifier checks SQL evidence for this boundary.

## Benchmark 1 — CRM routing

```text
EVT_CRM_ROUTING_20260715
routing latency ↑
→ response time ↑
→ FTD conversion probability ↓
```

## Benchmark 2 — Net deposits

```text
EVT_EU_HIGH_VALUE_WITHDRAWAL_20260805
```

Eleven high-value European customers receive additional synthetic withdrawals during 2026-08-03–09. The Agent must identify withdrawal pressure/concentration without inferring motives.

## Benchmark 3 — Customer Intelligence

No new event is injected. The Agent derives transparent `High Value / Growth / Core / Low Activity` segments from observable deposit/trading behavior. `customer_segment_gt` is evaluation-only.

## Benchmark 4 — Americas marketing quality

```text
EVT_AM_PAID_MEDIA_EXPANSION_20260615
```

A deterministic subset of Americas registrations is shifted into the 2026-06-15–28 campaign window and assigned to Paid Search. Paid Search conversion probability is also reduced in that window.

The Agent is expected to distinguish:

- lead-volume growth;
- channel-mix shift;
- within-channel conversion deterioration.

## Benchmark 5 — Asia false correlation

```text
EVT_ASIA_OFFICE_RELOCATION_20260720
```

An office relocation is intentionally placed near an Asia FTD decline but is marked with no expected lead-conversion effect. Affiliate conversion probability deteriorates in the same period.

The Agent should detect the Affiliate-specific pattern and reject the office event as a supported cause.
