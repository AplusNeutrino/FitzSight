# FitzSight — GOAI Initial-Round 12-Slide Speaker Notes (v0.13.0)

> Competition-facing numerical claims are derived from verified deterministic runtime evidence or the checked-in v0.12 evaluation JSON. This deck does not claim live Streamlit or live DeepSeek-provider validation.

## Slide 1 — FitzSight

“FitzSight is an evidence-grounded financial operations Agent for Brokerage / FinTech Operations Analysts. The operating principle is simple: autonomous investigation, human decision.”

## Slide 2 — Industry problem

“Dashboards and SQL show what changed. The expensive part is the investigation behind why: define the KPI, compare cohorts, drill drivers, test significance, inspect operational context, reconcile evidence, then write a report.”

## Slide 3 — Product

“The planner can select approved analytical actions, but deterministic SQL and Python own every number. Evidence records each step. The verifier determines which claims may reach the analyst.”

## Slide 4 — Hero journey

“This is the actual v0.12 verified execution trace, rendered from runtime JSON. The contribution and statistical results trigger the next approved latency and event branches. The planner still cannot invent SQL or arbitrary tools.”

## Slide 5 — Hero finding

“The affected European teams moved -7.53 pp versus -1.21 pp in the control cohort. Median response time changed +29.15 minutes. The evidence chain also includes contribution, anomaly, operational-event and document evidence at CRM-CHANGE-2026-0715#p1. The final status is supported_candidate, not proven real-world causality.”

## Slide 6 — Failure branch

“We also test the branch where the event dependency fails. FitzSight records error Evidence, skips document corroboration, changes root-cause status to insufficient_evidence, and still returns a verified bounded answer. The system is not rewarded for always forcing a cause.”

## Slide 7 — Refusal case

“In Asia, aggregate FTD changes -8.13 pp; Affiliate conversion changes -15.81 pp. A nearby office relocation exists, but causal support is FALSE. Temporal proximity is explicitly rejected as proof.”

## Slide 8 — Breadth

“Three other workflows prove reuse without diluting the main story: client-fund-flow concentration, descriptive customer segmentation, and acquisition volume-versus-quality. For example, current net-deposit change is -$187.8k; customer segmentation covers 100%; marketing lead volume changes +315% while FTD changes -10.84 pp.”

## Slide 9 — Architecture

“The technical depth is in authority separation: local intent gate, constrained planner, deterministic tools, source-addressable Evidence Registry, EvidenceClaimVerifier, and an explicit human-decision boundary.”

## Slide 10 — Evaluation v2

“Five fixed benchmark scenarios pass. Eight holdout seed-and-paraphrase runs route and verify successfully with 100% evidence coverage. Supported-candidate rate is only 75% because one unseen CRM seed correctly returns insufficient evidence. In the controlled architecture ablation, full FitzSight refuses 100% of adversarial fixtures; removing the verifier/evidence gate yields 100% unsafe-answer rate. This is not a Generic LLM baseline.”

## Slide 11 — Safety and reuse

“Current implementation uses synthetic data, read-only analytics, evidence tracing and fail-closed verification. Enterprise RBAC, PII masking and retention remain a production blueprint, not an implemented claim. Final professional judgment remains human.”

## Slide 12 — Close

“BI tells you what changed. FitzSight investigates what the measurable evidence supports — and what it does not. It is a reproducible financial investigation you can inspect, verify, challenge, and sometimes refuse.”
