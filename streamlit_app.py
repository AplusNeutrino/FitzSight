from __future__ import annotations

from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd
import streamlit as st

from fitzsight.agent.planner import ConstrainedRulePlanner
from fitzsight.demo import DEMO_QUESTIONS
from fitzsight.providers.openai_planner import OpenAIResponsesPlanner
from fitzsight.runtime import build_agent_runtime
from fitzsight.ui.presenter import PresentationView, build_presentation


def render_business_kpis(view: PresentationView) -> None:
    st.subheader("Business KPIs")
    cols = st.columns(len(view.kpis))
    for column, card in zip(cols, view.kpis, strict=True):
        column.metric(card.label, card.value)
    st.caption(
        f"Backend: {view.backend} · all displayed KPIs come from verified investigation output."
    )


def render_chart(view: PresentationView) -> None:
    st.subheader("Verified chart")
    chart = view.chart
    frame = pd.DataFrame(
        {series.label: list(series.values) for series in chart.series},
        index=list(chart.categories),
    )
    st.markdown(f"**{chart.title}**")
    st.bar_chart(frame)
    st.caption(chart.caption)


def render_trace(view: PresentationView) -> None:
    st.subheader("Investigation trace")
    frame = pd.DataFrame(
        [
            {
                "Step": row.step,
                "Action": row.action,
                "Purpose": row.purpose,
                "Policy": row.policy,
            }
            for row in view.trace
        ]
    )
    st.dataframe(frame, use_container_width=True, hide_index=True)
    st.caption(
        f"Verifier result: {'PASS' if view.verification_passed else 'FAIL'} · "
        f"{view.verified_claims}/{view.total_claims} claims verified."
    )


def render_evidence_cards(view: PresentationView) -> None:
    st.subheader("Evidence cards")
    st.caption(f"{len(view.evidence_cards)} append-only audit records")
    for record in view.evidence_cards:
        label = f"{record.evidence_id} · {record.tool_name} · {record.status}"
        with st.expander(label, expanded=False):
            st.caption(f"Digest: {record.result_digest}")
            if record.parameters:
                st.markdown("**Parameters**")
                st.json(record.parameters)
            st.markdown("**Result**")
            st.json(record.result)


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

labels = list(DEMO_QUESTIONS)
preset_label = st.radio(
    "Demo workflow",
    labels + ["Custom"],
    horizontal=False,
)
question = (
    st.text_area("Question", height=90)
    if preset_label == "Custom"
    else st.text_area("Question", value=DEMO_QUESTIONS[preset_label], height=90)
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
            view = build_presentation(result, backend=store.backend)
        finally:
            store.close()
    except Exception as exc:
        st.error(f"{type(exc).__name__}: {exc}")
        st.stop()

    if view.status == "verified":
        st.success(view.headline)
    else:
        st.error(view.headline)

    render_business_kpis(view)
    render_chart(view)

    st.subheader("Verified findings")
    for finding in view.findings:
        st.markdown(f"- {finding}")

    if view.guardrail:
        st.info(view.guardrail)

    render_trace(view)
    render_evidence_cards(view)

    with st.expander("Raw verified metrics", expanded=False):
        st.json(result["investigation"]["metrics"])

    st.caption(
        "Decision support only. FitzSight does not provide investment advice, "
        "automated compliance conclusions, credit decisions, or high-impact account actions."
    )
