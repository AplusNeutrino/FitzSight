# Streamlit Demo Shell

Run:

```bash
pip install -e ".[ui]"
streamlit run streamlit_app.py
```

The v0.5 UI is intentionally minimal.

It currently supports:

- CRM/FTD preset question;
- net-deposit preset question;
- deterministic/OpenAI planner choice;
- auto/DuckDB/SQLite backend choice;
- verification score;
- verified findings;
- guardrail display;
- plan JSON;
- metrics JSON;
- evidence/audit trace.

It does not yet include the final GOAI visual design, KPI business cards, charts, or animated real-time investigation trace.

Those remain subsequent UI tasks.
