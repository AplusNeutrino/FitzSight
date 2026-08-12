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

## v0.12 hero process evidence

The CRM/FTD presentation trace now renders execution status, branch rationale and Evidence IDs when `investigation.execution_trace` is present. This makes the product process visible rather than showing only the final KPI answer.

For a deterministic judge-facing product-process screen that does not depend on live Streamlit availability, run:

```bash
python scripts/build_hero_evidence.py
```

Outputs:

- `docs/V0.12_HERO_RUN.json`
- `submission/FitzSight_Hero_Run_Evidence.html`
- `submission/FitzSight_Hero_Run_Evidence.png`

The PNG is rendered from the actual verified runtime JSON, not a manually authored analytical mock.
