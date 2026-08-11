# FitzSight Architecture — v0.2

## Objective

v0.2 proves that a business question can be transformed into a deterministic, evidence-linked investigation before any LLM is allowed to control planning or narration.

## Components

```text
CLI / future UI
    |
    v
DeterministicInvestigationEngine
    |
    +--> SchemaInspectorTool
    +--> ReadOnlySQLTool
    +--> StatisticalTestTool
    +--> KPITool
    +--> PeriodComparisonTool
    |
    v
EvidenceRegistry
    |
    v
AnalyticsStore
    +--> DuckDB (preferred)
    +--> SQLite (offline fallback)
    |
    v
Synthetic CSV bundle
```

## Responsibility boundaries

### Investigation Engine

- understands only explicitly supported v0.2 intents;
- creates a fixed investigation plan;
- chooses predeclared Tools;
- builds supported claims from Tool outputs;
- applies causal-language guardrails;
- never reads evaluation-only `*_gt` fields.

### Tool Layer

- performs deterministic calculations;
- provides explicit failure states;
- creates evidence records;
- does not ask an LLM to calculate metrics.

### Analytics Store

- loads local synthetic CSV files;
- prefers DuckDB;
- exposes an offline SQLite fallback for restricted environments;
- does not accept arbitrary user file paths during SQL execution.

### Evidence Registry

Each record contains:

- Evidence ID;
- Tool name;
- parameters;
- result digest;
- timestamp;
- status;
- compact result payload.

## Future v0.3 boundary

The future LLM layer should sit **above** the current deterministic Tools:

```text
LLM Planner / Orchestrator
        ↓
existing v0.2 Tool contracts
        ↓
Evidence Registry
        ↓
Verifier
        ↓
Auditable report
```

The LLM should not receive direct authority to mutate the database or fabricate numeric results.
