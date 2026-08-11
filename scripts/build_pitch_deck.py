from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
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
    s=prs.slides.add_slide(prs.slide_layouts[6]); set_bg(s); add_title(s,"Demo 1 — Why did European FTD conversion deteriorate after July 15?", kicker="CRM / Sales")
    metric_card(s,0.75,1.9,2.35,1.15,"Affected FTD","-7.53 pp",accent=RED,note="Europe Team A+B")
    metric_card(s,3.25,1.9,2.35,1.15,"Control","-1.21 pp",accent=AMBER,note="Other Europe teams")
    metric_card(s,5.75,1.9,2.35,1.15,"Response median","+29.15 min",accent=RED,note="Affected cohort")
    metric_card(s,8.25,1.9,2.0,1.15,"Conversion p","0.00235",accent=GREEN)
    metric_card(s,10.4,1.9,2.1,1.15,"Root cause","Candidate",accent=CYAN,note="Not causal proof")
    add_bar(s,0.85,3.55,5.65,"Affected",-7.53,8,color=RED,value_fmt="{:+.2f} pp")
    add_bar(s,0.85,4.15,5.65,"Control",-1.21,8,color=AMBER,value_fmt="{:+.2f} pp")
    panel(s,7.05,3.4,5.45,2.25,fill=PANEL)
    add_text(s,"Investigation evidence",7.28,3.62,2.8,0.3,size=12,color=CYAN,bold=True)
    bullets=["Response latency shifted sharply after routing change","Team A / Team B dominate negative contribution","Nearby CRM routing event exists in business-event log","Verifier preserves causal-language guardrail"]
    for i,b in enumerate(bullets):
        add_text(s,"• "+b,7.3,4.05+i*0.37,4.8,0.28,size=10.5,color=TEXT)
    add_callout(s,"Result: supported root-cause candidate, with evidence and a causal boundary.",0.85,6.08,11.65,0.65,accent=GREEN)
    add_footer(s,4)


def slide_5(prs):
    s=prs.slides.add_slide(prs.slide_layouts[6]); set_bg(s); add_title(s,"Demo 2 — Why did European net deposits fall in the week starting August 3?", kicker="Financial Operations")
    metric_card(s,0.75,1.9,2.5,1.15,"Net-deposit change","-$223.9k",accent=RED)
    metric_card(s,3.45,1.9,2.5,1.15,"Deposits","+$24.4k",accent=GREEN)
    metric_card(s,6.15,1.9,2.5,1.15,"Withdrawals","+$248.3k",accent=RED)
    metric_card(s,8.85,1.9,3.65,1.15,"Top 11 withdrawal share","92.2%",accent=AMBER,note="Concentration, not motive inference")
    # waterfall-like visual
    panel(s,0.85,3.45,7.2,2.25,fill=PANEL)
    add_text(s,"Driver decomposition",1.05,3.68,2.6,0.28,size=12,color=CYAN,bold=True)
    bars=[("Deposit change",24.4,GREEN),("Withdrawal pressure",-248.3,RED),("Net change",-223.9,RED)]
    max_abs=250
    for i,(lab,val,col) in enumerate(bars):
        add_bar(s,1.1,4.2+i*0.45,6.5,lab,val,max_abs,color=col,value_fmt="{:+.1f}k")
    panel(s,8.35,3.45,4.15,2.25,fill=PANEL)
    add_text(s,"What FitzSight refuses to infer",8.6,3.72,3.55,0.3,size=12,color=AMBER,bold=True)
    for i,t in enumerate(["Customer motive","AML suspicion","Investment intent","Automated account action"]):
        chip(s,t,8.7,4.2+i*0.36,3.45,fill=PANEL_2,color=MUTED)
    add_callout(s,"Observed driver: concentrated withdrawal pressure. Unsupported story: why customers withdrew.",0.85,6.08,11.65,0.65,accent=AMBER)
    add_footer(s,5)


def slide_6(prs):
    s=prs.slides.add_slide(prs.slide_layouts[6]); set_bg(s); add_title(s,"Demo 3 — Customer Intelligence without hidden labels", kicker="Customer Intelligence")
    metric_card(s,0.75,1.9,2.45,1.15,"Europe customers","6,770",accent=CYAN)
    metric_card(s,3.4,1.9,2.45,1.15,"Coverage","100%",accent=GREEN)
    metric_card(s,6.05,1.9,2.45,1.15,"High Value users","4.1%",accent=AMBER)
    metric_card(s,8.7,1.9,3.8,1.15,"High Value deposit share","55.8%",accent=GREEN)
    panel(s,0.8,3.45,7.25,2.1,fill=PANEL)
    add_text(s,"Transparent behavioral value policy",1.03,3.7,3.7,0.3,size=12,color=CYAN,bold=True)
    features=["Deposit value","Deposit frequency","Trade volume","Trade frequency","Withdrawal value"]
    for i,f in enumerate(features):
        chip(s,f,1.05+(i%3)*2.15,4.2+(i//3)*0.55,1.85,fill=PANEL_2,color=TEXT)
    arrow(s,5.95,4.95,7.35,4.95,color=MUTED,width=1.5)
    panel(s,8.35,3.45,4.15,2.1,fill=PANEL)
    add_text(s,"Descriptive use only",8.65,3.72,3.45,0.3,size=12,color=AMBER,bold=True)
    for i,t in enumerate(["No credit decision","No AML decision","No eligibility decision","No adverse action"]):
        add_text(s,"✓ " if False else "• "+t,8.65,4.18+i*0.32,3.2,0.24,size=10.5,color=MUTED)
    add_callout(s,"Normal Agent SQL never reads customer_segment_gt. Segments are built from observable behavior.",0.85,6.08,11.65,0.65,accent=GREEN)
    add_footer(s,6)


def slide_7(prs):
    s=prs.slides.add_slide(prs.slide_layouts[6]); set_bg(s); add_title(s,"Demo 4 — More leads ≠ better acquisition quality", kicker="Marketing / Sales")
    metric_card(s,0.75,1.9,2.3,1.15,"Lead volume","+315%",accent=GREEN)
    metric_card(s,3.2,1.9,2.3,1.15,"Aggregate FTD","-10.84 pp",accent=RED)
    metric_card(s,5.65,1.9,2.3,1.15,"Paid Search mix","+60.52 pp",accent=AMBER)
    metric_card(s,8.1,1.9,2.3,1.15,"Paid Search FTD","-16.44 pp",accent=RED)
    metric_card(s,10.55,1.9,1.95,1.15,"p-value","4.43e-05",accent=GREEN)
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
    s=prs.slides.add_slide(prs.slide_layouts[6]); set_bg(s); add_title(s,"Demo 5 — The system is tested on explanations it refuses to make", kicker="False-correlation guardrail")
    metric_card(s,0.75,1.9,2.25,1.15,"Asia FTD","-8.13 pp",accent=RED)
    metric_card(s,3.15,1.9,2.25,1.15,"Affiliate FTD","-15.81 pp",accent=RED)
    metric_card(s,5.55,1.9,2.25,1.15,"Affiliate p","0.00463",accent=GREEN)
    metric_card(s,7.95,1.9,2.25,1.15,"Nearby event","Office move",accent=AMBER)
    metric_card(s,10.35,1.9,2.15,1.15,"Causal support","FALSE",accent=GREEN)
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
    s=prs.slides.add_slide(prs.slide_layouts[6]); set_bg(s); add_title(s,"Evaluation measures correctness, evidence quality — and safe refusal", kicker="Benchmark & adversarial release gate")
    metric_card(s,0.75,1.95,2.75,1.2,"Benchmark scenarios","5 / 5 PASS",accent=GREEN)
    metric_card(s,3.7,1.95,2.75,1.2,"Root-cause accuracy","100%",accent=GREEN)
    metric_card(s,6.65,1.95,2.75,1.2,"Evidence coverage","100%",accent=GREEN)
    metric_card(s,9.6,1.95,2.9,1.2,"Verifier violations","0",accent=GREEN)
    panel(s,0.8,3.55,5.7,2.2,fill=PANEL)
    add_text(s,"5 deterministic scenarios",1.05,3.8,3.3,0.3,size=12,color=CYAN,bold=True)
    for i,t in enumerate(["CRM routing","Net deposits","Customer Intelligence","Lead quality","False correlation"]):
        chip(s,t,1.05+(i%2)*2.55,4.25+(i//2)*0.43,2.25,fill=PANEL_2,color=TEXT)
    panel(s,6.8,3.55,5.7,2.2,fill=PANEL)
    add_text(s,"8 adversarial cases / 8 PASS",7.05,3.8,4.2,0.3,size=12,color=AMBER,bold=True)
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
    s=prs.slides.add_slide(prs.slide_layouts[6]); set_bg(s)
    add_text(s,"FITZSIGHT",0.8,0.7,3.0,0.45,size=13,color=CYAN,bold=True)
    add_text(s,"BI tells you what changed.\nFitzSight investigates why the measurable evidence changed.",0.8,1.55,10.9,1.35,size=30,bold=True)
    add_callout(s,"A reproducible financial investigation you can inspect, verify, challenge — and sometimes refuse.",0.8,3.35,10.8,0.85,accent=GREEN)
    metric_card(s,0.8,4.75,2.45,1.15,"Agent intents","5",accent=CYAN)
    metric_card(s,3.45,4.75,2.45,1.15,"Benchmark","5 / 5",accent=GREEN)
    metric_card(s,6.1,4.75,2.45,1.15,"Adversarial","8 / 8",accent=AMBER)
    metric_card(s,8.75,4.75,2.85,1.15,"Evidence coverage","100%",accent=GREEN)
    add_text(s,"Evidence-grounded autonomous financial operations investigation",0.85,6.42,10.7,0.35,size=14,color=MUTED,bold=True)
    add_footer(s,12)


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
    pdf = export_pdf(pptx)
    print(f"Created PPTX: {pptx}")
    if pdf:
        print(f"Created PDF:  {pdf}")
        return 0
    print("PDF export skipped: LibreOffice/soffice not available or conversion failed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
