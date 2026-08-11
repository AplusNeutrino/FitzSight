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

---

## v0.3 diagnostic extension

v0.3 inserts two deterministic diagnostics between the core statistical layer and final evidence rendering:

```text
Read-only SQL / KPI / statistics
          ↓
ContributionAnalysisTool
          ↓
AnomalyDetectionTool
          ↓
Evidence-linked diagnostic claims
```

The contribution tool performs an additive symmetric rate decomposition so that team-level impacts reconstruct the aggregate FTD-rate movement. The anomaly tool compares current observations with a robust historical baseline using median/MAD thresholds.

Neither tool is permitted to turn an observed contribution or anomaly into a causal, compliance, fraud, or investment conclusion on its own.

---

## v0.4 constrained Agent extension

v0.4 places a constrained planning and verification layer above the existing deterministic stack:

```text
Question
  ↓
ConstrainedRulePlanner / StructuredJSONPlanner
  ↓
validate_plan() allow-list
  ↓
FitzSightAgent
  ↓
DeterministicInvestigationEngine
  ↓
Read-only SQL / statistics / contribution / anomaly tools
  ↓
EvidenceRegistry
  ↓
EvidenceClaimVerifier
  ↓
Verified FinalAnswer
```

### New responsibility boundaries

**Planner**

- classifies only currently approved intent(s);
- emits high-level actions only;
- cannot emit SQL, arbitrary tool parameters, or business actions;
- unsupported scope is refused before a structured external planner callback is invoked.

**Agent Orchestrator**

- validates the plan again at execution time;
- routes the approved intent into the deterministic engine;
- records planning, verification, and final-answer audit events;
- does not give the planner direct access to the analytical store.

**Verifier**

- fails closed when claim evidence is missing or corrupted;
- checks evidence digest/status;
- checks the evaluation-only `_gt` SQL boundary;
- rejects causal wording that exceeds the root-cause evidence status;
- controls whether final findings may be rendered.

This creates a deliberate separation between **planning**, **calculation**, **evidence**, and **presentation**.
