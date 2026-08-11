# FitzSight

**Evidence-grounded Financial Operations Intelligence Agent**

FitzSight is a GOAI 2026 · Boundless Agents · AI+金融 project focused on a specific operational problem:

> **Turn a financial-operations question into a reproducible investigation with traceable evidence.**

Instead of asking an LLM to invent an explanation, FitzSight separates planning from calculation:

```text
Business question
        ↓
Local approved-intent gate
        ↓
Constrained planner
        ↓
Deterministic SQL / Python tools
        ↓
Evidence Registry
        ↓
EvidenceClaimVerifier
        ↓
Verified decision-support answer
```

## Current release: v0.6.0

v0.6 adds the third supported workflow—deterministic Customer Intelligence / behavioral segmentation—and expands the benchmark/evaluation layer while preserving the same evidence-first architecture.

### Supported workflow 1 — CRM / FTD investigation

```text
Why did European FTD conversion deteriorate after July 15?
```

FitzSight checks:

- affected vs control conversion;
- response-time movement;
- statistical significance;
- team contribution decomposition;
- daily response anomalies;
- nearby operational events;
- causal-language boundaries.

Fixed-seed benchmark:

```text
affected FTD change:      -7.53 pp
control FTD change:       -1.21 pp
response median change:  +29.15 min
verification:             PASS
```

### Supported workflow 2 — Net-deposit investigation

```text
Why did European net deposits fall in the week starting August 3?
```

FitzSight measures:

- baseline/current deposits;
- baseline/current withdrawals;
- exact net-deposit driver decomposition;
- top-customer withdrawal concentration;
- regional control movement;
- nearby operational events;
- boundary between observed drivers and unsupported customer-motive claims.

Fixed-seed benchmark:

```text
net-deposit change:      -$223,901.70
deposit change:          +$24,365.52
withdrawal change:       +$248,267.22
top-11 withdrawal share:  92.2%
verification:             PASS
```

### Supported workflow 3 — Customer Intelligence

```text
How are European customer segments distributed by behavioral value,
and which segment contributes most to deposits?
```

FitzSight builds observable customer behavior features and applies the transparent `behavioral_value_score_v1` policy. It never uses the hidden synthetic `customer_segment_gt` field during normal Agent execution.

Fixed-seed benchmark:

```text
European customers:          6,770
coverage:                     100%
value groups:                 4
High Value customers:          278 (4.1%)
High Value deposit share:     55.8%
High Value withdrawal share:  61.0%
verification:                 5 / 5 PASS
```

Customer segments are descriptive operational analytics only. They are not credit, AML, suitability, eligibility, or adverse-action decisions.

---

## Why FitzSight is not “chat with CSV”

A chat interface is not the core product. FitzSight requires:

1. a locally recognized approved business intent;
2. an approved high-level investigation plan;
3. deterministic tool execution;
4. Evidence IDs for supported factual claims;
5. verification of evidence integrity and causal wording;
6. fail-closed output if verification fails.

The model, when enabled, is a constrained planner—not a calculator and not an unrestricted SQL agent.

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
  --backend duckdb \
  --question "Why did European FTD conversion deteriorate after July 15?"
```

Net-deposit workflow:

```bash
python scripts/agent_investigate.py \
  --backend duckdb \
  --question "Why did European net deposits fall in the week starting August 3?"
```

Customer Intelligence workflow:

```bash
python scripts/agent_investigate.py \
  --backend duckdb \
  --question "How are European customer segments distributed by behavioral value, and which segment contributes most to deposits?"
```

Run the three-scenario benchmark catalog:

```bash
python scripts/run_benchmark.py --backend duckdb
```

Run tests:

```bash
pytest -q
```

---

## Runtime validation status

### DuckDB — validated

A deployment environment has successfully executed both:

- the default constrained planner; and
- the JSON-file structured planner

using DuckDB and `data/generated`, with final status `verified`.

### OpenAI Responses planner — implemented, live runtime still pending

The optional provider adapter uses strict structured planner output while preserving the local scope gate and plan validator.

Install:

```bash
pip install -e ".[openai]"
export OPENAI_API_KEY="..."
export FITZSIGHT_MODEL="<model available to your account>"
```

Then:

```bash
python scripts/agent_investigate.py \
  --backend duckdb \
  --planner openai \
  --question "Why did European net deposits fall in the week starting August 3?"
```

A real provider call is not treated as validated until actual deployment output exists.

### Streamlit UI — implemented, runtime smoke test still pending

Install:

```bash
pip install -e ".[ui]"
```

or:

```bash
pip install -e ".[demo]"
```

Run:

```bash
streamlit run streamlit_app.py
```

v0.6 UI code contains:

- three preset workflows;
- backend/planner selector;
- verified business KPI cards;
- intent-specific charts;
- verified findings;
- explicit investigation-plan trace;
- evidence cards with ID/tool/status/digest;
- raw verified metrics.

The UI reads verified Agent outputs and does not recalculate business metrics.

---

## Customer Intelligence method

`CustomerSegmentationTool` uses observable features only:

- completed deposit value;
- trading volume;
- trading frequency;
- withdrawal behavior for descriptive profiling.

Active customers receive a transparent score:

```text
value_score =
    0.55 × deposit-value percentile
  + 0.30 × trade-volume percentile
  + 0.15 × trade-count percentile
```

Segments:

```text
High Value   score >= 0.75
Growth       0.50 <= score < 0.75
Core         score < 0.50 among active customers
Low Activity no completed deposit / withdrawal / trade activity
```

See `docs/CUSTOMER_INTELLIGENCE.md`.

---

## Benchmark and evaluation

v0.6 contains three deterministic benchmark workflows.

Current SQLite build result:

```text
scenario count:               3
passed:                       3
failed:                       0
scenario pass rate:           100%
root-cause scenario accuracy: 100%
mean evidence coverage:       100%
verifier violations:          0
```

The benchmark runner also records end-to-end deterministic latency. Latency values are environment-specific and are not production guarantees.

Evaluation artifacts:

- `evaluation/benchmark_catalog.json`
- `scripts/run_benchmark.py`
- `docs/V0.6_BENCHMARK_RESULTS.json`
- `docs/V0.6_VALIDATION.md`

---

## Planner safety policy

Planner/model output is untrusted input.

The planner may only return one published intent and that intent's exact approved action sequence.

It may not:

- produce SQL;
- choose arbitrary tables;
- submit free-form tool arguments;
- execute trades;
- transfer funds;
- freeze accounts;
- contact customers;
- create automated compliance conclusions;
- create credit/suitability decisions;
- make investment recommendations.

Unsupported questions fail before an external model invocation.

---

## SQL safety policy

The read-only SQL tool:

- accepts only `SELECT` / `WITH`;
- rejects multiple statements;
- rejects write/DDL/admin keywords;
- rejects external file/network scan functions;
- enforces a bounded row output;
- records successful and failed calls in the Evidence Registry.

---

## Evidence-first verification

For every supported claim, `EvidenceClaimVerifier` checks:

- referenced Evidence IDs exist;
- evidence digests still match;
- tool execution status is successful;
- supported claims have evidence;
- evaluation-only `*_gt` fields were not queried;
- guarded claims include a policy boundary;
- wording does not exceed the evidence status.

If verification fails:

```text
answer = withheld
```

---

## Synthetic-data and compliance policy

All benchmark data is synthetic.

Never add:

- real customer PII;
- former-employer CRM exports;
- confidential transaction data;
- internal sales reports;
- real API secrets.

The `_gt` fields used by the synthetic generator are evaluation-only and must never be queried by the normal Agent workflow.

FitzSight is analytical decision support. It does not provide investment advice or automated high-impact financial/compliance decisions.

---

## Repository structure

```text
FitzSight/
├── README.md
├── MASTER_PLAN.md
├── IMPLEMENTATION_STATUS.md
├── LICENSE
├── THIRD_PARTY_NOTICES.md
├── streamlit_app.py
├── evaluation/
│   └── benchmark_catalog.json
├── examples/
│   ├── valid_agent_plan.json
│   ├── valid_net_deposit_plan.json
│   └── valid_customer_intelligence_plan.json
├── scripts/
│   ├── generate_data.py
│   ├── agent_investigate.py
│   └── run_benchmark.py
├── src/fitzsight/
│   ├── agent/
│   ├── data/
│   ├── evidence/
│   ├── investigation/
│   ├── providers/
│   └── tools/
├── tests/
└── docs/
```

Key new v0.6 files:

- `src/fitzsight/tools/segmentation.py`
- `src/fitzsight/investigation/customer_intelligence.py`
- `docs/CUSTOMER_INTELLIGENCE.md`
- `docs/INITIAL_ROUND_PROJECT_SUMMARY.md`
- `docs/PITCH_DECK_CONTENT.md`
- `docs/V0.6_VALIDATION.md`

---

## Validation snapshot

Build sandbox:

```text
46 passed, 1 skipped
compileall PASS
3 / 3 benchmark scenarios PASS
```

The single build skip is the DuckDB-specific test because the sandbox lacks DuckDB; separate deployment evidence has already validated the DuckDB runtime path.

---

## License

MIT. See `LICENSE`.

Third-party dependencies remain subject to their own licenses; see `THIRD_PARTY_NOTICES.md`.

## Progress source of truth

Project status is maintained separately in:

```text
AplusNeutrino/My_Blog/docs/PROJFITZGERALD_PROGRESS.md
```

The published tracker reads that file. Repository implementation evidence and tests determine whether tracker tasks may be marked `done`.
