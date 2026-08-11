# FitzSight Compliance and Safety Boundary

## Intended use

FitzSight is a financial-operations **analytical decision-support prototype**. It is designed to investigate operational KPI changes and produce evidence-linked analytical briefs.

## Explicit non-uses

FitzSight is not designed to:

- give investment advice;
- execute trades;
- transfer funds;
- freeze or restrict accounts;
- contact customers automatically;
- make AML enforcement decisions;
- make credit, eligibility, suitability, or adverse-action decisions;
- infer protected/sensitive traits;
- replace legal/compliance review.

## Data policy

Competition/demo data are synthetic. The repository must not contain real customer PII, confidential employer data, internal CRM exports, private trading records, or API secrets.

Synthetic fields ending in `_gt` exist only to construct/evaluate benchmark scenarios. Normal Agent SQL is prohibited from reading them, and the verifier checks for `_gt` leakage in SQL evidence.

## Planner boundary

Planner/model output is untrusted. A planner can only select an approved high-level intent/action sequence. It cannot create SQL, arbitrary tool arguments, or high-impact financial actions.

## SQL boundary

The SQL tool is read-only and rejects write/DDL/admin operations, multiple statements, and external file/network scan functions.

## Evidence boundary

Supported factual claims require Evidence IDs. Evidence digests and tool statuses are checked before the final answer is rendered. Verification failure causes the answer to be withheld.

## Causal-language boundary

Operational event proximity is not sufficient evidence of causality. v0.7 includes a dedicated false-correlation benchmark in which a nearby office-relocation event must be rejected as the cause of an unrelated channel-specific conversion deterioration.

## Customer Intelligence boundary

Behavioral segmentation is descriptive only. It must not be converted into credit, AML, suitability, eligibility, account-restriction, or adverse-action decisions.

## Open source and dependencies

Project-owned code is released under the MIT License. Third-party packages remain under their respective licenses; see `THIRD_PARTY_NOTICES.md`.

## Human review

Any real-world high-impact decision must occur outside FitzSight and requires authorized human review under the deploying organization's policies and applicable law.
