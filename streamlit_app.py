from __future__ import annotations

from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd
import streamlit as st

from fitzsight.agent.planner import ConstrainedRulePlanner
from fitzsight.providers.openai_planner import OpenAIResponsesPlanner
from fitzsight.runtime import build_agent_runtime


CRM_QUESTION = "Why did European FTD conversion deteriorate after July 15?"
NET_QUESTION = "Why did European net deposits fall in the week starting August 3?"
SEGMENT_QUESTION = (
    "How are European customer segments distributed by behavioral value, "
    "and which segment contributes most to deposits?"
)


def money(value: float) -> str:
    sign = "-" if value < 0 else ""
    return f"{sign}${abs(value):,.0f}"


def render_business_kpis(intent: str, metrics: dict, backend: str, verification: dict) -> None:
    st.subheader("Business KPIs")
    if intent == "crm_routing_ftd_investigation":
        cols = st.columns(5)
        cols[0].metric("FTD change", f"{metrics['affected']['conversion_change_pp']:.2f} pp")
        cols[1].metric("Europe control", f"{metrics['control']['conversion_change_pp']:.2f} pp")
        cols[2].metric("Response median", f"{metrics['affected_response_median_change_minutes']:+.2f} min")
        cols[3].metric("Anomaly days", metrics['post_change_response_anomalies']['anomaly_count'])
        cols[4].metric("Verified claims", f"{verification['verified_claims']}/{verification['total_claims']}")
    elif intent == "net_deposit_anomaly_investigation":
        driver = metrics["driver_decomposition"]
        concentration = metrics["customer_concentration"]
        cols = st.columns(5)
        cols[0].metric("Net-deposit change", money(driver["net_change"]))
        cols[1].metric("Deposit change", money(driver["deposit_change"]))
        cols[2].metric("Withdrawal change", money(driver["withdrawal_change"]))
        cols[3].metric("Top-11 withdrawal share", f"{concentration['share_of_current_withdrawals']:.1%}")
        cols[4].metric("Verified claims", f"{verification['verified_claims']}/{verification['total_claims']}")
    elif intent == "customer_intelligence_segmentation":
        segmentation = metrics["segmentation"]
        cols = st.columns(5)
        cols[0].metric("Customers segmented", f"{segmentation['customer_count']:,}")
        cols[1].metric("Coverage", f"{segmentation['coverage']:.0%}")
        cols[2].metric("Value groups", segmentation["segment_count"])
        cols[3].metric("Top deposit segment", segmentation["top_deposit_segment"])
        cols[4].metric("Top segment deposit share", f"{segmentation['top_deposit_segment_share']:.1%}")
    st.caption(f"Backend: {backend} · all displayed KPIs come from verified investigation output.")


def render_charts(intent: str, metrics: dict) -> None:
    st.subheader("Verified charts")
    if intent == "crm_routing_ftd_investigation":
        rows = metrics["team_contribution_analysis"]["segments"]
        chart = pd.DataFrame(
            {
                "team": [row["segment"] for row in rows],
                "FTD contribution (pp)": [row["total_contribution_pp"] for row in rows],
            }
        ).set_index("team")
        st.bar_chart(chart)
        st.caption("Symmetric team-level decomposition of the Europe-wide FTD-rate movement.")
    elif intent == "net_deposit_anomaly_investigation":
        periods = metrics["periods"]
        chart = pd.DataFrame(
            {
                "Baseline": [
                    periods["baseline"]["deposits"],
                    periods["baseline"]["withdrawals"],
                    periods["baseline"]["net_deposits"],
                ],
                "Current": [
                    periods["current"]["deposits"],
                    periods["current"]["withdrawals"],
                    periods["current"]["net_deposits"],
                ],
            },
            index=["Deposits", "Withdrawals", "Net deposits"],
        )
        st.bar_chart(chart)
        st.caption("Baseline vs current weekly money-flow totals from the verified result.")
    elif intent == "customer_intelligence_segmentation":
        rows = metrics["segmentation"]["profiles"]
        chart = pd.DataFrame(
            {
                "segment": [row["segment"] for row in rows],
                "Deposit share": [row["deposit_share"] for row in rows],
                "Withdrawal share": [row["withdrawal_share"] for row in rows],
            }
        ).set_index("segment")
        st.bar_chart(chart)
        st.caption("Descriptive segment shares only; not a credit, AML or eligibility score.")


def render_trace(plan: dict, verification: dict) -> None:
    st.subheader("Investigation trace")
    rows = []
    for step in plan["steps"]:
        rows.append(
            {
                "Step": step["step_id"],
                "Action": step["action"],
                "Purpose": step["purpose"],
                "Policy": "approved",
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.caption(
        f"Verifier result: {'PASS' if verification['passed'] else 'FAIL'} · "
        f"{verification['verified_claims']}/{verification['total_claims']} claims verified."
    )


def render_evidence_cards(records: list[dict]) -> None:
    st.subheader("Evidence cards")
    st.caption(f"{len(records)} append-only audit records")
    for record in records:
        label = f"{record['evidence_id']} · {record['tool_name']} · {record['status']}"
        with st.expander(label, expanded=False):
            st.caption(f"Digest: {record['result_digest']}")
            if record.get("parameters"):
                st.markdown("**Parameters**")
                st.json(record["parameters"])
            st.markdown("**Result**")
            st.json(record.get("result"))


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
    [CRM_QUESTION, NET_QUESTION, SEGMENT_QUESTION, "Custom"],
    horizontal=False,
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
    intent = result["plan"]["intent"]

    if final["status"] == "verified":
        st.success(final["headline"])
    else:
        st.error(final["headline"])

    render_business_kpis(intent, investigation["metrics"], runtime_backend, verification)
    render_charts(intent, investigation["metrics"])

    st.subheader("Verified findings")
    for finding in final["findings"]:
        st.markdown(f"- {finding}")

    if final["guardrail"]:
        st.info(final["guardrail"])

    render_trace(result["plan"], verification)
    render_evidence_cards(result["audit_evidence"])

    with st.expander("Raw verified metrics", expanded=False):
        st.json(investigation["metrics"])

    st.caption(
        "Decision support only. FitzSight does not provide investment advice, "
        "automated compliance conclusions, credit decisions, or high-impact account actions."
    )
