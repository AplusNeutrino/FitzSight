# FitzSight — Initial-Round Pitch Deck Content Draft

This document is the content source for the formal PPT/PDF artifact. The slide file itself is tracked separately and is not marked complete until generated and reviewed.

## Slide 1 — FitzSight

**Evidence-grounded Financial Operations Intelligence Agent**

GOAI 2026 · Boundless Agents · AI+金融

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

## Slide 4 — Demo: FTD deterioration

Question: “Why did European FTD conversion deteriorate after July 15?”

Show:

- affected **-7.53 pp** vs control **-1.21 pp**;
- response median **+29.15 min**;
- statistical validation;
- Team A / Team B contribution decomposition;
- event evidence;
- causal guardrail.

## Slide 5 — Demo: Net deposits

Question: “Why did European net deposits fall in the week starting August 3?”

Show:

- net deposits **-$223.9k** WoW;
- deposits **+$24.4k**;
- withdrawals **+$248.3k**;
- top 11 = **92.2%** of current withdrawals;
- observed withdrawal concentration rather than invented customer motives.

## Slide 6 — Demo: Customer Intelligence

Question: “How are European customers segmented by behavioral value?”

Show:

- **6,770** customers, 100% coverage;
- transparent scoring policy;
- High Value = **4.1%** customers / **55.8%** deposits;
- descriptive use only: no AML/credit/adverse-action inference.

## Slide 7 — Demo: Volume ≠ quality

Question: “Why did Americas lead volume rise while FTD conversion fell?”

Show:

- leads **+315%**;
- aggregate FTD **-10.84 pp**;
- Paid Search mix **+60.52 pp**;
- Paid Search FTD **-16.44 pp**;
- Paid Search statistical test **p = 4.43e-05**.

Message: FitzSight separates volume, mix and within-channel performance.

## Slide 8 — The false-correlation test

Question: “Asia conversion fell after July 20. Did the nearby office relocation cause it?”

Show:

- Asia FTD **-8.13 pp**;
- Affiliate FTD **-15.81 pp**;
- Affiliate **p = 0.00463**;
- nearby office event detected;
- event causal support = **false**;
- FitzSight rejects the tempting causal story.

Message: **The system is evaluated on explanations it refuses to make, not only answers it produces.**

## Slide 9 — Why it is technically different

Four boundaries:

1. Local intent gate before model call.
2. Planner can only emit approved high-level actions.
3. Read-only SQL/Python own every number.
4. Every supported claim must pass EvidenceClaimVerifier.

If verification fails, FitzSight withholds the analytical answer.

## Slide 10 — Evaluation and reproducibility

```text
5 benchmark scenarios / 5 PASS
100% root-cause scenario accuracy
100% false-correlation rejection accuracy
100% evidence coverage
0 verifier violations
```

Adversarial release gate:

```text
8 cases / 8 PASS
100% scope refusal
100% planner-policy catch
100% causal-overclaim catch
100% ground-truth-leak catch
```

Show public repository, benchmark catalog, test suite, and deterministic fallback.

## Slide 11 — Safety / compliance / open source

- synthetic data only;
- no real customer PII or employer data;
- no investment advice;
- no trading/account actions;
- no automated AML, credit, or suitability decisions;
- `_gt` fields prohibited in normal Agent SQL;
- MIT License;
- DuckDB/local fallback keeps core demo reproducible without a cloud model.

## Slide 12 — Why FitzSight matters

Existing BI answers **what** happened.

FitzSight investigates **why the measurable evidence changed**, while preserving an audit boundary between evidence and speculation.

> Not “chat with your CSV.” A reproducible financial investigation you can inspect, verify, challenge—and sometimes refuse.
