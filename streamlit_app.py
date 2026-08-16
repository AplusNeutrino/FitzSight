from __future__ import annotations

from pathlib import Path
import os
import sys
from threading import Lock

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd
import streamlit as st

from fitzsight.agent.planner import ConstrainedRulePlanner
from fitzsight.demo import DEMO_QUESTIONS
from fitzsight.providers.deepseek_planner import DeepSeekChatPlanner
from fitzsight.runtime import build_agent_runtime
from fitzsight.ui.demo_config import ALLOWED_MODELS, OnlineDemoConfig, secret_value
from fitzsight.ui.presenter import PresentationView, build_presentation


def streamlit_secrets() -> dict[str, object]:
    try:
        return st.secrets.to_dict()
    except Exception:
        return {}


@st.cache_resource
def shared_live_budget() -> dict[str, object]:
    return {"used": 0, "lock": Lock()}


def reserve_live_call(limit: int) -> tuple[bool, int]:
    budget = shared_live_budget()
    lock = budget["lock"]
    with lock:
        used = int(budget["used"])
        if used >= limit:
            return False, 0
        used += 1
        budget["used"] = used
        return True, max(0, limit - used)


def global_calls_remaining(limit: int) -> int:
    budget = shared_live_budget()
    lock = budget["lock"]
    with lock:
        return max(0, limit - int(budget["used"]))


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
                "Status": row.status,
                "Why this branch": row.reason,
                "Evidence": ", ".join(row.evidence_ids),
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


def render_deepseek_telemetry(telemetry: dict[str, object] | None) -> None:
    if not telemetry:
        return
    safe_fields = {
        key: telemetry.get(key)
        for key in (
            "request_id",
            "requested_model",
            "response_model",
            "planning_seconds",
            "input_tokens",
            "output_tokens",
            "total_tokens",
            "thinking",
            "response_format",
            "intent",
        )
    }
    with st.expander("DeepSeek live request telemetry", expanded=False):
        st.json(safe_fields)
        st.caption("API keys, full prompts and reasoning content are never recorded here.")


st.set_page_config(page_title="FitzSight", page_icon="FS", layout="wide")
secrets = streamlit_secrets()
try:
    demo_config = OnlineDemoConfig.from_sources(secrets, os.environ)
except (TypeError, ValueError) as exc:
    st.error(f"Online demo configuration error: {exc}")
    st.stop()

deepseek_api_key = secret_value("DEEPSEEK_API_KEY", secrets, os.environ)
if "deepseek_live_calls" not in st.session_state:
    st.session_state.deepseek_live_calls = 0

st.title("FitzSight")
st.caption("Evidence-grounded Financial Operations Intelligence Agent")
if demo_config.public_demo:
    st.info(
        "Public competition demo · synthetic data only · bounded planning · "
        "deterministic calculations · human decision."
    )

with st.sidebar:
    st.subheader("Runtime")
    backend_options = ["auto", "duckdb", "sqlite"]
    backend = st.selectbox(
        "Data backend",
        backend_options,
        index=backend_options.index(demo_config.backend),
        disabled=demo_config.public_demo,
    )
    planner_options = ["Deterministic fallback", "DeepSeek V4"]
    planner_mode = st.selectbox(
        "Planner",
        planner_options,
        index=1 if deepseek_api_key else 0,
    )
    model_options = sorted(ALLOWED_MODELS)
    model = st.selectbox(
        "DeepSeek model",
        model_options,
        index=model_options.index(demo_config.default_model),
        disabled=planner_mode != "DeepSeek V4" or demo_config.public_demo,
    )
    st.caption(
        "The model can only produce a constrained plan. SQL, statistics and numeric "
        "claims remain inside deterministic tools."
    )
    if planner_mode == "DeepSeek V4":
        remaining = max(
            0,
            demo_config.max_live_calls_per_session
            - int(st.session_state.deepseek_live_calls),
        )
        if deepseek_api_key:
            global_remaining = global_calls_remaining(demo_config.max_live_calls_global)
            st.caption(
                f"Live calls remaining: {remaining} this session · "
                f"{global_remaining} in this app process"
            )
        else:
            st.warning("DEEPSEEK_API_KEY is not configured in server-side secrets.")

labels = list(DEMO_QUESTIONS)
workflow_options = labels if demo_config.public_demo else labels + ["Custom"]
preset_label = st.radio(
    "Demo workflow",
    workflow_options,
    horizontal=False,
)
if preset_label == "Custom":
    question = st.text_area("Question", height=90)
else:
    question = st.text_area(
        "Question",
        value=DEMO_QUESTIONS[preset_label],
        height=90,
        disabled=demo_config.public_demo,
    )

is_live = planner_mode == "DeepSeek V4"
remaining = max(
    0,
    demo_config.max_live_calls_per_session
    - int(st.session_state.deepseek_live_calls),
)
global_remaining = global_calls_remaining(demo_config.max_live_calls_global)
run_disabled = is_live and (
    not deepseek_api_key or remaining == 0 or global_remaining == 0
)
run = st.button("Investigate", type="primary", disabled=run_disabled)

if run:
    planner = None
    try:
        if is_live:
            reserved, _ = reserve_live_call(demo_config.max_live_calls_global)
            if not reserved:
                st.error("The shared live-call budget is exhausted. Use deterministic fallback.")
                st.stop()
            st.session_state.deepseek_live_calls += 1
            planner = DeepSeekChatPlanner(model=model, api_key=deepseek_api_key)
        else:
            planner = ConstrainedRulePlanner()
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

    render_deepseek_telemetry(getattr(planner, "last_telemetry", None))
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
