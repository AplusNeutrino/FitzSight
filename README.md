# FitzSight

**Evidence-grounded Financial Operations Intelligence Agent**

FitzSight is a GOAI 2026 · Boundless Agents · AI+金融 project focused on a practical analytical question:

> **Why did this financial-operations metric change?**

The project does not ask an LLM to invent an explanation. It separates planning from calculation and verification:

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

## Current release: v0.10.0

v0.10 is the **operator handoff layer**. It keeps the five-intent analytical core unchanged and makes the boundary explicit: FitzSight automation prepares, validates, hashes, and packages all local competition assets, while the actual GOAI portal submission and confirmation workflow is user-manual only. A portable handoff ZIP, field map, manual checklist, runtime checklist, and machine-readable readiness report are generated so the user can take over without additional code work.

## Supported workflows

### 1. CRM / FTD deterioration

```text
Why did European FTD conversion deteriorate after July 15?
```

Fixed-seed benchmark:

```text
affected FTD change:      -7.53 pp
control FTD change:       -1.21 pp
response median change:  +29.15 min
verification:             PASS
```

### 2. Net-deposit deterioration

```text
Why did European net deposits fall in the week starting August 3?
```

Fixed-seed benchmark:

```text
net-deposit change:      -$187,790.90
deposit change:          +$59,158.18
withdrawal change:       +$246,949.08
top-11 withdrawal share:  91.6%
verification:             PASS
```

The Agent reports withdrawal concentration as an observed driver. It does not infer why individual customers withdrew.

### 3. Customer Intelligence

```text
How are European customer segments distributed by behavioral value,
and which segment contributes most to deposits?
```

Fixed-seed benchmark:

```text
European customers:          6,770
coverage:                     100%
value groups:                 4
High Value customer share:    3.7%
High Value deposit share:     53.7%
verification:                 5 / 5 PASS
```

The segmentation is descriptive operational analytics only. It is not a credit, AML, suitability, eligibility, or adverse-action system.

### 4. Marketing lead quality

```text
Why did Americas lead volume rise while FTD conversion fell after June 15?
```

The synthetic campaign benchmark deliberately creates **more leads but lower acquisition quality**.

```text
lead volume change:        +838 (+315.0%)
FTD conversion change:     -10.84 pp
Paid Search mix change:    +60.52 pp
Paid Search conversion:    -16.44 pp
Paid Search p-value:       4.43e-05
verification:              4 / 4 PASS
```

FitzSight distinguishes volume, mix, and within-channel performance instead of treating “more leads” as equivalent to “better performance.”

### 5. False-correlation guardrail

```text
Why did Asia FTD conversion fall after July 20,
and is the nearby office relocation the cause?
```

This benchmark puts an unrelated office-relocation event next to a real Affiliate conversion deterioration.

```text
Asia conversion change:              -8.13 pp
Affiliate conversion change:        -15.81 pp
Affiliate p-value:                    0.00463
top negative performance channel:     Affiliate
nearby office-event causal support:   false
false correlation rejected:           true
verification:                         4 / 4 PASS
```

Temporal proximity alone is not accepted as causal evidence.

---

## Why FitzSight is not “chat with CSV”

A supported answer requires all of the following:

1. the question matches an approved business intent;
2. the planner emits only the exact approved high-level action sequence;
3. SQL/Python tools calculate every numeric result;
4. supported claims reference Evidence IDs;
5. the verifier checks evidence integrity, policy boundaries, and causal wording;
6. failed verification causes the final answer to be withheld.

The model, when enabled, is a constrained planner—not a calculator and not an unrestricted SQL agent.

---

## Quick start

Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python scripts/generate_data.py
```

One-command competition demo:

```bash
python scripts/start_demo.py
```

`auto` mode launches Streamlit when the optional UI dependency is installed and otherwise falls back to the deterministic CLI. Explicit modes are also available:

```bash
python scripts/start_demo.py --mode ui --backend duckdb
python scripts/start_demo.py --mode cli --backend duckdb
```

Run any supported workflow directly:

```bash
python scripts/agent_investigate.py \
  --backend duckdb \
  --question "Why did European FTD conversion deteriorate after July 15?"
```

```bash
python scripts/agent_investigate.py \
  --backend duckdb \
  --question "Why did Americas lead volume rise while FTD conversion fell after June 15?"
```

```bash
python scripts/agent_investigate.py \
  --backend duckdb \
  --question "Why did Asia FTD conversion fall after July 20, and is the nearby office relocation the cause?"
```

Run the full deterministic benchmark:

```bash
python scripts/run_benchmark.py --backend duckdb
```

Run the adversarial safety/evidence suite:

```bash
python scripts/run_adversarial_evaluation.py --backend duckdb
```

Run tests:

```bash
pytest -q
```

---

## Benchmark and evaluation

The current benchmark catalog contains five deterministic business scenarios.

Current SQLite build result:

```text
scenario count:                       5
passed:                               5
failed:                               0
scenario pass rate:                   100%
root-cause scenario accuracy:         100%
false-correlation rejection accuracy: 100%
mean evidence coverage:               100%
verifier violations:                  0
```

The benchmark also records deterministic end-to-end latency. Latency is environment-specific and is not presented as a production guarantee.

Evaluation artifacts:

- `evaluation/benchmark_catalog.json`
- `evaluation/adversarial_cases.json`
- `scripts/run_benchmark.py`
- `scripts/run_adversarial_evaluation.py`
- `docs/V0.7_BENCHMARK_RESULTS.json`
- `docs/V0.7_ADVERSARIAL_RESULTS.json`
- `docs/V0.7_VALIDATION.md`
- `docs/V0.8_VALIDATION.md`
- `docs/V0.8_SUBMISSION_PREFLIGHT.json`
- `docs/V0.10_BENCHMARK_RESULTS.json`
- `docs/V0.10_ADVERSARIAL_RESULTS.json`
- `docs/V0.9_DETERMINISTIC_LATENCY.json`
- `docs/V0.9_RUNTIME_STATUS.json`
- `docs/OPERATOR_BOUNDARY.md`
- `docs/V0.10_HANDOFF_READINESS.json`
- `docs/V0.10_SUBMISSION_PREFLIGHT.json`
- `docs/V0.10_VALIDATION.md`

### Adversarial release gate

The eight-case adversarial suite checks:

- unsupported trading actions are refused;
- unsupported AML/account-freeze requests are refused;
- planner SQL injection is rejected;
- planner high-impact actions are rejected;
- missing Evidence IDs are rejected;
- causal overclaim wording is rejected;
- evaluation-only `_gt` SQL leakage is rejected;
- a nearby-but-unrelated event is not promoted to a cause.

Current result:

```text
8 / 8 PASS
all category catch/refusal rates: 100%
```

---

## Planner safety policy

Planner/model output is untrusted input.

The planner may only return one published intent and that intent's exact approved action sequence. It may not:

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
- enforces bounded output;
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

## Initial-round submission assets

The repository now contains a reproducible competition-facing asset bundle:

```text
submission/
├── FitzSight_GOAI_Initial_Round.pptx
├── FitzSight_GOAI_Initial_Round.pdf
├── DEMO_RUNBOOK.md
├── PITCH_SPEAKER_NOTES.md
├── SUBMISSION_CHECKLIST.md
└── README.md
```

Regenerate the deck with:

```bash
pip install -e ".[submission]"
python scripts/build_pitch_deck.py
```

Run repository/submission preflight with:

```bash
python scripts/preflight_submission.py
```

Build the manual handoff packet with:

```bash
python scripts/build_manual_handoff.py
python scripts/handoff_readiness.py
```

The generated `submission/FitzSight_Manual_Handoff.zip` contains the copy-ready portal text, PPT/PDF, offline demo/video, compliance/evaluation summaries, and manual operator instructions. It performs **no network action and no external submission**.

### Manual submission boundary

By default, FitzSight/ChatGPT project automation does not open or submit the GOAI portal, access Gmail, send email, or modify external accounts. Those submission actions are explicitly user-controlled. See `docs/OPERATOR_BOUNDARY.md` and `submission/START_HERE_MANUAL.md`.

## Runtime validation status

### DuckDB — validated

A deployment environment has successfully executed the constrained planner and JSON-file planner using DuckDB and `data/generated`, with final status `verified`.

### OpenAI Responses planner — implemented, live runtime pending

Install the optional provider:

```bash
pip install -e ".[openai]"
export OPENAI_API_KEY="..."
export FITZSIGHT_MODEL="<model available to your account>"
```

The live provider is not marked validated until actual deployment output exists.

### Streamlit UI — implemented, runtime smoke test pending

```bash
pip install -e ".[ui]"
streamlit run streamlit_app.py
```

The current UI code contains five preset workflows, verified KPI cards, intent-specific charts, plan trace, evidence cards, and raw verified metrics. The UI renders verified Agent output and does not create a second analytical path.

---

## Synthetic-data and compliance policy

All benchmark data is synthetic.

Never add:

- real customer PII;
- former-employer CRM exports;
- confidential transaction data;
- internal sales reports;
- real API secrets.

The `_gt` fields used by synthetic benchmark construction are evaluation-only and must never be queried by the normal Agent workflow.

FitzSight is analytical decision support. It does not provide investment advice or automated high-impact financial/compliance decisions.

See `docs/COMPLIANCE_AND_SAFETY.md`.

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
│   ├── benchmark_catalog.json
│   └── adversarial_cases.json
├── scripts/
│   ├── generate_data.py
│   ├── agent_investigate.py
│   ├── run_benchmark.py
│   ├── run_adversarial_evaluation.py
│   ├── start_demo.py
│   ├── runtime_doctor.py
│   ├── validate_streamlit_runtime.py
│   ├── validate_openai_runtime.py
│   ├── build_offline_demo.py
│   ├── build_offline_demo_video.py
│   ├── measure_latency.py
│   ├── build_submission_bundle.py
│   ├── build_manual_handoff.py
│   ├── handoff_readiness.py
│   ├── preflight_submission.py
│   └── build_pitch_deck.py
├── submission/
│   ├── FitzSight_GOAI_Initial_Round.pptx
│   ├── FitzSight_GOAI_Initial_Round.pdf
│   ├── FitzSight_Offline_Demo.html
│   ├── FitzSight_Offline_Demo_Backup.mp4
│   ├── FitzSight_GOAI_Upload_Bundle.zip
│   ├── FitzSight_Manual_Handoff.zip
│   ├── START_HERE_MANUAL.md
│   ├── MANUAL_SUBMISSION_CHECKLIST.md
│   ├── RUNTIME_VALIDATION_FOR_USER.md
│   └── ...
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

Key competition/evaluation files:

- `src/fitzsight/investigation/lead_quality.py`
- `evaluation/adversarial_cases.json`
- `scripts/run_adversarial_evaluation.py`
- `docs/BENCHMARK_SCENARIOS.md`
- `docs/ADVERSARIAL_EVALUATION.md`
- `docs/COMPLIANCE_AND_SAFETY.md`
- `docs/V0.7_VALIDATION.md`
- `docs/V0.8_VALIDATION.md`
- `docs/V0.8_SUBMISSION_PREFLIGHT.json`
- `docs/V0.10_BENCHMARK_RESULTS.json`
- `docs/V0.10_ADVERSARIAL_RESULTS.json`
- `docs/V0.9_DETERMINISTIC_LATENCY.json`
- `docs/V0.9_RUNTIME_STATUS.json`
- `docs/OPERATOR_BOUNDARY.md`
- `docs/V0.10_HANDOFF_READINESS.json`
- `docs/V0.10_SUBMISSION_PREFLIGHT.json`
- `docs/V0.10_VALIDATION.md`

---

## Validation snapshot

Current v0.9 release-gate state:

```text
5 / 5 deterministic benchmark scenarios PASS
8 / 8 adversarial cases PASS
mean evidence coverage 100%
verifier violations 0

offline deterministic demo: 5 / 5 verified workflows
offline MP4 backup: generated from verified outputs
submission PPTX/PDF: generated from fresh verified Agent metrics
```

Build-environment Streamlit/OpenAI live checks remain explicitly separate from implementation tests. DuckDB was previously validated in the deployment environment; the build sandbox may still skip its integration test when the dependency is absent.

---

## License

MIT. See `LICENSE`.

Third-party dependencies remain subject to their own licenses; see `THIRD_PARTY_NOTICES.md`.

## Progress source of truth

Project status is maintained in:

```text
AplusNeutrino/My_Blog/docs/PROJFITZGERALD_PROGRESS.md
```

Repository implementation evidence and tests determine whether tracker tasks may be marked `done`.
