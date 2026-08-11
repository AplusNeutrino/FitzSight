from __future__ import annotations

from pathlib import Path
from functools import lru_cache
from tempfile import TemporaryDirectory
import json
import shutil
import subprocess
import sys

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fitzsight.agent.catalog import (
    CRM_INTENT,
    NET_DEPOSIT_INTENT,
    CUSTOMER_INTELLIGENCE_INTENT,
    MARKETING_LEAD_QUALITY_INTENT,
    FALSE_CORRELATION_INTENT,
)
from fitzsight.agent.planner import ConstrainedRulePlanner
from fitzsight.demo import DEMO_QUESTIONS
from fitzsight.runtime import build_agent_runtime

SUBMISSION_DIR = ROOT / "submission"
PPTX_PATH = SUBMISSION_DIR / "FitzSight_GOAI_Initial_Round.pptx"
PDF_PATH = SUBMISSION_DIR / "FitzSight_GOAI_Initial_Round.pdf"

# 16:9 widescreen.
SLIDE_W = Inches(13.333333)
SLIDE_H = Inches(7.5)

BG = RGBColor(11, 16, 32)
PANEL = RGBColor(20, 27, 45)
PANEL_2 = RGBColor(27, 36, 58)
TEXT = RGBColor(246, 248, 252)
MUTED = RGBColor(170, 180, 197)
CYAN = RGBColor(88, 211, 255)
GREEN = RGBColor(84, 211, 155)
AMBER = RGBColor(255, 200, 87)
RED = RGBColor(255, 107, 107)
WHITE = RGBColor(255, 255, 255)

FONT = "Liberation Sans"


@lru_cache(maxsize=1)
def _pitch_runs() -> dict[str, dict]:
    """Generate the competition-facing metrics from fresh verified Agent runs.

    This intentionally uses a temporary synthetic-data directory so the deck never
    relies on whatever CSV bundle happens to exist in the repository. Every numeric
    claim on the demo slides therefore comes from the current deterministic runtime.
    """

    runs: dict[str, dict] = {}
    with TemporaryDirectory(prefix="fitzsight_pitch_") as tmp:
        store, _registry, agent = build_agent_runtime(
            data_dir=Path(tmp),
            backend="sqlite",
            planner=ConstrainedRulePlanner(),
        )
        try:
            for question in DEMO_QUESTIONS.values():
                result = agent.run(question)
                if result.final_answer.status != "verified" or not result.verification.passed:
                    raise RuntimeError(
                        f"Pitch-deck metric source failed verification for {result.plan.intent}"
                    )
                runs[result.plan.intent] = result.to_dict()
        finally:
            store.close()
    return runs


def _metrics(intent: str) -> dict:
    return _pitch_runs()[intent]["investigation"]["metrics"]


def _diagnosis(intent: str) -> dict:
    return _pitch_runs()[intent]["investigation"]["diagnosis"]


def _money_k(value: float, *, signed: bool = True) -> str:
    sign = ""
    if signed:
        sign = "+" if value > 0 else "-" if value < 0 else ""
    elif value < 0:
        sign = "-"
    return f"{sign}${abs(value) / 1000:.1f}k"


def _pp(value: float) -> str:
    return f"{value:+.2f} pp"


def _pct(value: float, digits: int = 1) -> str:
    return f"{value * 100:.{digits}f}%"


def _pvalue(value: float) -> str:
    return f"{value:.2e}" if value < 0.001 else f"{value:.5f}"


def _segment_profile(metrics: dict, segment: str) -> dict:
    for profile in metrics["segmentation"]["profiles"]:
        if profile["segment"] == segment:
            return profile
    raise KeyError(f"Missing segment profile: {segment}")


def _evaluation_snapshot() -> dict:
    """Read the latest available benchmark/adversarial release-gate snapshot."""

    bench_candidates = [
        ROOT / "docs" / "V0.9_BENCHMARK_RESULTS.json",
        ROOT / "docs" / "V0.7_BENCHMARK_RESULTS.json",
    ]
    adv_candidates = [
        ROOT / "docs" / "V0.9_ADVERSARIAL_RESULTS.json",
        ROOT / "docs" / "V0.7_ADVERSARIAL_RESULTS.json",
    ]
    bench = next((json.loads(p.read_text(encoding="utf-8")) for p in bench_candidates if p.exists()), None)
    adv = next((json.loads(p.read_text(encoding="utf-8")) for p in adv_candidates if p.exists()), None)
    if bench is None or adv is None:
        raise FileNotFoundError("Benchmark/adversarial release-gate results are required to build the pitch deck")
    return {"benchmark": bench, "adversarial": adv}


def set_bg(slide, color=BG):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_text(slide, text, x, y, w, h, *, size=24, color=TEXT, bold=False,
             align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP, font=FONT):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.name = font
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    return box


def add_title(slide, title, subtitle=None, *, kicker=None):
    if kicker:
        add_text(slide, kicker.upper(), 0.7, 0.35, 6.4, 0.3, size=10, color=CYAN, bold=True)
    add_text(slide, title, 0.7, 0.72, 11.8, 0.72, size=30, bold=True)
    if subtitle:
        add_text(slide, subtitle, 0.72, 1.48, 11.5, 0.42, size=14, color=MUTED)


def add_footer(slide, n):
    add_text(slide, "FitzSight · GOAI 2026 · Boundless Agents · AI+金融", 0.72, 7.13, 9.5, 0.2, size=8, color=MUTED)
    add_text(slide, str(n), 12.1, 7.08, 0.5, 0.24, size=9, color=MUTED, align=PP_ALIGN.RIGHT)


def panel(slide, x, y, w, h, *, fill=PANEL, radius=True, line=None):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    shp = slide.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    shp.line.color.rgb = line or fill
    return shp


def chip(slide, text, x, y, w, *, fill=PANEL_2, color=TEXT):
    shp = panel(slide, x, y, w, 0.36, fill=fill)
    add_text(slide, text, x+0.12, y+0.08, w-0.24, 0.18, size=10, color=color, bold=True, align=PP_ALIGN.CENTER)
    return shp


def metric_card(slide, x, y, w, h, label, value, *, accent=CYAN, note=None):
    panel(slide, x, y, w, h, fill=PANEL)
    add_text(slide, label, x+0.18, y+0.16, w-0.36, 0.26, size=10, color=MUTED, bold=True)
    add_text(slide, value, x+0.18, y+0.54, w-0.36, 0.55, size=24, color=accent, bold=True)
    if note:
        add_text(slide, note, x+0.18, y+h-0.38, w-0.36, 0.24, size=8.5, color=MUTED)


def arrow(slide, x1, y1, x2, y2, *, color=CYAN, width=2.0):
    line = slide.shapes.add_connector(1, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    line.line.color.rgb = color
    line.line.width = Pt(width)
    line.line.end_arrowhead = True
    return line


def flow_node(slide, text, x, y, w=1.7, *, fill=PANEL_2, accent=CYAN):
    panel(slide, x, y, w, 0.72, fill=fill, line=accent)
    add_text(slide, text, x+0.08, y+0.17, w-0.16, 0.34, size=11, bold=True, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)


def add_bar(slide, x, y, w, label, value, max_abs, *, color=CYAN, value_fmt="{:+.2f}"):
    add_text(slide, label, x, y, 2.1, 0.22, size=10, color=TEXT, bold=True)
    bar_x = x + 2.25
    base_y = y + 0.05
    base_w = w - 2.25
    panel(slide, bar_x, base_y, base_w, 0.16, fill=PANEL_2, radius=False)
    ratio = min(abs(value) / max_abs, 1.0) if max_abs else 0
    fill_w = max(0.04, base_w * ratio)
    fill_color = color if value >= 0 else RED
    panel(slide, bar_x, base_y, fill_w, 0.16, fill=fill_color, radius=False)
    add_text(slide, value_fmt.format(value), bar_x+base_w-0.8, y-0.01, 0.75, 0.2, size=9.5, color=TEXT, bold=True, align=PP_ALIGN.RIGHT)


def add_callout(slide, text, x, y, w, h, *, accent=CYAN):
    panel(slide, x, y, w, h, fill=PANEL_2, line=accent)
    panel(slide, x, y, 0.06, h, fill=accent, radius=False)
    add_text(slide, text, x+0.2, y+0.14, w-0.35, h-0.24, size=12, color=TEXT, bold=True, valign=MSO_ANCHOR.MIDDLE)


def slide_1(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6]); set_bg(s)
    add_text(s, "FITZSIGHT", 0.75, 0.65, 4.5, 0.55, size=13, color=CYAN, bold=True)
    add_text(s, "Evidence-grounded\nFinancial Operations\nIntelligence Agent", 0.75, 1.34, 7.9, 2.05, size=31, bold=True)
    add_text(s, "GOAI 2026 · Boundless Agents · AI+金融", 0.8, 3.65, 6.6, 0.4, size=16, color=MUTED)
    add_callout(s, "Question → Data → Analysis → Evidence → Decision", 0.8, 4.48, 6.8, 0.8, accent=CYAN)
    # Visual evidence chain on right
    x = 9.2
    for i, (t, c) in enumerate([("PLAN", CYAN), ("TOOLS", GREEN), ("EVIDENCE", AMBER), ("VERIFY", CYAN)]):
        panel(s, x, 1.15+i*1.15, 2.7, 0.82, fill=PANEL, line=c)
        add_text(s, t, x+0.2, 1.39+i*1.15, 2.3, 0.3, size=15, color=c, bold=True, align=PP_ALIGN.CENTER)
        if i < 3:
            arrow(s, x+1.35, 1.97+i*1.15, x+1.35, 2.25+i*1.15, color=MUTED, width=1.3)
    add_text(s, "Not chat with a CSV.\nAn auditable investigation.", 9.25, 6.05, 2.8, 0.65, size=13, color=MUTED, bold=True, align=PP_ALIGN.CENTER)
    add_footer(s, 1)


def slide_2(prs):
    s=prs.slides.add_slide(prs.slide_layouts[6]); set_bg(s); add_title(s,"The gap: dashboards show what, analysts still investigate why", kicker="Problem")
    steps=["Find tables","Define KPI","Compare periods","Drill dimensions","Test significance","Inspect events","Reconcile numbers","Write report"]
    y=2.05
    for i,t in enumerate(steps):
        x=0.75+(i%4)*3.05; yy=y+(i//4)*1.25
        panel(s,x,yy,2.55,0.76,fill=PANEL)
        add_text(s,f"{i+1:02d}",x+0.16,yy+0.17,0.35,0.26,size=11,color=CYAN,bold=True)
        add_text(s,t,x+0.52,yy+0.15,1.82,0.35,size=12,bold=True)
    add_callout(s,"A generic LLM can generate an explanation faster — but plausibility is not auditability.",0.75,4.85,11.75,0.86,accent=AMBER)
    metric_card(s,0.75,5.95,3.55,0.9,"Existing stack","Dashboard + SQL + BI",accent=MUTED)
    metric_card(s,4.55,5.95,3.55,0.9,"Missing layer","Reproducible investigation",accent=CYAN)
    metric_card(s,8.35,5.95,4.15,0.9,"Design target","Evidence before narrative",accent=GREEN)
    add_footer(s,2)


def slide_3(prs):
    s=prs.slides.add_slide(prs.slide_layouts[6]); set_bg(s); add_title(s,"FitzSight turns a business question into a verified investigation", kicker="Product")
    labels=[("Question",CYAN),("Constrained\nPlan",CYAN),("SQL / Python\nTools",GREEN),("Evidence\nGraph",AMBER),("Verifier",CYAN),("Verified\nAnswer",GREEN)]
    xs=[0.65,2.75,4.85,7.0,9.1,11.0]
    widths=[1.55,1.55,1.65,1.55,1.35,1.7]
    for i,((t,c),x,w) in enumerate(zip(labels,xs,widths)):
        flow_node(s, t, x, 2.45, w, fill=PANEL, accent=c)
    # fix flow nodes manually due signature
    # connectors
    for i in range(len(xs)-1):
        arrow(s,xs[i]+widths[i],2.81,xs[i+1]-0.08,2.81,color=MUTED,width=1.4)
    add_callout(s,"Planner decides what to investigate. Deterministic tools own every number. Verifier decides what may be shown.",0.8,4.0,11.7,0.95,accent=CYAN)
    metric_card(s,0.8,5.3,3.5,1.15,"Planner authority","Approved actions only",accent=CYAN,note="No free-form SQL or high-impact actions")
    metric_card(s,4.55,5.3,3.5,1.15,"Calculation authority","Read-only SQL / Python",accent=GREEN,note="Statistics and decompositions are executable")
    metric_card(s,8.3,5.3,4.2,1.15,"Answer authority","EvidenceClaimVerifier",accent=AMBER,note="Verification failure → answer withheld")
    add_footer(s,3)


def slide_4(prs):
    m = _metrics(CRM_INTENT)
    d = _diagnosis(CRM_INTENT)
    affected = float(m["affected"]["conversion_change_pp"])
    control = float(m["control"]["conversion_change_pp"])
    response = float(m["affected_response_median_change_minutes"])
    conversion_p = float(m["conversion_test"]["p_value"])
    top_team = m["team_contribution_analysis"]["segments"][0]["segment"]
    anomaly_days = int(m["post_change_response_anomalies"]["anomaly_count"])
    root_status = str(d["root_cause_status"]).replace("_", " ").title()

    s=prs.slides.add_slide(prs.slide_layouts[6]); set_bg(s); add_title(s,"Demo 1 — Why did European FTD conversion deteriorate after July 15?", kicker="CRM / Sales")
    metric_card(s,0.75,1.9,2.35,1.15,"Affected FTD",_pp(affected),accent=RED,note="Europe Team A+B")
    metric_card(s,3.25,1.9,2.35,1.15,"Control",_pp(control),accent=AMBER,note="Other Europe teams")
    metric_card(s,5.75,1.9,2.35,1.15,"Response median",f"{response:+.2f} min",accent=RED,note="Affected cohort")
    metric_card(s,8.25,1.9,2.0,1.15,"Conversion p",_pvalue(conversion_p),accent=GREEN)
    metric_card(s,10.4,1.9,2.1,1.15,"Root cause",root_status.replace("Supported ", ""),accent=CYAN,note="Not causal proof")
    max_abs=max(abs(affected),abs(control),1.0)
    add_bar(s,0.85,3.55,5.65,"Affected",affected,max_abs,color=RED,value_fmt="{:+.2f} pp")
    add_bar(s,0.85,4.15,5.65,"Control",control,max_abs,color=AMBER,value_fmt="{:+.2f} pp")
    panel(s,7.05,3.4,5.45,2.25,fill=PANEL)
    add_text(s,"Investigation evidence",7.28,3.62,2.8,0.3,size=12,color=CYAN,bold=True)
    bullets=[
        f"Response latency shifted by {response:+.2f} minutes after the routing change",
        f"{top_team} is the largest negative team-level contributor",
        "Nearby CRM routing event exists in the business-event log",
        f"{anomaly_days} post-change response-time days exceed the robust threshold",
    ]
    for i,b in enumerate(bullets):
        add_text(s,"• "+b,7.3,4.05+i*0.37,4.8,0.28,size=10.5,color=TEXT)
    add_callout(s,"Result: supported root-cause candidate, with evidence and a causal boundary.",0.85,6.08,11.65,0.65,accent=GREEN)
    add_footer(s,4)

def slide_5(prs):
    m = _metrics(NET_DEPOSIT_INTENT)
    dec = m["driver_decomposition"]
    concentration = m["customer_concentration"]
    net_change = float(dec["net_change"])
    deposit_change = float(dec["deposit_change"])
    withdrawal_change = float(dec["withdrawal_change"])
    share = float(concentration["share_of_current_withdrawals"])
    n_customers = int(concentration["customer_count"])

    s=prs.slides.add_slide(prs.slide_layouts[6]); set_bg(s); add_title(s,"Demo 2 — Why did European net deposits fall in the week starting August 3?", kicker="Financial Operations")
    metric_card(s,0.75,1.9,2.5,1.15,"Net-deposit change",_money_k(net_change),accent=RED)
    metric_card(s,3.45,1.9,2.5,1.15,"Deposits",_money_k(deposit_change),accent=GREEN)
    metric_card(s,6.15,1.9,2.5,1.15,"Withdrawals",_money_k(withdrawal_change),accent=RED)
    metric_card(s,8.85,1.9,3.65,1.15,f"Top {n_customers} withdrawal share",_pct(share),accent=AMBER,note="Concentration, not motive inference")
    panel(s,0.85,3.45,7.2,2.25,fill=PANEL)
    add_text(s,"Driver decomposition",1.05,3.68,2.6,0.28,size=12,color=CYAN,bold=True)
    bars=[("Deposit change",deposit_change/1000,GREEN),("Withdrawal pressure",-withdrawal_change/1000,RED),("Net change",net_change/1000,RED)]
    max_abs=max(abs(v) for _,v,_ in bars)
    for i,(lab,val,col) in enumerate(bars):
        add_bar(s,1.1,4.2+i*0.45,6.5,lab,val,max_abs,color=col,value_fmt="{:+.1f}k")
    panel(s,8.35,3.45,4.15,2.25,fill=PANEL)
    add_text(s,"What FitzSight refuses to infer",8.6,3.72,3.55,0.3,size=12,color=AMBER,bold=True)
    for i,t in enumerate(["Customer motive","AML suspicion","Investment intent","Automated account action"]):
        chip(s,t,8.7,4.2+i*0.36,3.45,fill=PANEL_2,color=MUTED)
    add_callout(s,"Observed driver: concentrated withdrawal pressure. Unsupported story: why customers withdrew.",0.85,6.08,11.65,0.65,accent=AMBER)
    add_footer(s,5)

def slide_6(prs):
    m = _metrics(CUSTOMER_INTELLIGENCE_INTENT)
    seg = m["segmentation"]
    high = _segment_profile(m, "High Value")
    customers = int(seg["customer_count"])
    coverage = float(seg["coverage"])
    customer_share = float(high["customer_share"])
    deposit_share = float(high["deposit_share"])

    s=prs.slides.add_slide(prs.slide_layouts[6]); set_bg(s); add_title(s,"Demo 3 — Customer Intelligence without hidden labels", kicker="Customer Intelligence")
    metric_card(s,0.75,1.9,2.45,1.15,"Europe customers",f"{customers:,}",accent=CYAN)
    metric_card(s,3.4,1.9,2.45,1.15,"Coverage",_pct(coverage,0),accent=GREEN)
    metric_card(s,6.05,1.9,2.45,1.15,"High Value users",_pct(customer_share),accent=AMBER)
    metric_card(s,8.7,1.9,3.8,1.15,"High Value deposit share",_pct(deposit_share),accent=GREEN)
    panel(s,0.8,3.45,7.25,2.1,fill=PANEL)
    add_text(s,"Transparent behavioral value policy",1.03,3.7,3.7,0.3,size=12,color=CYAN,bold=True)
    features=["Deposit value","Deposit frequency","Trade volume","Trade frequency","Withdrawal value"]
    for i,f in enumerate(features):
        chip(s,f,1.05+(i%3)*2.15,4.2+(i//3)*0.55,1.85,fill=PANEL_2,color=TEXT)
    arrow(s,5.95,4.95,7.35,4.95,color=MUTED,width=1.5)
    panel(s,8.35,3.45,4.15,2.1,fill=PANEL)
    add_text(s,"Descriptive use only",8.65,3.72,3.45,0.3,size=12,color=AMBER,bold=True)
    for i,t in enumerate(["No credit decision","No AML decision","No eligibility decision","No adverse action"]):
        add_text(s,"• "+t,8.65,4.18+i*0.32,3.2,0.24,size=10.5,color=MUTED)
    add_callout(s,"Normal Agent SQL never reads customer_segment_gt. Segments are built from observable behavior.",0.85,6.08,11.65,0.65,accent=GREEN)
    add_footer(s,6)

def slide_7(prs):
    m = _metrics(MARKETING_LEAD_QUALITY_INTENT)
    volume_pct=float(m["lead_volume_change_pct"])
    conversion=float(m["conversion_change_pp"])
    mix=float(m["paid_search_share_change_pp"])
    paid=float(m["paid_search_conversion_test"]["difference_pp_b_minus_a"])
    pval=float(m["paid_search_conversion_test"]["p_value"])

    s=prs.slides.add_slide(prs.slide_layouts[6]); set_bg(s); add_title(s,"Demo 4 — More leads ≠ better acquisition quality", kicker="Marketing / Sales")
    metric_card(s,0.75,1.9,2.3,1.15,"Lead volume",f"{volume_pct:+.0f}%",accent=GREEN)
    metric_card(s,3.2,1.9,2.3,1.15,"Aggregate FTD",_pp(conversion),accent=RED)
    metric_card(s,5.65,1.9,2.3,1.15,"Paid Search mix",_pp(mix),accent=AMBER)
    metric_card(s,8.1,1.9,2.3,1.15,"Paid Search FTD",_pp(paid),accent=RED)
    metric_card(s,10.55,1.9,1.95,1.15,"p-value",_pvalue(pval),accent=GREEN)
    panel(s,0.85,3.45,11.65,2.1,fill=PANEL)
    add_text(s,"FitzSight separates three questions",1.1,3.72,4.2,0.3,size=12,color=CYAN,bold=True)
    flow_node(s,"1. Volume",1.15,4.25,2.1,fill=PANEL_2,accent=GREEN)
    flow_node(s,"2. Channel mix",4.05,4.25,2.4,fill=PANEL_2,accent=AMBER)
    flow_node(s,"3. Within-channel\nperformance",7.3,4.1,2.8,fill=PANEL_2,accent=RED)
    arrow(s,3.25,4.61,4.0,4.61,color=MUTED,width=1.4)
    arrow(s,6.45,4.61,7.25,4.61,color=MUTED,width=1.4)
    add_text(s,"Paid Search is the measurable quality failure — not simply a high lead count.",1.15,5.08,10.6,0.3,size=12,color=TEXT,bold=True,align=PP_ALIGN.CENTER)
    add_footer(s,7)

def slide_8(prs):
    m = _metrics(FALSE_CORRELATION_INTENT)
    d = _diagnosis(FALSE_CORRELATION_INTENT)
    asia=float(m["conversion_change_pp"])
    affiliate=float(m["affiliate_conversion_test"]["difference_pp_b_minus_a"])
    pval=float(m["affiliate_conversion_test"]["p_value"])
    nearby=m["nearby_business_events"][0]["event_type"].replace("_", " ").title() if m["nearby_business_events"] else "None"
    supported=bool(d["nearby_event_cause_supported"])

    s=prs.slides.add_slide(prs.slide_layouts[6]); set_bg(s); add_title(s,"Demo 5 — The system is tested on explanations it refuses to make", kicker="False-correlation guardrail")
    metric_card(s,0.75,1.9,2.25,1.15,"Asia FTD",_pp(asia),accent=RED)
    metric_card(s,3.15,1.9,2.25,1.15,"Affiliate FTD",_pp(affiliate),accent=RED)
    metric_card(s,5.55,1.9,2.25,1.15,"Affiliate p",_pvalue(pval),accent=GREEN)
    metric_card(s,7.95,1.9,2.25,1.15,"Nearby event",nearby,accent=AMBER)
    metric_card(s,10.35,1.9,2.15,1.15,"Causal support",str(supported).upper(),accent=GREEN if not supported else RED)
    panel(s,0.85,3.45,11.65,2.3,fill=PANEL)
    add_text(s,"Tempting story",1.15,3.7,2.2,0.3,size=12,color=AMBER,bold=True)
    flow_node(s,"Office relocation",1.15,4.15,2.2,fill=PANEL_2,accent=AMBER)
    arrow(s,3.4,4.5,4.4,4.5,color=AMBER,width=1.5)
    flow_node(s,"Asia FTD ↓",4.45,4.15,1.8,fill=PANEL_2,accent=RED)
    add_text(s,"Rejected",4.72,5.05,1.2,0.25,size=11,color=RED,bold=True,align=PP_ALIGN.CENTER)
    add_text(s,"Measured evidence",7.1,3.7,2.6,0.3,size=12,color=CYAN,bold=True)
    flow_node(s,"Affiliate quality ↓",7.15,4.15,2.35,fill=PANEL_2,accent=RED)
    arrow(s,9.55,4.5,10.35,4.5,color=CYAN,width=1.5)
    flow_node(s,"Supported driver",10.4,4.15,1.65,fill=PANEL_2,accent=GREEN)
    add_callout(s,"Temporal proximity is context, not proof. FitzSight runs a falsification check before attribution.",0.85,6.15,11.65,0.62,accent=GREEN)
    add_footer(s,8)

def slide_9(prs):
    s=prs.slides.add_slide(prs.slide_layouts[6]); set_bg(s); add_title(s,"Four trust boundaries make the Agent auditable", kicker="Technical differentiation")
    cards=[
        ("01","Local intent gate","Unsupported questions are refused before a model call.",CYAN),
        ("02","Constrained planner","Only approved high-level actions; no SQL or arbitrary tool args.",AMBER),
        ("03","Deterministic tools","Read-only SQL / Python own calculations, tests and decompositions.",GREEN),
        ("04","Claim verifier","Evidence IDs, digest/status, ground-truth boundary and causal language.",CYAN),
    ]
    for i,(num,title,desc,col) in enumerate(cards):
        x=0.8+(i%2)*6.0; y=1.95+(i//2)*2.05
        panel(s,x,y,5.65,1.6,fill=PANEL,line=col)
        add_text(s,num,x+0.2,y+0.2,0.5,0.3,size=12,color=col,bold=True)
        add_text(s,title,x+0.8,y+0.18,4.35,0.35,size=16,bold=True)
        add_text(s,desc,x+0.8,y+0.66,4.35,0.65,size=11,color=MUTED)
    add_callout(s,"Verification fails → FitzSight withholds the analytical answer.",0.85,6.2,11.65,0.6,accent=RED)
    add_footer(s,9)


def slide_10(prs):
    snapshot = _evaluation_snapshot()
    bench = snapshot["benchmark"]
    adv = snapshot["adversarial"]
    bm = bench["metrics"]
    scenario_count = int(bench["scenario_count"])
    passed = int(bench["passed"])
    root_acc=float(bm["root_cause_scenario_accuracy"])
    evidence_cov=float(bm["mean_evidence_coverage"])
    violations=int(bm["total_verifier_violations"])
    adv_passed=int(adv["passed"])
    adv_count=int(adv["case_count"])

    s=prs.slides.add_slide(prs.slide_layouts[6]); set_bg(s); add_title(s,"Evaluation measures correctness, evidence quality — and safe refusal", kicker="Benchmark & adversarial release gate")
    metric_card(s,0.75,1.95,2.75,1.2,"Benchmark scenarios",f"{passed} / {scenario_count} PASS",accent=GREEN)
    metric_card(s,3.7,1.95,2.75,1.2,"Root-cause accuracy",_pct(root_acc,0),accent=GREEN)
    metric_card(s,6.65,1.95,2.75,1.2,"Evidence coverage",_pct(evidence_cov,0),accent=GREEN)
    metric_card(s,9.6,1.95,2.9,1.2,"Verifier violations",str(violations),accent=GREEN)
    panel(s,0.8,3.55,5.7,2.2,fill=PANEL)
    add_text(s,f"{scenario_count} deterministic scenarios",1.05,3.8,3.3,0.3,size=12,color=CYAN,bold=True)
    for i,t in enumerate(["CRM routing","Net deposits","Customer Intelligence","Lead quality","False correlation"]):
        chip(s,t,1.05+(i%2)*2.55,4.25+(i//2)*0.43,2.25,fill=PANEL_2,color=TEXT)
    panel(s,6.8,3.55,5.7,2.2,fill=PANEL)
    add_text(s,f"{adv_count} adversarial cases / {adv_passed} PASS",7.05,3.8,4.2,0.3,size=12,color=AMBER,bold=True)
    items=["Scope refusal","Planner policy","Missing evidence","Causal overclaim","_gt leakage","False correlation"]
    for i,t in enumerate(items):
        chip(s,t,7.05+(i%2)*2.55,4.25+(i//2)*0.43,2.25,fill=PANEL_2,color=MUTED)
    add_callout(s,"The release gate rewards the system for refusing unsupported answers, not only producing correct ones.",0.85,6.15,11.65,0.62,accent=AMBER)
    add_footer(s,10)

def slide_11(prs):
    s=prs.slides.add_slide(prs.slide_layouts[6]); set_bg(s); add_title(s,"Safety, compliance and reproducibility are product constraints", kicker="Open source")
    left=["Synthetic benchmark data only","No real customer PII or employer data","No investment advice or trading actions","No automated AML / credit / suitability decisions","Evaluation-only *_gt fields blocked from normal Agent SQL"]
    panel(s,0.8,1.9,6.2,4.75,fill=PANEL)
    add_text(s,"Operational boundaries",1.05,2.18,3.4,0.3,size=13,color=CYAN,bold=True)
    for i,t in enumerate(left):
        add_text(s,"• "+t,1.08,2.72+i*0.62,5.5,0.44,size=11.5,color=TEXT)
    panel(s,7.35,1.9,5.15,4.75,fill=PANEL)
    add_text(s,"Reproducibility",7.65,2.18,2.8,0.3,size=13,color=GREEN,bold=True)
    metric_card(s,7.65,2.75,2.0,1.0,"License","MIT",accent=GREEN)
    metric_card(s,9.85,2.75,2.25,1.0,"Backend","DuckDB",accent=CYAN)
    metric_card(s,7.65,4.0,2.0,1.0,"Fallback","SQLite",accent=AMBER)
    metric_card(s,9.85,4.0,2.25,1.0,"Planner","Local fallback",accent=GREEN)
    add_text(s,"Public repo",7.65,5.35,1.4,0.22,size=10,color=MUTED,bold=True)
    add_text(s,"github.com/AplusNeutrino/FitzSight",7.65,5.72,4.1,0.35,size=11,color=CYAN,bold=True)
    add_footer(s,11)


def slide_12(prs):
    snapshot = _evaluation_snapshot()
    bench = snapshot["benchmark"]
    adv = snapshot["adversarial"]
    coverage=float(bench["metrics"]["mean_evidence_coverage"])
    s=prs.slides.add_slide(prs.slide_layouts[6]); set_bg(s)
    add_text(s,"FITZSIGHT",0.8,0.7,3.0,0.45,size=13,color=CYAN,bold=True)
    add_text(s,"BI tells you what changed.\nFitzSight investigates why the measurable evidence changed.",0.8,1.55,10.9,1.35,size=30,bold=True)
    add_callout(s,"A reproducible financial investigation you can inspect, verify, challenge — and sometimes refuse.",0.8,3.35,10.8,0.85,accent=GREEN)
    metric_card(s,0.8,4.75,2.45,1.15,"Agent intents",str(len(DEMO_QUESTIONS)),accent=CYAN)
    metric_card(s,3.45,4.75,2.45,1.15,"Benchmark",f"{bench['passed']} / {bench['scenario_count']}",accent=GREEN)
    metric_card(s,6.1,4.75,2.45,1.15,"Adversarial",f"{adv['passed']} / {adv['case_count']}",accent=AMBER)
    metric_card(s,8.75,4.75,2.85,1.15,"Evidence coverage",_pct(coverage,0),accent=GREEN)
    add_text(s,"Evidence-grounded autonomous financial operations investigation",0.85,6.42,10.7,0.35,size=14,color=MUTED,bold=True)
    add_footer(s,12)

def build_speaker_notes() -> Path:
    crm = _metrics(CRM_INTENT)
    net = _metrics(NET_DEPOSIT_INTENT)
    customer = _metrics(CUSTOMER_INTELLIGENCE_INTENT)
    marketing = _metrics(MARKETING_LEAD_QUALITY_INTENT)
    false_corr = _metrics(FALSE_CORRELATION_INTENT)
    snapshot = _evaluation_snapshot()

    crm_affected = float(crm["affected"]["conversion_change_pp"])
    crm_control = float(crm["control"]["conversion_change_pp"])
    crm_response = float(crm["affected_response_median_change_minutes"])

    net_dec = net["driver_decomposition"]
    net_conc = net["customer_concentration"]

    high = _segment_profile(customer, "High Value")

    notes = f"""# FitzSight — 12-Slide Speaker Notes

> Numeric claims in Slides 4-8 are generated from fresh verified deterministic FitzSight runs by `scripts/build_pitch_deck.py`.

## Slide 1 — FitzSight

“FitzSight is an evidence-grounded financial operations Agent. It turns a business question into a bounded, reproducible investigation: question, data, analysis, evidence, decision.”

## Slide 2 — Problem

“Financial teams already have dashboards and SQL. The slow part is the investigation behind ‘why did this change?’ A generic LLM can write a plausible explanation quickly, but plausibility is not auditability.”

## Slide 3 — Product

“The model or fallback planner selects an approved workflow. SQL and Python calculate. Evidence records each step. A verifier decides which claims are allowed into the final answer.”

## Slide 4 — CRM / FTD

“The affected European teams changed by {_pp(crm_affected)} versus {_pp(crm_control)} in the control cohort, while median response time changed by {crm_response:+.2f} minutes. The result is a supported root-cause candidate, not a causal proof.”

## Slide 5 — Net deposits

“European net deposits changed by {_money_k(float(net_dec['net_change']))} week over week. Deposits changed by {_money_k(float(net_dec['deposit_change']))}, while withdrawals increased by {_money_k(float(net_dec['withdrawal_change']))}. The largest {int(net_conc['customer_count'])} withdrawals account for {_pct(float(net_conc['share_of_current_withdrawals']))} of current withdrawals. FitzSight reports that concentration without inventing customer motives.”

## Slide 6 — Customer Intelligence

“Customer segmentation is transparent and descriptive. It uses observable behavior, not hidden benchmark labels. High Value customers are {_pct(float(high['customer_share']))} of European customers but contribute {_pct(float(high['deposit_share']))} of deposits in the current synthetic benchmark.”

## Slide 7 — Acquisition quality

“Lead volume increased {float(marketing['lead_volume_change_pct']):.0f}%, while FTD conversion changed by {_pp(float(marketing['conversion_change_pp']))}. FitzSight separates volume, channel mix and within-channel performance; Paid Search conversion changed by {_pp(float(marketing['paid_search_conversion_test']['difference_pp_b_minus_a']))} with p={_pvalue(float(marketing['paid_search_conversion_test']['p_value']))}.”

## Slide 8 — False correlation

“This is a deliberate trap. An office relocation occurs near an Asia conversion decline of {_pp(float(false_corr['conversion_change_pp']))}. Affiliate conversion changes by {_pp(float(false_corr['affiliate_conversion_test']['difference_pp_b_minus_a']))}; the falsification check therefore rejects the nearby office event as a supported cause.”

## Slide 9 — Technical difference

“The four trust boundaries are local intent gating, constrained planning, deterministic tools and a fail-closed verifier. A model never receives unrestricted authority to execute SQL or financial actions.”

## Slide 10 — Evaluation

“The benchmark contains {snapshot['benchmark']['scenario_count']} deterministic scenarios and {snapshot['benchmark']['passed']} pass. Mean evidence coverage is {_pct(float(snapshot['benchmark']['metrics']['mean_evidence_coverage']),0)}, with {snapshot['benchmark']['metrics']['total_verifier_violations']} verifier violations. The adversarial release gate contains {snapshot['adversarial']['case_count']} cases and {snapshot['adversarial']['passed']} pass.”

## Slide 11 — Safety and open source

“All benchmark data is synthetic. The system is not an investment adviser or automated compliance engine. The core project is MIT licensed, DuckDB is the preferred local backend, and a deterministic fallback keeps the demo usable without a cloud model.”

## Slide 12 — Close

“BI tells you what changed. FitzSight investigates why the measurable evidence changed — with a result you can inspect, verify, challenge, and sometimes refuse.”
"""
    path = SUBMISSION_DIR / "PITCH_SPEAKER_NOTES.md"
    path.write_text(notes, encoding="utf-8")
    return path


def build_pptx() -> Path:
    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    # remove default slide if any (Presentation starts with none in python-pptx)
    for builder in [slide_1,slide_2,slide_3,slide_4,slide_5,slide_6,slide_7,slide_8,slide_9,slide_10,slide_11,slide_12]:
        builder(prs)
    prs.save(PPTX_PATH)
    return PPTX_PATH


def export_pdf(pptx_path: Path) -> Path | None:
    libreoffice = shutil.which("libreoffice") or shutil.which("soffice")
    if not libreoffice:
        return None
    completed = subprocess.run(
        [
            libreoffice,
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(SUBMISSION_DIR),
            str(pptx_path),
        ],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    print(completed.stdout.strip())
    generated = pptx_path.with_suffix(".pdf")
    return generated if generated.exists() else None


def main() -> int:
    pptx = build_pptx()
    notes = build_speaker_notes()
    pdf = export_pdf(pptx)
    print(f"Created PPTX: {pptx}")
    print(f"Created notes: {notes}")
    if pdf:
        print(f"Created PDF:  {pdf}")
        return 0
    print("PDF export skipped: LibreOffice/soffice not available or conversion failed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
