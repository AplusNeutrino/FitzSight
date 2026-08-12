# FitzSight v0.12.0 Release Notes

**Release date:** 2026-08-12  
**Theme:** GOAI alignment, bounded-adaptive CRM hero, source-addressable document evidence, evaluation v2

## What changed

### 1. Competition positioning is now explicit

- Primary persona: **Brokerage / FinTech Operations Analyst**.
- Secondary persona: **Regional Operations Manager / Sales Operations Manager**.
- Beachhead business chain: **acquisition → FTD conversion → client-fund flows**.
- Competition-facing decision boundary: **Autonomous investigation. Human decision.**

### 2. CRM / FTD is now the bounded-adaptive hero workflow

The planner still emits only the approved high-level CRM action catalog. The deterministic executor now records result-driven branch decisions:

```text
contribution/statistical evidence
→ conditional latency anomaly scan
→ conditional operational-event check
→ conditional source-paragraph document evidence
→ evidence boundary
→ verifier
```

Branch decisions are registered as `agent.branch_decision` evidence. The executor does not accept planner-generated SQL, table names, arbitrary tool arguments or high-impact financial actions.

A tested dependency-failure path records the failed event lookup and changes the root-cause status to `insufficient_evidence` instead of fabricating attribution.

### 3. Approved evidence-only follow-up

`FitzSightAgent.answer_follow_up()` supports two bounded CRM/FTD follow-up families using the already verified run only:

- largest negative team contributor;
- evidence behind the CRM routing candidate.

It does not open a new unrestricted SQL/chat path.

### 4. Lightweight synthetic document evidence

`DocumentEvidenceTool` adds three fixed synthetic operational paragraphs with stable source/paragraph IDs. The hero uses:

```text
CRM-CHANGE-2026-0715#p1
```

The tool performs no network access, arbitrary filesystem read or vector retrieval. This is deliberately not presented as production RAG.

### 5. Real hero product-process evidence

Generated from an actual verified deterministic run:

- `docs/V0.12_HERO_RUN.json`
- `submission/FitzSight_Hero_Run_Evidence.html`
- `submission/FitzSight_Hero_Run_Evidence.png`

The process view includes the user question, bounded execution trace, branch rationale, Evidence IDs, verifier status, final answer/guardrail, source-paragraph evidence and approved follow-up.

### 6. Evaluation v2

#### Holdout seed + question-paraphrase robustness

Evidence: `docs/V0.12_HOLDOUT_RESULTS.json`

```text
8 case runs
intent routing stability:                100%
verification pass rate:                  100%
mean evidence coverage:                  100%
false-correlation refusal correctness:   100%
supported-candidate rate:                 75%
```

One unseen CRM seed correctly returned `insufficient_evidence`; the release does not convert that into a 100% root-cause recovery claim.

#### Controlled verifier/evidence-gate ablation

Evidence: `docs/V0.12_ABLATION_RESULTS.json`

```text
Full FitzSight
  adversarial refusal correctness:        100%
  unsafe answer rate on adversarial:        0%
  emitted-output mean evidence coverage:  100%

No-verifier-gate ablation
  adversarial refusal correctness:          0%
  unsafe answer rate on adversarial:       100%
  emitted-output mean evidence coverage:   66.7%
```

This is a controlled architecture ablation, **not** a Generic LLM/live-provider baseline.

### 7. Enterprise boundary documented

`docs/ENTERPRISE_DEPLOYMENT_BOUNDARY.md` now separates implemented PoC controls from planned production requirements such as SSO, RBAC/ABAC, row/field authorization, PII masking, tenant isolation, retention and production observability.

## Validation evidence

The 85 collected tests were executed in non-overlapping groups because a monolithic pytest process can exceed the sandbox command ceiling:

```text
85 tests collected
84 passed
1 skipped
0 failed
compileall: PASS
```

The single skip is the DuckDB-specific build-sandbox integration test. It is **not** treated as a DuckDB runtime PASS in this environment.

Release regressions:

```text
fixed deterministic benchmark: 5 / 5 PASS
root-cause scenario accuracy: 100%
false-correlation rejection: 100%
mean evidence coverage: 100%
verifier violations: 0

adversarial gate: 8 / 8 PASS
scope refusal: 100%
planner policy catch: 100%
verifier integrity catch: 100%
causal overclaim catch: 100%
ground-truth leak catch: 100%
false-correlation rejection: 100%
```

Targeted v0.12 hero/document/planner tests: 18 / 18 PASS before the complete non-overlapping suite run.

## Evidence/status boundaries

### Done in v0.12.0

- persona / beachhead freeze;
- bounded-adaptive CRM/FTD hero + fail-closed dependency branch;
- runtime-derived hero product-process evidence;
- holdout seed/paraphrase evaluation;
- controlled verifier/evidence-gate ablation;
- lightweight source-addressable synthetic document evidence;
- enterprise deployment blueprint;
- decision-support / human-decision language normalization in active source documents.

### In progress / not yet claimed done

- formal PPT/PDF regeneration to the new v0.12 one-hero + one-refusal narrative;
- full competition-asset synchronization dependent on that regenerated deck;
- final GOAI handbook reviewer gate after presentation regeneration.

### Not validated in this build environment

- Streamlit live runtime (UI dependency not installed in this sandbox);
- OpenAI Responses live planner (not requested; no live-provider claim);
- live-provider latency/cost;
- final-presentation-machine **live Streamlit/provider runtime** (local deterministic final-machine core is validated separately below).

### User-manual external actions

No GitHub publish, GOAI portal upload/final submit, Gmail/confirmation-email access or other external account write was performed by this release workflow.

## Final local release readiness

After the v0.12 versioned operator assets were rebuilt, the local release gates were rerun:

```text
submission preflight:             PASS
handoff ready_for_user_takeover:  true
final-machine local_core_ready:   true
deterministic Agent smoke:        verified
```

The manual handoff and final-machine kit were integrity-checked during local build. Their delivery-time hashes are recorded outside the self-contained kit to avoid self-referential/stale checksum claims.

These are local readiness results only. The default final-machine run intentionally did not claim a live Streamlit health-check or OpenAI provider call; those remain separately evidence-gated.
