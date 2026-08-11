# FitzSight Architecture — v0.6

## Core principle

```text
LLM / planner decides only the approved analytical workflow.
SQL / Python calculates.
Evidence Registry records.
Verifier decides what may be presented.
```

## Runtime

```text
User question
    ↓
Local intent classifier
    ├── CRM / FTD
    ├── Net Deposit
    └── Customer Intelligence
    ↓
Constrained planner
    ├── deterministic fallback
    ├── JSON adapter
    └── optional OpenAI Responses provider
    ↓
Intent-specific deterministic executor
    ↓
Read-only analytical tools
    ↓
Evidence Registry
    ↓
EvidenceClaimVerifier
    ↓
Verified answer / fail closed
```

## Approved deterministic executors

### CRM / FTD

- schema inspection;
- affected/control SQL;
- statistical tests;
- contribution decomposition;
- anomaly detection;
- event check.

### Net Deposit

- period money-flow measurement;
- deposit/withdrawal driver decomposition;
- customer concentration;
- regional controls;
- event check.

### Customer Intelligence

- schema inspection;
- observable customer-feature aggregation;
- transparent behavioral-value segmentation;
- segment deposit/withdrawal/trading profiles;
- decision-use guardrail.

## Data layer

Preferred: DuckDB.

Fallback: SQLite for restricted/offline development.

Synthetic CSV files are the reproducible source for the competition benchmark.

## SQL boundary

Normal Agent queries are passed through `ReadOnlySQLTool`:

- SELECT/WITH only;
- no multiple statements;
- no DDL/DML/admin keywords;
- no external file/network scan functions;
- bounded output;
- every call registered as evidence.

The v0.6 row limit is 25,000 so the complete 20,000-customer synthetic benchmark can be profiled without truncation.

## Evidence boundary

Every evidence record contains:

- Evidence ID;
- tool name;
- parameters;
- result payload;
- result digest;
- execution status.

The final renderer does not recompute analytical metrics. It renders only previously verified claim text.

## Evaluation-only data

Synthetic generator fields ending in `_gt` are benchmark-only. Normal Agent SQL is prohibited from using them, and the verifier scans read-only SQL evidence for leakage.

## UI boundary

Streamlit is a presentation layer. KPI cards, charts, trace, and evidence cards are constructed from verified result objects. The UI must not become an independent analytics path.
