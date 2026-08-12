# FitzSight — Runtime Validation for the Final Machine

These checks are separate from portal submission. They require the environment in which you will actually present FitzSight.

## 1. General readiness

```bash
python scripts/runtime_doctor.py
```

Expected core state: deterministic demo ready. DuckDB was already validated in a deployment environment.

## 2. Streamlit live path

Install the optional UI dependency if needed:

```bash
pip install -e ".[ui]"
```

Then run:

```bash
python scripts/validate_streamlit_runtime.py
```

Only a real health-check PASS on this machine is valid evidence for closing the Streamlit live-runtime task.

If it fails, do not improvise a new analytical path. Use:

```bash
python scripts/start_demo.py --mode cli --backend auto
```

or open:

```text
submission/FitzSight_Offline_Demo.html
submission/FitzSight_Offline_Demo_Backup.mp4
```

## 3. OpenAI planner — optional

This path is not required for the deterministic competition fallback.

Only if you intentionally configure stable credentials and a model available to your account:

```bash
pip install -e ".[openai]"
export OPENAI_API_KEY="..."
export FITZSIGHT_MODEL="..."
python scripts/validate_openai_runtime.py
```

Do not paste API keys into screenshots, logs, tickets, emails, or repository files.

## 4. What to report back if you want the tracker updated

For Streamlit, provide the validator's final status/output.

For OpenAI, provide the validator result and non-secret telemetry only, such as:

- requested/returned model;
- response ID if safe to retain;
- token counts;
- planning latency;
- final Agent verification status.

Never provide the API key.
