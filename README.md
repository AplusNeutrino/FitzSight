# FitzSight

**Evidence-grounded Financial Operations Intelligence Agent**

FitzSight is the implementation project for **GOAI 2026 · Boundless Agents · AI+金融**.

The core product question is simple:

> **Why did this business metric change?**

FitzSight is designed to turn that question into a reproducible investigation based on real tool execution, SQL, statistics, comparison cohorts, and traceable evidence instead of an unsupported LLM narrative.

## Current release: v0.3.0

v0.3 strengthens the deterministic diagnostic and evidence layer **before an LLM Agent is introduced**.

Implemented:

- deterministic synthetic financial-operations dataset generator;
- customers, salespeople, sales activity, deposits, withdrawals, trades, and business events;
- injected `CRM_ROUTING_CHANGE` ground-truth scenario;
- preferred DuckDB analytical-store backend plus explicit SQLite offline fallback;
- Schema Inspector;
- read-only SQL Tool with destructive-statement and external-file/network guards;
- canonical KPI Tool;
- Period Comparison Tool;
- two-proportion, Mann–Whitney and Welch t-test support;
- evidence IDs, tool parameters, result digests, status, and compact evidence payloads;
- deterministic investigation engine for the European FTD / July 15 benchmark;
- symmetric team-level contribution decomposition for FTD-rate changes;
- robust baseline anomaly detection for post-change response-time medians;
- claim-to-evidence mapping and causal-language guardrail;
- automated test suite.

Not yet implemented:

- LLM orchestration / dynamic Agent planning;
- customer segmentation;
- interactive Streamlit UI;
- multi-scenario benchmark harness.

## Quick start

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

python scripts/generate_data.py
python scripts/run_baseline.py
python scripts/investigate.py --question "Why did European FTD conversion deteriorate after July 15?"
pytest -q
```

`pip install -e ".[dev]"` installs DuckDB. The runtime defaults to DuckDB when available. A SQLite fallback exists for restricted/offline development environments:

```bash
python scripts/investigate.py --backend sqlite
```

Generated files are written to `data/generated/` and ignored by Git.

## Current benchmark scenario

On **2026-07-15**, a synthetic CRM routing change affects European `Team A` and `Team B`:

```text
CRM routing change
      ↓
lead response time increases
      ↓
FTD conversion probability decreases
```

The deterministic v0.3 investigation should recover:

- a material FTD conversion decline in the affected teams;
- a large response-time increase;
- a materially smaller conversion movement in the European control cohort;
- a statistically significant affected conversion shift;
- a matching operational event in the business-event log.

The engine reports this event as a **supported root-cause candidate** rather than automatically converting temporal association into a real-world causal conclusion.

## Evidence-first architecture

```text
Business question
      ↓
Deterministic investigation plan (v0.3)
      ↓
Schema Inspector
      ↓
Read-only SQL
      ↓
Statistics / KPI / period comparison
      ↓
Contribution decomposition / anomaly detection
      ↓
Evidence Registry
      ↓
Supported claims + evidence IDs + guardrails
```

The next stage will replace the deterministic planner with an LLM planner/orchestrator while retaining the same deterministic calculation and evidence tools.

## SQL safety policy

The read-only SQL Tool:

- allows only `SELECT` / `WITH` queries;
- rejects multi-statement SQL;
- rejects mutation / DDL / configuration commands;
- rejects SQL comments in Agent-generated queries;
- rejects external file/network scan functions such as `read_csv`, `read_parquet`, `glob`, and database scan helpers;
- applies a maximum returned-row limit;
- records failed executions as evidence before raising an error.

This is defense in depth for a local competition prototype, not a substitute for enterprise database permissions.

## Design principles

1. **Evidence first** — numeric claims come from deterministic tools.
2. **Synthetic by default** — never use former-employer or real customer data.
3. **Read-only analytics** — no automated trading or high-impact financial actions.
4. **One reliable investigation loop before feature expansion.**
5. **LLM = planner/orchestrator; Python/SQL = calculator.**
6. **Reproducible benchmark data from a fixed random seed.**
7. **Unsupported evidence must remain unsupported** — the system should be able to say it does not know.

## Safety and compliance

Do not commit:

- API keys;
- customer PII;
- confidential CRM exports;
- former-employer internal data;
- non-public trading or transaction records.

FitzSight is an analytical decision-support prototype. It is **not** an investment adviser, trading engine, AML enforcement system, credit decision system, or automated compliance decision-maker.

## Limitations

v0.3 deliberately has a narrow scope:

- the deterministic investigation engine currently recognizes one benchmark intent;
- the benchmark uses synthetic data and does not prove real-world causal validity;
- the preferred DuckDB backend requires the `duckdb` dependency; restricted build environments may use SQLite fallback;
- SQL safety is conservative and intentionally rejects some otherwise valid read-only SQL patterns;
- evidence IDs prove traceability to tool outputs, not truthfulness of the underlying source data;
- no LLM is used in v0.3, so natural-language question coverage is intentionally limited;
- contribution decomposition explains observed metric movement but does not independently establish causality;
- anomaly flags only indicate unusual values relative to the configured baseline.

## Documentation

- `MASTER_PLAN.md` — competition/product master plan
- `IMPLEMENTATION_STATUS.md` — implementation snapshot
- `docs/ARCHITECTURE.md` — current architecture
- `docs/TOOL_LAYER.md` — core Tool Layer specification
- `docs/DIAGNOSTIC_TOOLS.md` — v0.3 contribution/anomaly diagnostics
- `docs/BASELINE_RESULTS.md` — original synthetic baseline
- `docs/V0.2_VALIDATION.md` — v0.2 validation evidence
- `docs/V0.3_VALIDATION.md` — v0.3 validation evidence
- `docs/V0.3_SAMPLE_INVESTIGATION.json` — deterministic v0.3 output sample
- `PROJECT_PROGRESS.md` — pointer to the external progress source of truth

## Progress source of truth

Project progress is maintained outside this implementation repository:

- Tracker: https://neutriverse.uk/projfitzgerald/
- Source document: https://neutriverse.uk/docs/PROJFITZGERALD_PROGRESS.md
- Source repository: https://github.com/AplusNeutrino/My_Blog

## License

A final project license is intentionally deferred until competition submission and third-party dependency requirements are rechecked.
