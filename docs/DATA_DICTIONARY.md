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
