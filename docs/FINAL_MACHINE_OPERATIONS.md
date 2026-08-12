# FitzSight Final-Machine Operations

FitzSight v0.11 adds a final-machine layer without changing the analytical core or the manual-submission boundary.

## One command

```bash
python scripts/final_machine_check.py --output final_machine_report.json
```

The default check is local-only except for the Streamlit health probe, which targets `127.0.0.1`. It does not access the GOAI portal, Gmail/email, or an external account.

The OpenAI live planner is never called by the default command. It requires the explicit `--include-openai` flag plus deliberately configured credentials/model access.

## Portable kit

`submission/FitzSight_Final_Machine_Kit.zip` is a standalone presentation-machine packet containing the executable FitzSight source/runtime entry points, verified offline assets, the manual handoff packet, and Windows/POSIX launchers.

## Rehearsal evidence

`scripts/rehearsal_assistant.py` records timing evidence locally. A generated timing report is not treated as proof of a rehearsal unless the user actually performed or measured that rehearsal.

## Remaining external/manual truth

The following cannot be closed by local code presence:

- final-machine Streamlit live validation;
- optional OpenAI live provider validation;
- actual GOAI portal upload/final submit/confirmation;
- real timed pitch/demo/Q&A rehearsal.
