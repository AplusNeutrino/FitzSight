# FinSight

**Evidence-grounded Financial Operations Intelligence Agent**

FinSight is the implementation project for **GOAI 2026 · Boundless Agents · AI+金融**.

The system is designed to let a financial-operations manager ask **“Why did this business metric change?”** and receive a reproducible investigation based on real tool execution, statistics, and traceable evidence rather than unsupported LLM narrative.

## v0.1 implemented

- deterministic synthetic financial-operations dataset generator;
- customers, salespeople, sales activity, deposits, withdrawals, trades, business events;
- injected `CRM_ROUTING_CHANGE` ground-truth scenario;
- KPI helpers;
- before/after CRM routing baseline investigation;
- evidence-registry primitive;
- tests and data dictionary.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python scripts/generate_data.py
python scripts/run_baseline.py
pytest
```

Generated data is written to `data/generated/` and is ignored by Git.

## Current benchmark scenario

On **2026-07-15**, a synthetic CRM routing change affects European `Team A` and `Team B`:

```text
CRM routing change
      ↓
lead response time increases
      ↓
FTD conversion probability decreases
```

The baseline should detect deterioration in the affected cohort and a weaker/no corresponding shift in the European control cohort.

## Design principles

1. Evidence first — numeric claims come from deterministic tools.
2. Synthetic by default — never use former-employer or real customer data.
3. Read-only analytics — no automated trading or high-impact financial actions.
4. One reliable investigation loop before feature expansion.
5. LLM = planner/orchestrator; Python/SQL = calculator.
6. Reproducible benchmark data from a fixed random seed.

## Safety

Do not commit API keys, PII, confidential CRM exports, or non-public trading/transaction data. FinSight is an analytical decision-support prototype, not an investment adviser, trading engine, AML enforcement system, or automated compliance decision-maker.

See `MASTER_PLAN.md` for the full competition and product plan.
