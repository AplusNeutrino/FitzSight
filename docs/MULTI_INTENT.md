# FitzSight v0.5 Multi-Intent Contract

## Intent catalog

### `crm_routing_ftd_investigation`

Primary question:

```text
Why did European FTD conversion deteriorate after July 15?
```

Approved actions:

1. inspect schema
2. query affected cohort
3. query control cohort
4. statistical validation
5. contribution decomposition
6. anomaly scan
7. event check
8. evidence boundary

### `net_deposit_anomaly_investigation`

Primary question:

```text
Why did European net deposits fall in the week starting August 3?
```

Approved actions:

1. inspect schema
2. measure period net deposits
3. decompose deposit/withdrawal drivers
4. identify customer concentration
5. compare regional control
6. event check
7. evidence boundary

## Critical policy

The planner does not choose arbitrary tools.

The local classifier first decides whether the user question falls into a published supported intent. A model may then produce a structured plan only inside that intent's exact action policy.

The executor independently routes the question to a deterministic engine. Planner and executor intents must match or the Agent fails.

## Second benchmark interpretation

The net-deposit benchmark is designed to test **driver attribution**, not customer-motive inference.

Supported:

- withdrawals increased;
- deposits increased/decreased;
- net deposits changed;
- a small group of customer withdrawals dominates the current withdrawal volume;
- Europe moved more negatively than a regional control statistic;
- a matching operational event exists.

Not supported without additional evidence:

- why a specific customer withdrew;
- fraud/AML conclusions;
- customer creditworthiness;
- investment intent;
- legal or compliance conclusions.
