# FitzSight v0.6 Streamlit Demo

`streamlit_app.py` is a presentation layer over the verified Agent result.

## Preset workflows

1. CRM / FTD investigation
2. Net-deposit investigation
3. Customer Intelligence / segmentation

A custom text box is also exposed, but the local intent gate rejects questions outside the approved catalog.

## v0.6 presentation components

- backend selector;
- deterministic/OpenAI planner selector;
- question input;
- verified headline;
- business KPI cards;
- intent-specific bar charts;
- verified findings;
- guardrail text;
- investigation-plan trace table;
- Evidence cards with ID/tool/status/digest;
- raw verified metrics expander.

## Trust boundary

The UI does not independently compute KPI definitions, statistical tests, contribution analysis, segmentation, or evidence status. It renders values already produced and verified by the Agent runtime.

## Runtime state

Code and compile validation are complete. A real Streamlit runtime smoke test remains required under the project External Runtime Evidence rule before the tracker task can be marked fully done.

Run after installing the optional UI dependency:

```bash
pip install -e ".[ui]"
streamlit run streamlit_app.py
```
