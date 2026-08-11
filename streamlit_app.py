from __future__ import annotations

from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import streamlit as st

from fitzsight.agent.planner import ConstrainedRulePlanner
from fitzsight.providers.openai_planner import (
    OpenAIPlannerConfigurationError,
    OpenAIResponsesPlanner,
)
from fitzsight.runtime import build_agent_runtime


CRM_QUESTION = "Why did European FTD conversion deteriorate after July 15?"
NET_QUESTION = "Why did European net deposits fall in the week starting August 3?"

st.set_page_config(page_title="FitzSight", page_icon="FS", layout="wide")
st.title("FitzSight")
st.caption("Evidence-grounded Financial Operations Intelligence Agent")

with st.sidebar:
    st.subheader("Runtime")
    backend = st.selectbox("Data backend", ["auto", "duckdb", "sqlite"], index=0)
    planner_mode = st.selectbox(
        "Planner",
        ["Deterministic fallback", "OpenAI Responses"],
        index=0,
    )
    model = st.text_input(
        "OpenAI model",
        value=os.getenv("FITZSIGHT_MODEL", ""),
        disabled=planner_mode != "OpenAI Responses",
    )
    st.caption(
        "The model can only produce a constrained plan. SQL, statistics and numeric "
        "claims remain inside deterministic tools."
    )

preset = st.radio(
    "Demo question",
    [CRM_QUESTION, NET_QUESTION, "Custom"],
    horizontal=True,
)
question = (
    st.text_area("Question", height=90)
    if preset == "Custom"
    else st.text_area("Question", value=preset, height=90)
)

run = st.button("Investigate", type="primary")

if run:
    try:
        planner = (
            ConstrainedRulePlanner()
            if planner_mode == "Deterministic fallback"
            else OpenAIResponsesPlanner(model=model or None)
        )
        store, registry, agent = build_agent_runtime(
            data_dir=ROOT / "data" / "generated",
            backend=backend,
            planner=planner,
        )
        try:
            with st.spinner("Running constrained investigation..."):
                result = agent.run(question).to_dict()
            runtime_backend = store.backend
        finally:
            store.close()
    except Exception as exc:
        st.error(f"{type(exc).__name__}: {exc}")
        st.stop()

    final = result["final_answer"]
    verification = result["verification"]
    investigation = result["investigation"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Intent", result["plan"]["intent"])
    col2.metric(
        "Verification",
        f"{verification['verified_claims']}/{verification['total_claims']}",
    )
    col3.metric("Backend", runtime_backend)

    if final["status"] == "verified":
        st.success(final["headline"])
    else:
        st.error(final["headline"])

    st.subheader("Verified findings")
    for finding in final["findings"]:
        st.markdown(f"- {finding}")

    if final["guardrail"]:
        st.info(final["guardrail"])

    with st.expander("Investigation plan", expanded=False):
        st.json(result["plan"])

    with st.expander("Metrics", expanded=False):
        st.json(investigation["metrics"])

    with st.expander("Evidence / audit trace", expanded=False):
        st.write(f"{len(result['audit_evidence'])} evidence records")
        st.json(result["audit_evidence"])

    st.caption(
        "Decision support only. FitzSight does not provide investment advice, "
        "automated compliance conclusions, or high-impact account actions."
    )
