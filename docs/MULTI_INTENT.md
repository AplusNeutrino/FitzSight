# FitzSight v0.7 Multi-Intent Contract

FitzSight expands by **approved business intents**, not unrestricted tool autonomy.

## 1. `crm_routing_ftd_investigation`

Question family: European FTD deterioration around 2026-07-15.

Required actions:

1. `inspect_schema`
2. `query_affected_cohort`
3. `query_control_cohort`
4. `statistical_validation`
5. `contribution_decomposition`
6. `anomaly_scan`
7. `event_check`
8. `evidence_boundary`

## 2. `net_deposit_anomaly_investigation`

Question family: European weekly net-deposit deterioration around 2026-08-03.

Required actions:

1. `inspect_schema`
2. `measure_period_net_deposits`
3. `decompose_deposit_withdrawal_drivers`
4. `identify_customer_concentration`
5. `compare_regional_control`
6. `event_check`
7. `evidence_boundary`

## 3. `customer_intelligence_segmentation`

Question family: European behavioral-value segmentation and deposit contribution.

Required actions:

1. `inspect_customer_schema`
2. `build_customer_behavior_features`
3. `segment_customer_value`
4. `profile_segment_deposits`
5. `compare_withdrawal_pressure`
6. `evidence_boundary`

## 4. `marketing_lead_quality_investigation`

Question family: Americas lead-volume growth with conversion deterioration after 2026-06-15.

Required actions:

1. `inspect_schema`
2. `measure_lead_volume`
3. `measure_conversion`
4. `channel_mix_decomposition`
5. `statistical_validation`
6. `event_check`
7. `evidence_boundary`

## 5. `false_correlation_guardrail_investigation`

Question family: Asia conversion deterioration after 2026-07-20 with a tempting nearby office-relocation event.

Required actions:

1. `inspect_schema`
2. `measure_conversion_shift`
3. `channel_decomposition`
4. `statistical_validation`
5. `nearby_event_check`
6. `falsification_check`
7. `evidence_boundary`

## Policy

A planner/model may not:

- invent a sixth intent;
- omit or reorder required actions;
- emit SQL;
- provide arbitrary tool arguments;
- request a trade, transfer, account freeze, customer contact, credit decision, AML conclusion, suitability decision, or investment recommendation.

The local classifier runs before any external model invocation. The local plan validator remains authoritative after model output.
