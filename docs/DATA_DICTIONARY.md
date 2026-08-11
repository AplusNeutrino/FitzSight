# Data Dictionary

All data is synthetic.

## Tables

### `salespeople`
Synthetic salesperson, team, region, tenure.

### `customers`
Synthetic customer registration, region, acquisition channel, salesperson/team assignment, and a hidden ground-truth value segment.

### `sales_activity`
Lead-level response time, contacted/qualified flags, FTD conversion, and the hidden benchmark flag `affected_by_crm_change_gt`.

### `deposits`
Completed synthetic deposits.

### `withdrawals`
Completed synthetic withdrawals.

### `trades`
Synthetic trading-volume activity. `pnl_mock` exists only for data richness and must not be treated as investment advice.

### `business_events`
Synthetic operating events used for root-cause benchmarks.

## Ground-truth event

`EVT_CRM_ROUTING_20260715`

```text
routing latency ↑
→ response time ↑
→ FTD conversion probability ↓
```

## Benchmark isolation rule

Future Agent code must not read fields ending in `_gt` during normal investigation. They are for offline evaluation only.

## v0.5 net-deposit benchmark

The generator now includes a second deterministic synthetic benchmark.

Event:

```text
EVT_EU_HIGH_VALUE_WITHDRAWAL_20260805
```

Window:

```text
baseline: 2026-07-27 → 2026-08-02
current:  2026-08-03 → 2026-08-09
```

A deterministic set of 11 European customers with the largest cumulative synthetic deposits receives an additional withdrawal during the current window.

The normal Agent does not receive a special per-withdrawal ground-truth flag. It must detect the driver using normal `withdrawals + customers` queries.

The `business_events` table contains a synthetic `HIGH_VALUE_WITHDRAWAL_CLUSTER` event to support event-log correlation, but the Agent must still avoid inferring why individual customers withdrew.

