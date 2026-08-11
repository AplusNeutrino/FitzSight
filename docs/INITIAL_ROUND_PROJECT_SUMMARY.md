# FitzSight — Initial-Round Project Summary

## Project name

**FitzSight — Financial Operations Intelligence Agent**

Track: **GOAI 2026 · Boundless Agents · AI+金融**

## One-sentence definition

FitzSight is an evidence-grounded financial-operations Agent that turns a manager's business question into a reproducible investigation: it plans a bounded workflow, executes read-only SQL/Python analytical tools, performs statistical or driver analysis, links important findings to evidence IDs, and verifies claims before presenting a decision-support answer.

## Problem

Financial teams already have dashboards, SQL, and BI tools, yet questions such as:

- “Why did FTD conversion deteriorate?”
- “Why did net deposits fall this week?”
- “Which customer segments contribute most to deposit value?”

still require analysts to move manually across multiple tables, comparison periods, statistical tests, and business-event records.

A generic LLM can make this problem worse if it produces a plausible explanation without actually calculating the numbers or preserving an audit trail.

## Target users

- Financial Business Analysts
- Operations Managers
- Sales Managers
- Risk / Management Information analysts using the system for analytical support

FitzSight is **not** an investment adviser, trading system, AML enforcement engine, credit-decision system, or automated compliance decision-maker.

## Core product loop

```text
Question
  ↓
Local intent gate
  ↓
Constrained planner
  ↓
Approved action sequence
  ↓
Read-only SQL / Python tools
  ↓
Statistics / decomposition / segmentation
  ↓
Evidence Registry
  ↓
EvidenceClaimVerifier
  ↓
Verified decision-support answer
```

## Why this is an Agent rather than “chat with CSV”

The system does not send a CSV to a model and ask for an answer. A planner is allowed only to select an approved high-level workflow. Numerical work remains in deterministic tools. Every supported factual claim has traceable Evidence IDs, and the final answer fails closed if verification does not pass.

## Current supported workflows

### 1. CRM / FTD anomaly investigation

Question:

```text
Why did European FTD conversion deteriorate after July 15?
```

FitzSight compares affected and control cohorts, measures response-time change, performs statistical validation, decomposes team contributions, detects response-time anomalies, checks nearby operational events, and applies causal-language guardrails.

Synthetic benchmark:

- affected FTD change: **-7.53 pp**
- European control: **-1.21 pp**
- affected response median: **+29.15 min**
- verification: **PASS**

### 2. Net-deposit anomaly investigation

Question:

```text
Why did European net deposits fall in the week starting August 3?
```

FitzSight measures baseline/current deposits and withdrawals, reconstructs the net-deposit movement, measures top-customer withdrawal concentration, compares Europe with regional controls, and explicitly refuses to infer customer motives.

Synthetic benchmark:

- net-deposit change: **-$223,901.70**
- deposit change: **+$24,365.52**
- withdrawal change: **+$248,267.22**
- top-11 withdrawal share: **92.2%**
- verification: **PASS**

### 3. Customer Intelligence / segmentation

Question:

```text
How are European customer segments distributed by behavioral value, and which segment contributes most to deposits?
```

FitzSight builds observable customer behavior features, applies a transparent deterministic value score, profiles segment deposits/withdrawals/trading behavior, and enforces a boundary against credit/AML/adverse-action use.

Synthetic benchmark:

- customers segmented: **6,770**
- coverage: **100%**
- value groups: **4**
- High Value customer share: **4.1%**
- High Value deposit share: **55.8%**
- verification: **5/5 claims PASS**

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

The v0.6 benchmark catalog contains three independent workflows and measures:

- scenario pass rate;
- root-cause scenario accuracy for anomaly scenarios;
- evidence coverage;
- verifier violations / overclaim failures;
- deterministic end-to-end latency.

Current SQLite build benchmark:

```text
3 / 3 scenarios PASS
scenario pass rate:       100%
root-cause scenario acc.: 100%
mean evidence coverage:   100%
verifier violations:      0
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
What are we not justified in claiming?
```
