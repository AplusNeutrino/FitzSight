# FitzSight Agent Layer

Version: v0.6.0

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

## Customer Intelligence boundary

The new segmentation workflow is descriptive. The Agent may discuss observed value and withdrawal concentration but cannot turn the segments into credit, AML, suitability, eligibility, customer-contact, restriction, or adverse-action decisions.
