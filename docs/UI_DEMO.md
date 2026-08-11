# FitzSight v0.7 Streamlit Demo

`streamlit_app.py` is a presentation layer over the verified Agent result.

## Preset workflows

1. CRM / FTD investigation
2. Net-deposit investigation
3. Customer Intelligence / segmentation
4. Americas marketing lead quality
5. Asia false-correlation guardrail

A custom text box is also exposed, but the local intent gate rejects questions outside the approved catalog.

## Presentation components

- backend selector;
- deterministic/OpenAI planner selector;
- question input;
- verified headline;
- business KPI cards;
- intent-specific charts;
- verified findings;
- guardrail text;
- investigation-plan trace table;
- Evidence cards with ID/tool/status/digest;
- raw verified metrics expander.

## Trust boundary

The UI does not independently compute KPI definitions, statistical tests, contribution analysis, segmentation, or evidence status. It renders values already produced and verified by the Agent runtime.

## Runtime state

Code and compile validation are complete. A real Streamlit runtime smoke test remains required under the External Runtime Evidence rule before UI runtime tasks can be marked fully done.

```bash
pip install -e ".[ui]"
streamlit run streamlit_app.py
```
