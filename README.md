# FitzSight

**Evidence-grounded Financial Operations Intelligence Agent**

FitzSight is a GOAI 2026 · Boundless Agents · AI+金融 project focused on one question:

> **Why did this financial-operations metric change?**

Instead of letting an LLM invent an explanation, FitzSight separates reasoning from calculation:

```text
Business question
        ↓
Constrained planner
        ↓
Approved intent + approved action sequence
        ↓
Deterministic SQL / Python analysis
        ↓
Evidence Registry
        ↓
EvidenceClaimVerifier
        ↓
Verified decision-support answer
```

## Current release: v0.5.0

v0.5 turns the v0.4 single-intent Agent MVP into a **multi-intent financial-operations Agent** and adds an optional live OpenAI Responses planner plus a minimal Streamlit demo shell.

### Supported intent 1 — CRM / FTD investigation

Question:

```text
Why did European FTD conversion deteriorate after July 15?
```

The synthetic benchmark contains a CRM routing change affecting European Team A/B. FitzSight investigates:

- affected vs control conversion;
- response-time movement;
- statistical significance;
- team contribution decomposition;
- daily response anomalies;
- nearby operational events;
- causal-language boundaries.

### Supported intent 2 — Net-deposit investigation

Question:

```text
Why did European net deposits fall in the week starting August 3?
```

The v0.5 synthetic benchmark contains a concentrated European high-value withdrawal shock. FitzSight investigates:

- baseline vs current deposits;
- baseline vs current withdrawals;
- exact net-deposit driver decomposition;
- customer withdrawal concentration;
- Europe vs other-region control movement;
- nearby operational events;
- explicit boundary between an observed financial driver and an unsupported claim about customer motives.

Default-seed v0.5 benchmark result:

```text
CRM benchmark:
  affected FTD change:      -7.53 pp
  control FTD change:       -1.21 pp
  response median change:  +29.15 min
  verification:             PASS

Net-deposit benchmark:
  net-deposit change:      -$223,901.70
  deposit change:          +$24,365.52
  withdrawal change:       +$248,267.22
  top-11 withdrawal share:  92.2%
  verification:             PASS
```

These are **synthetic benchmark results**, not real-company performance data.

---

## Why FitzSight is not "chat with CSV"

A chat interface is not the core product.

FitzSight requires:

1. a recognized business intent;
2. an approved investigation plan;
3. actual tool execution;
4. evidence IDs for factual claims;
5. verification of evidence integrity and causal wording;
6. fail-closed output if verification fails.

The LLM, when enabled, is a planner—not a calculator and not an unrestricted SQL agent.

---

## Quick start

Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Generate synthetic data:

```bash
python scripts/generate_data.py
```

Run the reliable no-API Agent fallback:

```bash
python scripts/agent_investigate.py \
  --backend sqlite \
  --question "Why did European FTD conversion deteriorate after July 15?"
```

Second intent:

```bash
python scripts/agent_investigate.py \
  --backend sqlite \
  --question "Why did European net deposits fall in the week starting August 3?"
```

Run the two-scenario benchmark catalog:

```bash
python scripts/run_benchmark.py --backend sqlite
```

Run tests:

```bash
pytest -q
```

---

## DuckDB

DuckDB is the preferred competition backend.

```bash
pip install -e ".[dev]"
python scripts/agent_investigate.py --backend duckdb
```

A SQLite fallback remains available for restricted/offline environments.

---

## Optional OpenAI Responses planner

The core project does **not** require an external model.

To enable the optional OpenAI planner:

```bash
pip install -e ".[openai]"
export OPENAI_API_KEY="..."
export FITZSIGHT_MODEL="<your enabled model>"
```

Then:

```bash
python scripts/agent_investigate.py \
  --backend duckdb \
  --planner openai \
  --question "Why did European net deposits fall in the week starting August 3?"
```

The provider:

- uses the Responses API;
- requests strict JSON-schema output;
- sets `store=False`;
- is locally scope-gated before API invocation;
- cannot emit SQL or arbitrary tool arguments;
- remains subject to local plan validation.

No API key is ever committed to the repository.

---

## Streamlit demo

Install:

```bash
pip install -e ".[ui]"
```

or with both UI and model provider:

```bash
pip install -e ".[demo]"
```

Run:

```bash
streamlit run streamlit_app.py
```

The initial UI exposes:

- the two supported demo questions;
- planner/backend selection;
- verification status;
- verified findings;
- investigation plan;
- metrics;
- evidence/audit trace.

The UI is a demo shell, not yet the final competition interface.

---

## Planner safety policy

Model/planner output is treated as untrusted input.

The planner may only return one of the published intents and that intent's exact action sequence.

It may not:

- produce SQL;
- choose arbitrary tables;
- submit free-form tool arguments;
- execute trades;
- transfer funds;
- freeze accounts;
- contact customers;
- create compliance conclusions;
- make investment recommendations.

Unsupported questions fail before external model invocation.

---

## SQL safety policy

The read-only SQL tool:

- accepts only `SELECT` / `WITH`;
- rejects multi-statement SQL;
- rejects write/DDL/admin keywords;
- rejects external file/network scan functions;
- applies a bounded row limit;
- writes successful and failed calls to the Evidence Registry.

---

## Evidence-first verification

For every supported claim, `EvidenceClaimVerifier` checks:

- referenced Evidence IDs exist;
- evidence digests still match;
- tool execution status is successful;
- supported claims have evidence;
- evaluation-only `*_gt` fields were not queried;
- guarded claims include causal-language boundaries;
- wording does not exceed the evidence status.

If verification fails:

```text
answer = withheld
```

---

## Synthetic-data policy

All benchmark data is synthetic.

Never add:

- real customer PII;
- former-employer CRM exports;
- confidential transaction data;
- internal sales reports;
- real API secrets.

The `_gt` fields used by the benchmark generator are evaluation-only and must never be queried by the normal Agent workflow.

---

## Repository structure

```text
FitzSight/
├── README.md
├── MASTER_PLAN.md
├── IMPLEMENTATION_STATUS.md
├── streamlit_app.py
├── evaluation/
│   └── benchmark_catalog.json
├── examples/
│   ├── valid_agent_plan.json
│   └── valid_net_deposit_plan.json
├── scripts/
│   ├── generate_data.py
│   ├── agent_investigate.py
│   └── run_benchmark.py
├── src/fitzsight/
│   ├── agent/
│   │   ├── catalog.py
│   │   ├── planner.py
│   │   ├── orchestrator.py
│   │   └── verifier.py
│   ├── providers/
│   │   └── openai_planner.py
│   ├── investigation/
│   │   ├── engine.py
│   │   ├── net_deposit.py
│   │   └── router.py
│   ├── tools/
│   ├── evidence/
│   └── data/
└── tests/
```

---

## Current limitations

v0.5 remains intentionally constrained:

- only two approved business intents exist;
- all data is synthetic;
- the OpenAI provider code is integration-tested with a fake Responses client in the build environment, but a live API call requires user credentials;
- Streamlit code is syntax-validated in the build environment, but runtime validation requires the optional package;
- DuckDB runtime validation requires an environment with the dependency installed;
- customer segmentation is not yet integrated into the Agent;
- the benchmark catalog contains two scenarios, not the planned five;
- evidence traceability proves what the tools returned, not that an external real-world data source is intrinsically correct;
- observed drivers are not automatically causal explanations.

---

## Safety boundary

FitzSight is analytical decision support.

It is **not**:

- an investment adviser;
- an automated trading system;
- an AML enforcement engine;
- a credit-decision system;
- an automated compliance decision-maker.

High-impact actions remain outside the MVP.

---

## Documentation

- `MASTER_PLAN.md` — competition/product master plan
- `IMPLEMENTATION_STATUS.md` — current implementation snapshot
- `docs/ARCHITECTURE.md` — system architecture
- `docs/AGENT_LAYER.md` — constrained Agent policy
- `docs/MULTI_INTENT.md` — v0.5 intent catalog
- `docs/MODEL_PROVIDER.md` — optional OpenAI provider boundary
- `docs/V0.5_VALIDATION.md` — v0.5 validation evidence
- `evaluation/benchmark_catalog.json` — current benchmark catalog
- `PROJECT_PROGRESS.md` — pointer to the external progress truth source

---

## Progress source of truth

Project status is maintained in:

```text
AplusNeutrino/My_Blog/docs/PROJFITZGERALD_PROGRESS.md
```

The public tracker is:

```text
https://neutriverse.uk/projfitzgerald/
```

When implementation and tracker disagree, verified code/tests/commit evidence must be used to correct the tracker.

---

## License

Final open-source license selection remains pending competition/dependency review.
