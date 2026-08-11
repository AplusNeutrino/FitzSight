# FitzSight Architecture

Version: v0.5.0

## North-star boundary

```text
LLM / Planner = decide what approved investigation to run
SQL / Python   = calculate
Evidence       = prove what ran
Verifier       = decide whether claims may be shown
UI             = render verified results
```

No layer above the deterministic tools is allowed to invent business numbers.

## Runtime architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                        User / UI                            │
│              CLI or Streamlit demo shell                   │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Supported Intent Gate                    │
│  CRM/FTD investigation | Net-deposit anomaly investigation │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                   Constrained Planner                       │
│ deterministic fallback | structured JSON | OpenAI optional │
│        approved intent + approved actions only             │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              MultiIntentInvestigationEngine                 │
│                                                             │
│  ┌──────────────────────┐  ┌──────────────────────────────┐ │
│  │ CRM/FTD Engine       │  │ Net Deposit Engine           │ │
│  │ conversion/control   │  │ deposits/withdrawals         │ │
│  │ stats/contribution   │  │ concentration/control       │ │
│  │ anomaly/events       │  │ events/guardrail            │ │
│  └──────────────────────┘  └──────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Deterministic Tools                      │
│ Schema | Read-only SQL | Statistics | Contribution | KPI   │
│ Anomaly | local decomposition                              │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     Evidence Registry                       │
│ Evidence ID | inputs | status | digest | compact result    │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                   EvidenceClaimVerifier                     │
│ references | digest | status | *_gt boundary | causality   │
└────────────────────────────┬────────────────────────────────┘
                             │
                        PASS │ FAIL
                     ┌───────┴────────┐
                     ▼                ▼
              Verified answer    Fail closed
```

## Data layer

Current reproducible source:

```text
Synthetic CSV bundle
├── customers
├── salespeople
├── sales_activity
├── deposits
├── withdrawals
├── trades
└── business_events
```

Preferred analytical backend:

```text
DuckDB
```

Restricted/offline fallback:

```text
SQLite
```

The SQL Tool never receives direct model-generated SQL.

## Intent 1: CRM routing / FTD

Deterministic path:

```text
schema
→ affected cohort SQL
→ control SQL
→ two-proportion test
→ response-time test
→ team contribution decomposition
→ robust daily anomaly scan
→ business event check
→ evidence-linked claims
```

## Intent 2: net deposits

Deterministic path:

```text
schema
→ baseline/current deposit SQL
→ baseline/current withdrawal SQL
→ net-deposit identity decomposition
→ top-customer withdrawal concentration
→ regional per-customer control
→ business event check
→ evidence-linked claims
```

The identity enforced by the engine is:

```text
net_change = deposit_change - withdrawal_change
```

## Optional model provider

The OpenAI provider is above the local scope gate.

```text
question
→ local supported-intent classifier
→ provider Structured Output
→ local plan validator
→ deterministic executor
```

It is impossible for the provider contract to authorize an unknown intent, direct SQL, arbitrary tool parameters, or a high-impact financial action.

## UI boundary

`streamlit_app.py` only:

- submits a question;
- selects approved runtime options;
- renders verified findings;
- shows metrics/evidence.

It does not recompute financial metrics.

## Expansion rule

Future functionality should generally be added in this order:

1. deterministic data/tool capability;
2. tests and evidence;
3. benchmark scenario;
4. approved Agent intent/action contract;
5. optional model planning;
6. UI.

This prevents the interface or LLM layer from outrunning the analytical evidence layer.
