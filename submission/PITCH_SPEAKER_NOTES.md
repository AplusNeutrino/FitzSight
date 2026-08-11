# FitzSight — 12-Slide Speaker Notes

> Numeric claims in Slides 4-8 are generated from fresh verified deterministic FitzSight runs by `scripts/build_pitch_deck.py`.

## Slide 1 — FitzSight

“FitzSight is an evidence-grounded financial operations Agent. It turns a business question into a bounded, reproducible investigation: question, data, analysis, evidence, decision.”

## Slide 2 — Problem

“Financial teams already have dashboards and SQL. The slow part is the investigation behind ‘why did this change?’ A generic LLM can write a plausible explanation quickly, but plausibility is not auditability.”

## Slide 3 — Product

“The model or fallback planner selects an approved workflow. SQL and Python calculate. Evidence records each step. A verifier decides which claims are allowed into the final answer.”

## Slide 4 — CRM / FTD

“The affected European teams changed by -7.53 pp versus -1.21 pp in the control cohort, while median response time changed by +29.15 minutes. The result is a supported root-cause candidate, not a causal proof.”

## Slide 5 — Net deposits

“European net deposits changed by -$187.8k week over week. Deposits changed by +$59.2k, while withdrawals increased by +$246.9k. The largest 11 withdrawals account for 91.6% of current withdrawals. FitzSight reports that concentration without inventing customer motives.”

## Slide 6 — Customer Intelligence

“Customer segmentation is transparent and descriptive. It uses observable behavior, not hidden benchmark labels. High Value customers are 3.7% of European customers but contribute 53.7% of deposits in the current synthetic benchmark.”

## Slide 7 — Acquisition quality

“Lead volume increased 315%, while FTD conversion changed by -10.84 pp. FitzSight separates volume, channel mix and within-channel performance; Paid Search conversion changed by -16.44 pp with p=4.43e-05.”

## Slide 8 — False correlation

“This is a deliberate trap. An office relocation occurs near an Asia conversion decline of -8.13 pp. Affiliate conversion changes by -15.81 pp; the falsification check therefore rejects the nearby office event as a supported cause.”

## Slide 9 — Technical difference

“The four trust boundaries are local intent gating, constrained planning, deterministic tools and a fail-closed verifier. A model never receives unrestricted authority to execute SQL or financial actions.”

## Slide 10 — Evaluation

“The benchmark contains 5 deterministic scenarios and 5 pass. Mean evidence coverage is 100%, with 0 verifier violations. The adversarial release gate contains 8 cases and 8 pass.”

## Slide 11 — Safety and open source

“All benchmark data is synthetic. The system is not an investment adviser or automated compliance engine. The core project is MIT licensed, DuckDB is the preferred local backend, and a deterministic fallback keeps the demo usable without a cloud model.”

## Slide 12 — Close

“BI tells you what changed. FitzSight investigates why the measurable evidence changed — with a result you can inspect, verify, challenge, and sometimes refuse.”
