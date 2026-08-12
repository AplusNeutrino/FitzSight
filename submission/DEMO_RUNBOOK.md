# FitzSight — Initial-Round Demo Runbook

## Objective

Demonstrate that FitzSight is not a generic chat interface. The demo must visibly show a bounded Agent plan, deterministic tool execution, Evidence IDs, verification, and a final decision-support answer.

## Recommended live scenario

Use the CRM / FTD benchmark first because it exercises the widest set of capabilities in a compact story.

```text
Why did European FTD conversion deteriorate after July 15?
```

Expected headline evidence:

- affected FTD change: **-7.53 pp**;
- European control: **-1.21 pp**;
- affected median response-time change: **+29.15 min**;
- conversion p-value: **0.00235**;
- Team A / Team B negative contribution;
- nearby CRM routing event;
- final status: **verified**.

## 2 minute 30 second demo route

### 0:00–0:20 — Ask the question

Open FitzSight and select the CRM / FTD preset. State:

> “The business question is simple: why did conversion deteriorate? FitzSight must investigate it rather than guess.”

Click **Investigate**.

### 0:20–0:50 — Show the plan

Open / point to **Investigation trace**.

Call out:

- approved high-level actions only;
- planner cannot generate SQL or arbitrary tool parameters;
- deterministic tools own calculations.

### 0:50–1:20 — Show the business result

Point to KPI cards:

```text
Affected FTD      -7.53 pp
Europe control    -1.21 pp
Response median   +29.15 min
```

Then show the team contribution chart.

### 1:20–1:50 — Show evidence

Expand one SQL Evidence card and one statistical-test Evidence card.

State:

> “Every supported factual claim is linked to append-only evidence. The final renderer does not recompute these numbers.”

### 1:50–2:10 — Show verification

Point to verifier status and the causal-language guardrail.

State:

> “The benchmark supports the CRM routing change as a root-cause candidate. FitzSight does not silently turn temporal association into real-world causal proof.”

### 2:10–2:30 — Show the safety differentiator

Switch briefly to the false-correlation preset or use the slide/PDF backup.

State:

> “We also benchmark explanations FitzSight must refuse. In the Asia scenario, an office relocation is nearby in time, but the measurable deterioration is concentrated in Affiliate leads. FitzSight rejects the tempting causal story.”

## Backup sequence

If live Streamlit fails:

```bash
python scripts/start_demo.py --mode cli --backend duckdb
```

If DuckDB is unavailable on a backup laptop:

```bash
python scripts/start_demo.py --mode cli --backend sqlite
```

If the UI is unavailable but Python is working, use the deterministic CLI output and the submitted PPT/PDF.

## Do not do during the demo

- Do not change synthetic benchmark seed immediately before presentation.
- Do not improvise unsupported financial questions.
- Do not enter real customer data.
- Do not enable a live model provider unless it has already been runtime-validated on the presentation machine.
- Do not describe synthetic benchmark accuracy as production accuracy.

## v0.12 primary judge-facing product-process view

The primary demo story is now the CRM / FTD hero. Before relying on live Streamlit, the operator can show `FitzSight_Hero_Run_Evidence.png` or open `FitzSight_Hero_Run_Evidence.html`. Both are derived from the real verified hero run in `docs/V0.12_HERO_RUN.json` and show:

1. user question;
2. bounded adaptive trace;
3. branch rationale;
4. Evidence IDs;
5. source-paragraph document evidence;
6. verifier PASS;
7. guarded final answer;
8. approved follow-up.

Then use the Asia office-relocation case as the single strongest refusal/falsification story. Other workflows are breadth/Q&A, not equal-weight main-demo sections.
## v0.12.1 primary judge route — 1 hero + 1 refusal

1. Open with the Brokerage / FinTech Operations Analyst question: **“Why did European FTD conversion deteriorate after July 15?”**
2. Show the bounded CRM execution trace: contribution/statistics → conditional latency/anomaly → conditional event check → source-addressable document Evidence → verifier.
3. Show the verified answer and explain that the CRM routing item is a **supported candidate, not causal proof**.
4. Show the tested dependency-failure branch: event lookup error → error Evidence → no document corroboration → `insufficient_evidence` → verified bounded answer.
5. Switch once to the Asia false-correlation case and show the refusal: Affiliate deterioration is measured; office relocation is nearby but causal support is false.
6. Close with Evaluation v2, safety/human-decision boundary, and the three additional workflows as breadth only.

Do not spend the main demo running five equal workflows. Net deposit, Customer Intelligence and Marketing are appendix/Q&A breadth proof.

