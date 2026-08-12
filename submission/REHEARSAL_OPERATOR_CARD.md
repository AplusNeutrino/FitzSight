# FitzSight — Rehearsal Operator Card

## Pitch target

**6:30 target; acceptable window 5:00–8:00.**

1. Problem: managers can ask “why did this metric change?” but BI still requires manual investigation.
2. Architecture: question → constrained planner → deterministic tools → Evidence Registry → verifier.
3. Proof: 5/5 benchmark scenarios, 8/8 adversarial cases, 100% evidence coverage in the fixed benchmark.
4. Differentiation: not chat-with-CSV; LLM cannot write arbitrary SQL or create financial actions.
5. Safety: false-correlation benchmark, causal-language guardrail, fail-closed final answer.
6. Resilience: DuckDB/local path validated; offline HTML/video fallback; external submission remains manual.

## Demo target

**2:20 target; hard stop before 3:00.**

- Start with the CRM/FTD question.
- Show the plan/trace briefly, not every line.
- Show the verified finding, Evidence IDs and guardrail.
- Show either net deposits or false correlation as the second proof point.
- Close on “Question → Data → Analysis → Evidence → Decision Support → Human Decision.”

## Failure rule

If the live UI is unstable for more than ~10 seconds, switch immediately to:

1. deterministic CLI;
2. offline HTML;
3. MP4 backup.

Do not debug on stage and do not switch to an unverified calculation path.

## Q&A anchors

- **Why Agent?** It coordinates multi-step investigation, not just text generation.
- **What does the LLM control?** Only an approved high-level intent/action plan.
- **Who calculates numbers?** Deterministic SQL/Python tools.
- **How do you stop hallucinated causes?** Evidence IDs + verifier + false-correlation/falsification checks.
- **Why synthetic data?** Reproducible ground truth without PII/employer/confidential data.
- **What if the cloud fails?** Core demo has deterministic local/offline fallback.
## v0.12.1 stage cue

Main demo order: **CRM question → branch trace → verified answer/document Evidence → failure branch → false-correlation refusal → Evaluation v2 → Human decision boundary.** Use net deposit / segmentation / marketing only when asked for breadth.

