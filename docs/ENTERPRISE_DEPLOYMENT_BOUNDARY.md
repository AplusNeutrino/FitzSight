# FitzSight — Enterprise Deployment Boundary

This document is a **production blueprint**, not a claim that all enterprise controls are implemented in the current competition PoC.

## Current PoC — implemented and evidenced

- synthetic competition data only;
- local approved-intent gate;
- constrained high-level planner contract;
- deterministic read-only SQL / Python analytical tools;
- append-only Evidence Registry with digests;
- EvidenceClaimVerifier fail-closed output gate;
- evaluation-only `*_gt` field boundary;
- bounded CRM/FTD conditional investigation;
- fixed synthetic document-evidence corpus with stable source/paragraph IDs;
- no trading, transfer, freeze, credit, suitability, AML-enforcement, or customer-contact actions.

## Production blueprint — planned requirements

A real brokerage / FinTech deployment should place FitzSight behind enterprise controls:

```text
Enterprise identity / SSO
        ↓
RBAC + row/field authorization
        ↓
PII masking / data-minimization policy
        ↓
Read-only semantic / analytical data layer
        ↓
FitzSight bounded investigation runtime
        ↓
Evidence + audit log / retention policy
        ↓
Authorized human Operations Analyst
        ↓
Human business decision outside FitzSight
```

The following are **planned production controls**, not current PoC implementation claims:

- enterprise identity federation and SSO;
- RBAC / ABAC;
- row-level and field-level policies;
- production PII masking / tokenization;
- organization-specific audit retention and deletion policy;
- production secrets management;
- tenant isolation;
- enterprise observability / incident response;
- formal model-risk, compliance, legal, and change-management approvals.

## Decision boundary

FitzSight provides analytical **decision support**. It does not autonomously make or execute investment, credit, AML, suitability, eligibility, account-restriction, or other high-impact financial decisions.

> **Autonomous investigation. Human decision.**
