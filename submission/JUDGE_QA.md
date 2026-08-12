# FitzSight — Judge Q&A Preparation

## 1. Why is this an Agent rather than a dashboard or scripted report?

FitzSight starts from a business question, maps it to an approved investigation workflow, executes multiple analytical tools, gathers evidence, verifies claims, and renders a bounded decision-support answer. The deterministic fallback makes the current benchmark reproducible; the same constrained plan contract also supports an external structured planner.

## 2. What does the LLM actually do?

Only planning within an approved intent/action contract. It does not calculate KPIs, generate unrestricted SQL, execute trades, move money, freeze accounts, or create automated compliance decisions. SQL/Python tools own calculations and EvidenceClaimVerifier controls final claims.

## 3. How do you reduce hallucination risk?

Supported factual claims must reference Evidence IDs. The verifier checks evidence existence, digest integrity, successful tool status, causal-language boundaries, and evaluation-only ground-truth leakage. If verification fails, the answer is withheld.

## 4. Why use synthetic data?

The competition prototype must be reproducible without exposing customer PII, former-employer data, confidential CRM exports, or restricted transaction records. Synthetic scenarios also provide hidden ground truth for evaluation. Production deployment would require separately authorized data connectors and governance.

## 5. Does 100% benchmark accuracy mean production accuracy?

No. The 100% figures refer only to the current fixed synthetic benchmark and adversarial suites. They demonstrate that the implemented workflow recovers known benchmark patterns and respects evidence/safety gates. They are not claims about unseen real-world financial data.

## 6. Why is false-correlation rejection important?

Financial operations teams often have many nearby events, campaigns, system changes, and business narratives. Temporal proximity can easily become an attractive but unsupported story. FitzSight explicitly benchmarks a case where a nearby office relocation must be rejected because the measurable deterioration is channel-specific elsewhere.

## 7. What happens when FitzSight does not have enough evidence?

It should return an insufficient-evidence or withheld result rather than invent a conclusion. The project treats safe refusal as a measurable capability, not a failure mode to hide.

## 8. Can it connect to a real warehouse?

The current competition build uses local synthetic CSVs loaded through DuckDB, with a SQLite fallback. The analytical Tool Layer and read-only SQL boundary are designed so a future authorized warehouse connector can replace the local source without giving the planner unrestricted write access.

## 9. Why DuckDB?

It provides a lightweight analytical SQL engine that works well with local CSV/Parquet-style competition demos, supports reproducible setup, and does not require a separate database server. DuckDB runtime has been separately validated in the deployment environment.

## 10. What is the strongest product differentiator?

The combination of autonomous investigation and an explicit audit boundary: Question → Plan → deterministic tools → Evidence → Verifier → Answer. The system is evaluated both on conclusions it supports and explanations/actions it refuses.

## 11. What would you build next with more time?

First, validate and polish the live Streamlit demo and external structured planner. Then add authorized production data connectors, stronger evaluation on unfamiliar datasets, role-based access, persistent audit storage, and human review workflows for high-impact contexts.

## 12. Is this investment advice or an automated compliance system?

No. FitzSight is internal analytical decision support. It does not make investment recommendations, execute trades, freeze accounts, label customers for AML enforcement, or make automated credit/suitability/adverse-action decisions.

## v0.12.1 top-line answers

**Why is this an Agent rather than a fixed dashboard?** The CRM hero allows deterministic tool results to select the next action from a closed approved catalog, then verifies the resulting claims; the planner still cannot generate arbitrary SQL or tool parameters.

**What happens when evidence is missing?** The tested event-dependency failure records error Evidence, skips unsupported document corroboration, sets `root_cause_status=insufficient_evidence`, and still returns only a verified bounded answer.

**Why trust the benchmark?** The fixed 5/5 suite is supplemented by eight unseen-seed/question-paraphrase holdouts and a controlled verifier/evidence-gate architecture ablation. One unseen CRM seed remains insufficient rather than being relabeled as a success.

**Does FitzSight make financial decisions?** No. Autonomous investigation, human decision. It does not provide investment, AML, credit, suitability, trading or account-action decisions.
