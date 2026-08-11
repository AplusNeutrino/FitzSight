# FitzSight v0.4 Agent Layer

## Purpose

v0.4 is the first FitzSight release that introduces an **Agent orchestration layer**. The design is intentionally constrained: language-model planning may decide *which approved analytical actions are needed*, but it cannot calculate business metrics, write SQL, invent tables, or bypass evidence registration.

## Architecture

```text
Question
  ↓
Planner
  ├─ ConstrainedRulePlanner (default / no API)
  └─ StructuredJSONPlanner (provider-neutral LLM adapter)
  ↓
Plan Policy Validation
  ↓
DeterministicInvestigationEngine
  ↓
Read-only SQL + Statistics + Contribution + Anomaly tools
  ↓
Evidence Registry
  ↓
EvidenceClaimVerifier
  ↓
Verified FinalAnswer
```

## Planner policy

Current intent:

```text
crm_routing_ftd_investigation
```

Approved action sequence:

1. `inspect_schema`
2. `query_affected_cohort`
3. `query_control_cohort`
4. `statistical_validation`
5. `contribution_decomposition`
6. `anomaly_scan`
7. `event_check`
8. `evidence_boundary`

The model cannot add actions such as `execute_trade`, cannot emit raw SQL, and cannot alter tool parameters.

## Why the planner is constrained

The competition value is not demonstrated by giving an LLM unrestricted database access. FitzSight needs a reproducible and auditable analysis chain. In v0.4:

- LLM/planner output is treated as untrusted input;
- unsupported questions are rejected before model invocation;
- structured planner JSON is validated against an allow-list;
- numeric work remains inside deterministic Python/SQL tools;
- SQL remains read-only;
- benchmark `_gt` fields remain evaluation-only;
- final claims are withheld if the verifier fails.

## Deterministic fallback

`ConstrainedRulePlanner` is a deliberate competition reliability feature. The core demo can operate without network connectivity, API credentials, or model availability.

## Structured LLM adapter

`StructuredJSONPlanner` accepts a callable:

```python
planner = StructuredJSONPlanner(completion_fn)
```

The provider integration is intentionally outside v0.4. A future provider adapter only needs to transform a prompt into JSON text; it still cannot bypass `validate_plan()`.

## Verifier

The verifier checks:

- supported claims have evidence;
- referenced Evidence IDs exist;
- evidence records have successful status;
- evidence payload digests still match;
- evaluation-only `_gt` fields were not used in SQL;
- guarded causal claims actually include a guardrail;
- unqualified causal wording is rejected when the root cause is not confirmed.

The final answer renderer only reuses verified claim text. It does not recalculate or invent metrics.

## Scope limitation

v0.4 remains intentionally narrow and supports the current European FTD / July 15 benchmark intent. Multi-intent planning and a live external model provider are later steps.
