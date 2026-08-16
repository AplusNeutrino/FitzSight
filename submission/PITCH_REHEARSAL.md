# FitzSight — Pitch & Demo Rehearsal Card

## Target timing

- **Pitch:** target 6:30, hard practice ceiling 7:15.
- **Demo:** target 2:20, hard practice ceiling 2:45.
- Keep 30–45 seconds of buffer for window switching, loading, or judge interruption.

## 6:30 pitch timing

| Time | Slide / message | Exit line |
|---|---|---|
| 0:00–0:35 | Problem | “Financial teams have data tools; the bottleneck is turning a question into a defensible investigation.” |
| 0:35–1:05 | Product | “FitzSight separates planning, calculation, evidence, and verification.” |
| 1:05–1:50 | Architecture | “The model never owns the numbers; deterministic tools do.” |
| 1:50–2:35 | CRM / FTD example | “The result is not a narrative — it is a claim with SQL/statistical evidence.” |
| 2:35–3:15 | Net-deposit example | “The Agent distinguishes deposit pressure from withdrawal concentration.” |
| 3:15–3:50 | Customer Intelligence | “Segmentation is transparent and descriptive, not a hidden risk score.” |
| 3:50–4:30 | Marketing / false correlation | “Nearby events are context, not causes; FitzSight actively falsifies weak explanations.” |
| 4:30–5:15 | Trust boundary | “Planner output is untrusted; SQL is read-only; verifier fails closed.” |
| 5:15–5:50 | Evaluation | “Five scenarios pass 5/5; eight adversarial cases pass 8/8.” |
| 5:50–6:20 | Open-source / reproducibility | “Synthetic generator, tools, evidence layer, tests and evaluation harness are reusable.” |
| 6:20–6:30 | Close | “Question → Data → Analysis → Evidence → Decision Support → Human Decision.” |

## 2:20 live/local demo timing

1. **0:00–0:15 — Open FitzSight.** State that the deterministic fallback is selected and the backend is DuckDB when available.
2. **0:15–0:30 — Ask one business question.** Recommended: “Why did European FTD conversion deteriorate after July 15?”
3. **0:30–0:55 — Show KPI cards.** FTD change, control, response-time shift, anomaly days, verified-claim count.
4. **0:55–1:20 — Show chart + findings.** Point to the strongest team contribution and statistical validation.
5. **1:20–1:45 — Show investigation trace.** Emphasize approved high-level actions and deterministic tools.
6. **1:45–2:05 — Open two Evidence cards.** Show SQL/tool parameters, result digest and Evidence IDs.
7. **2:05–2:20 — Show guardrail / verifier.** End on `verified`, then mention that unsupported trade/freeze-account requests fail closed.

## Fallback order

1. Streamlit live demo, if runtime smoke test is green.
2. `python scripts/start_demo.py --mode cli --backend duckdb`.
3. `submission/FitzSight_Offline_Demo.html`.
4. PPT/PDF screenshots and benchmark/evidence JSON.

## Practice log

Do not mark the tracker rehearsal task complete until a human timed run has been performed. Record actual timings below after rehearsal.

| Date | Pitch | Demo | Issues | Result |
|---|---:|---:|---|---|
| | | | | |
## v0.13.0 narrative gate

The timed pitch must preserve the 1+1 structure: one complete CRM/FTD investigation and one refusal/trust case. Do not re-expand the main story into five equal demos. Human rehearsal evidence remains required before R4/R5 can be marked done.

