# FitzSight v0.6 Multi-Intent Contract

FitzSight expands by **approved business intents**, not unrestricted tool autonomy.

## Approved intents

### `crm_routing_ftd_investigation`

Question family: European FTD/conversion deterioration around the synthetic 2026-07-15 CRM routing change.

Required actions:

1. `inspect_schema`
2. `query_affected_cohort`
3. `query_control_cohort`
4. `statistical_validation`
5. `contribution_decomposition`
6. `anomaly_scan`
7. `event_check`
8. `evidence_boundary`

### `net_deposit_anomaly_investigation`

Question family: European weekly net-deposit deterioration around the synthetic 2026-08-03 period.

Required actions:

1. `inspect_schema`
2. `measure_period_net_deposits`
3. `decompose_deposit_withdrawal_drivers`
4. `identify_customer_concentration`
5. `compare_regional_control`
6. `event_check`
7. `evidence_boundary`

### `customer_intelligence_segmentation`

Question family: European customer behavioral-value segmentation and deposit contribution.

Required actions:

1. `inspect_customer_schema`
2. `build_customer_behavior_features`
3. `segment_customer_value`
4. `profile_segment_deposits`
5. `compare_withdrawal_pressure`
6. `evidence_boundary`

## Policy

A planner/model may not:

- invent a fourth intent;
- omit or reorder required actions;
- emit SQL;
- provide arbitrary tool arguments;
- request a trade, transfer, account freeze, customer contact, credit decision, AML conclusion, suitability decision, or investment recommendation.

The local classifier runs before any external model invocation. The local plan validator remains authoritative after model output.
