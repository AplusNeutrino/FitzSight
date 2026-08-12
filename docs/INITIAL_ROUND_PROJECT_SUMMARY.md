# FitzSight — Initial-Round Project Summary

## Project name

**FitzSight — Financial Operations Intelligence Agent**

Track: **GOAI 2026 · Boundless Agents · AI+金融**

## One-sentence definition

FitzSight is an evidence-grounded financial-operations Agent for **Brokerage / FinTech Operations Analysts**. It turns an operational question into a reproducible investigation: it plans inside a bounded action catalog, executes read-only SQL/Python analytical tools, lets observed tool results control the next approved drilldown, links important findings to Evidence IDs and synthetic source-paragraph evidence, then verifies claims before presenting decision support to a human operator.

## Problem

Financial teams already have dashboards, SQL, and BI tools, yet “why did this KPI change?” still requires analysts to move manually across multiple tables, comparison periods, statistical tests, contribution analysis, customer segments, and business-event records.

A generic LLM can produce an explanation quickly, but a plausible explanation is not the same as a reproducible, auditable investigation.

## Target users

**Primary:** Brokerage / FinTech Operations Analyst  
**Secondary:** Regional Operations Manager / Sales Operations Manager

The initial beachhead chain is:

```text
acquisition → FTD conversion → client-fund flows
```

Risk / Management Information teams may consume the evidence-linked analytical output, but the current PoC is not positioned as an autonomous risk/compliance decision engine.

FitzSight is **not** an investment adviser, trading system, AML enforcement engine, credit-decision system, or automated compliance decision-maker.

## Core product loop

```text
Question
  ↓
Local approved-intent gate
  ↓
Constrained planner
  ↓
Approved action graph / sequence
  ↓
Read-only SQL / Python tools
  ↓
Statistics / decomposition / segmentation / falsification
  ↓
Evidence Registry
  ↓
EvidenceClaimVerifier
  ↓
Verified decision-support answer
  ↓
Authorized human decision
```

## Why this is an Agent rather than “chat with CSV”

The system does not send a CSV to a model and ask for an answer. A planner is allowed only to select an approved high-level workflow. In the CRM/FTD hero, deterministic tool results can select the next action only from the pre-approved branch catalog. Numerical work remains in deterministic tools. Every supported factual claim has traceable Evidence IDs, and the final answer fails closed if verification does not pass.

> **Autonomous investigation. Human decision.**

## Current supported workflows

### 1. Hero — CRM / FTD anomaly investigation

```text
Why did European FTD conversion deteriorate after July 15?
```

Synthetic benchmark:

- affected FTD change: **-7.53 pp**
- European control: **-1.21 pp**
- affected response median: **+29.15 min**
- verification: **PASS**

The v0.12 hero adds bounded conditional latency/event drilldown, stable document source `CRM-CHANGE-2026-0715#p1`, a fail-closed event-tool failure branch, and approved evidence-only follow-up questions.

### 2. Net-deposit anomaly investigation

```text
Why did European net deposits fall in the week starting August 3?
```

Synthetic benchmark:

- net-deposit change: **-$187,790.90**
- deposit change: **+$59,158.18**
- withdrawal change: **+$246,949.08**
- top-11 withdrawal share: **91.6%**
- verification: **PASS**

### 3. Customer Intelligence / segmentation

```text
How are European customer segments distributed by behavioral value,
and which segment contributes most to deposits?
```

Synthetic benchmark:

- customers segmented: **6,770**
- coverage: **100%**
- High Value customer share: **3.7%**
- High Value deposit share: **53.7%**
- verification: **5/5 PASS**

### 4. Marketing lead-quality investigation

```text
Why did Americas lead volume rise while FTD conversion fell after June 15?
```

Synthetic benchmark:

- lead-volume change: **+838 / +315.0%**
- aggregate FTD change: **-10.84 pp**
- Paid Search mix change: **+60.52 pp**
- Paid Search FTD change: **-16.44 pp**
- Paid Search p-value: **4.43e-05**
- verification: **4/4 PASS**

This workflow separates **volume**, **mix**, and **within-channel performance** rather than equating more leads with better commercial performance.

### 5. False-correlation guardrail investigation

```text
Why did Asia FTD conversion fall after July 20,
and is the nearby office relocation the cause?
```

Synthetic benchmark:

- Asia FTD change: **-8.13 pp**
- Affiliate FTD change: **-15.81 pp**
- Affiliate p-value: **0.00463**
- top negative within-channel performance effect: **Affiliate**
- nearby office-event causal support: **false**
- false correlation rejected: **true**
- verification: **4/4 PASS**

This is a deliberate falsification benchmark: a nearby event exists, but FitzSight must refuse to turn temporal proximity into causal attribution.

## Technical architecture

- Python 3.11+
- DuckDB preferred analytical backend; SQLite fallback for restricted environments
- pandas / NumPy / SciPy
- deterministic analytical Tool Layer
- append-only Evidence Registry
- constrained planner contract
- optional OpenAI Responses structured planner
- Streamlit demo UI

Planner/model output is untrusted. It cannot generate SQL, arbitrary table access, free-form tool arguments, trades, transfers, account freezes, or customer-contact actions.

## Evaluation

The v0.7 benchmark catalog contains **five** independent workflows.

```text
5 / 5 scenarios PASS
scenario pass rate:                    100%
root-cause scenario accuracy:          100%
false-correlation rejection accuracy:  100%
mean evidence coverage:                100%
verifier violations:                   0
```

The adversarial release gate contains eight cases:

```text
8 / 8 PASS
scope refusal accuracy:             100%
planner policy catch rate:          100%
verifier integrity catch rate:      100%
causal-overclaim catch rate:        100%
ground-truth leak catch rate:       100%
false-correlation rejection rate:   100%
```

## Data and compliance

All competition benchmark data is synthetic. No former-employer data, real customer PII, confidential CRM exports, or real trading records are included.

Hidden `*_gt` fields exist only for synthetic benchmark construction/evaluation and are prohibited from normal Agent SQL. The verifier checks this boundary.

## Open-source position

FitzSight is released under the **MIT License**. The repository includes source code, synthetic-data generation, benchmark definitions, tool contracts, tests, documentation, and deterministic fallback execution so the core demo does not depend on a live model provider.

## Key differentiation

**Evidence-grounded autonomous financial-operations investigation.**

Dashboard:

```text
What happened?
```

FitzSight:

```text
What changed?
Where did it change?
Which measurable drivers explain the movement?
What evidence supports each claim?
Which tempting explanations fail the evidence test?
What are we not justified in claiming?
```

## v0.12 robustness and architecture evidence

The fixed five-scenario benchmark remains the deterministic showcase/release regression set. v0.12 adds two complementary evaluations:

- **Holdout seeds + question paraphrases:** 8 runs, 100% routing stability, 100% verifier pass, 100% evidence coverage, 100% false-correlation refusal correctness; one holdout CRM seed returns `insufficient_evidence`, producing a 75% supported-candidate rate rather than an inflated universal-recovery claim.
- **Controlled no-verifier-gate ablation:** Full FitzSight refuses all four adversarial fixtures and emits no unsafe adversarial answer; the no-verifier-gate ablation emits all four unsafe cases. This is an architecture ablation, not a Generic LLM benchmark.

Evidence: `docs/V0.12_HOLDOUT_RESULTS.json`, `docs/V0.12_ABLATION_RESULTS.json`, `docs/V0.12_EVALUATION.md`.

## Production boundary

Current competition evidence covers synthetic data, bounded planning/execution, read-only deterministic tools, append-only evidence, fail-closed verification, and source-addressable synthetic document evidence. Enterprise SSO/RBAC, row/field authorization, PII masking, tenant isolation, retention and production observability are deployment-blueprint requirements, not current PoC implementation claims. See `docs/ENTERPRISE_DEPLOYMENT_BOUNDARY.md`.
## v0.12.1 competition-asset synchronization

The formal initial-round PPTX/PDF now uses the same current evidence contract as this summary: **one complete CRM/FTD hero investigation + one false-correlation refusal**, with the other three workflows retained as breadth proof. The deck includes runtime-derived hero trace/answer evidence, Evaluation v2 holdout and controlled ablation results, and an explicit implemented-vs-production-blueprint boundary. No slide claims live Streamlit/OpenAI provider validation, portal submission, or production RBAC/PII controls.

