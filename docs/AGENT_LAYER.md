# FitzSight Agent Layer

Version: v0.7.0

## Contract

```text
question
→ local intent classification
→ constrained AgentPlan
→ deterministic executor
→ Evidence Registry
→ EvidenceClaimVerifier
→ verified answer / withheld answer
```

Planner/model output is always untrusted.

## Planners

### `ConstrainedRulePlanner`

Reliable no-network fallback. It classifies one of the approved intents and creates the exact allowed action sequence.

### `StructuredJSONPlanner`

Provider-neutral adapter for pre-generated/model JSON. It parses only `intent` and `steps`, then applies the same local plan validator.

### `OpenAIResponsesPlanner`

Optional provider integration. The local classifier fixes the approved intent before API invocation; structured output is still validated locally afterwards.

## Approved intents

- `crm_routing_ftd_investigation`
- `net_deposit_anomaly_investigation`
- `customer_intelligence_segmentation`
- `marketing_lead_quality_investigation`
- `false_correlation_guardrail_investigation`

See `docs/MULTI_INTENT.md` for exact action sequences.

## Verifier

`EvidenceClaimVerifier` checks:

- claim status policy;
- Evidence ID existence;
- evidence digest integrity;
- tool success status;
- guardrail presence when required;
- causal overclaim wording;
- evaluation-only `*_gt` leakage;
- non-empty claim-to-evidence graph.

If any verification condition fails, the final renderer fails closed.

## v0.7 falsification boundary

The false-correlation workflow deliberately separates:

```text
nearby event exists
```

from:

```text
data support that event as a cause
```

A nearby event is not promoted to a causal explanation merely because it occurs near the KPI change.

## Customer Intelligence boundary

Segmentation remains descriptive. The Agent may discuss observed value and withdrawal concentration but cannot turn the segments into credit, AML, suitability, eligibility, customer-contact, restriction, or adverse-action decisions.
