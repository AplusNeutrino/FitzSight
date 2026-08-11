# FitzSight — Initial-Round Pitch Deck Content Draft

This document is the source content for the first formal PPT/PDF. It is not yet the final slide artifact.

## Slide 1 — FitzSight

**Evidence-grounded Financial Operations Intelligence Agent**

GOAI 2026 · Boundless Agents · AI+金融

Tagline:

> Question → Data → Analysis → Evidence → Decision

## Slide 2 — The problem

Financial teams have dashboards, SQL and BI, but “why did this KPI change?” still creates an analyst investigation:

```text
find tables → define KPI → compare periods → drill dimensions → test significance
→ inspect events → reconcile numbers → write report
```

A generic LLM can produce an explanation faster, but not necessarily a correct or auditable one.

## Slide 3 — The product

FitzSight converts a business question into an auditable investigation.

```text
Question
→ constrained plan
→ deterministic tools
→ evidence graph
→ verifier
→ verified answer
```

The model plans. SQL/Python calculate. The verifier controls what can be presented.

## Slide 4 — Demo workflow 1: FTD deterioration

Question: “Why did European FTD conversion deteriorate after July 15?”

Show:

- affected -7.53 pp vs control -1.21 pp;
- +29.15 min response median;
- statistical validation;
- Team A / Team B contribution decomposition;
- event evidence;
- causal guardrail.

## Slide 5 — Demo workflow 2: Net deposits

Question: “Why did European net deposits fall in the week starting August 3?”

Show:

- net deposits -$223.9k WoW;
- deposits +$24.4k;
- withdrawals +$248.3k;
- top 11 = 92.2% of current withdrawals;
- “observed withdrawal concentration” rather than invented customer motives.

## Slide 6 — Demo workflow 3: Customer Intelligence

Question: “How are European customers segmented by behavioral value?”

Show:

- 6,770 customers, 100% coverage;
- transparent scoring policy;
- High Value = 4.1% customers / 55.8% deposits;
- descriptive use only: no AML/credit/adverse-action inference.

## Slide 7 — Why it is technically different

Four boundaries:

1. Local intent gate before model call.
2. Planner can only emit approved high-level actions.
3. Read-only SQL/Python own every number.
4. Every supported claim must pass EvidenceClaimVerifier.

If verification fails, FitzSight withholds the analytical answer.

## Slide 8 — Evaluation and reproducibility

Current deterministic catalog:

```text
3 scenarios
3 passed
100% evidence coverage
0 verifier violations
```

Show public repository structure, benchmark catalog, tests, and deterministic fallback.

## Slide 9 — Safety / compliance / open source

- synthetic data only;
- no real customer PII or employer data;
- no investment advice;
- no trading/account actions;
- no automated AML, credit, or suitability decisions;
- MIT License;
- DuckDB/local fallback makes demo reproducible without a cloud model.

## Slide 10 — Why FitzSight matters

Existing BI answers **what** happened.

FitzSight investigates **why the measurable evidence changed**, while preserving an audit boundary between evidence and speculation.

Closing line:

> Not “chat with your CSV.” A reproducible financial investigation you can inspect, verify, and challenge.
