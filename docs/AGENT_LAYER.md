# FitzSight Agent Layer

Version: v0.5.0

## Purpose

The Agent layer converts a supported natural-language financial-operations question into an approved deterministic investigation.

It is deliberately **not** an unrestricted autonomous agent.

## Trust model

Planner output is untrusted.

The local application controls:

- which intents exist;
- which action names exist;
- the exact action order for each intent;
- which deterministic executor handles the question;
- whether final claims pass evidence verification.

## Planner modes

### Deterministic fallback

`ConstrainedRulePlanner`

- default;
- no API/network required;
- competition-safe fallback;
- produces the same approved plan contract.

### Structured JSON adapter

`StructuredJSONPlanner`

- provider neutral;
- accepts JSON text from an external completion function;
- validates exact keys, intent, step list, order and purposes.

### OpenAI Responses planner

`OpenAIResponsesPlanner`

- optional dependency;
- strict JSON-schema output;
- `store=False`;
- local scope classifier runs before provider invocation;
- local `validate_plan` runs after provider output.

## Supported v0.5 intents

### CRM/FTD

`crm_routing_ftd_investigation`

Eight approved actions.

### Net deposits

`net_deposit_anomaly_investigation`

Seven approved actions.

See `docs/MULTI_INTENT.md`.

## Prohibited planner capabilities

The planner may not authorize or construct:

- SQL;
- table names as dynamic tool targets;
- arbitrary filters or free-form tool arguments;
- trades;
- fund transfers;
- account freezes;
- customer outreach;
- investment advice;
- legal/compliance decisions.

## Executor independence

The executor re-classifies the question through the same local intent catalog.

If:

```text
planner intent != executor intent
```

the run fails.

The planner cannot trick the executor into running another workflow.

## Verification

Every `InvestigationResult` goes through `EvidenceClaimVerifier`.

A supported claim must have valid evidence IDs.

The verifier checks:

- evidence existence;
- evidence result digest;
- successful tool status;
- ground-truth-field SQL boundary;
- causal-language guardrail;
- non-empty evidence graph.

If verification fails, `render_verified_answer` returns a withheld result.

## Multi-intent growth policy

Adding an intent requires all of:

1. a deterministic executor;
2. data/tool evidence;
3. test coverage;
4. a benchmark or reproducible scenario;
5. an approved action contract;
6. verifier-compatible claims.

Do not add an intent by prompt engineering alone.
