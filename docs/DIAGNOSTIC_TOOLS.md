# FitzSight Diagnostic Tools — v0.3

Version: `0.3.0`

v0.3 adds two deterministic diagnostic tools above the v0.2 read-only SQL/statistics layer. Both tools emit Evidence IDs and are usable without an LLM.

## 1. ContributionAnalysisTool

File: `src/fitzsight/tools/contribution.py`

Purpose: explain an aggregate binary-rate change by a categorical dimension without treating raw subgroup rate changes as additive contributions.

Current method: **symmetric rate decomposition**.

For segment `i`, with population share `w` and rate `r`:

```text
performance_i = ((w0_i + w1_i) / 2) * (r1_i - r0_i)
composition_i = ((r0_i + r1_i) / 2) * (w1_i - w0_i)
contribution_i = performance_i + composition_i
```

The segment contributions reconstruct the aggregate rate change up to floating-point error.

Current benchmark use:

```text
Europe FTD conversion
pre 2026-07-15 vs post 2026-07-15
↓
decompose by assigned_team
```

The default synthetic benchmark identifies Team A and Team B as the largest negative contributors.

### Guardrail

A contribution is a mathematical decomposition of observed metric change. It does **not** independently establish causality.

## 2. AnomalyDetectionTool

File: `src/fitzsight/tools/anomaly.py`

Purpose: detect unusually high/low current values relative to a historical baseline using a transparent robust rule.

Current method:

```text
center = median(baseline)
scale  = 1.4826 × MAD(baseline)
robust_z = (value - center) / scale
```

If MAD is zero, FitzSight falls back to sample standard deviation; a final unit-scale fallback prevents division by zero for a perfectly constant baseline.

Supported directions:

- `high`
- `low`
- `two_sided`

Current benchmark use:

```text
pre-change daily median response time
↓ establishes robust baseline
post-change daily median response time
↓
high-anomaly scan
```

### Guardrail

Anomaly status means “unusual relative to the configured baseline.” It is not automatically a risk, fraud, compliance, or causal conclusion.

## 3. Evidence behavior

Each diagnostic execution records:

- Evidence ID;
- tool name;
- parameters;
- result digest;
- status;
- result payload.

Contribution analysis also retains the Evidence IDs of the underlying SQL queries.

## 4. Current deterministic investigation

The v0.3 investigation sequence is:

```text
Schema
→ affected cohort SQL
→ control cohort SQL
→ statistical tests
→ team contribution decomposition
→ response-time anomaly scan
→ business-event check
→ evidence/causal boundary
```

The LLM layer remains intentionally absent at this stage.
