from __future__ import annotations

import argparse
from dataclasses import asdict
from html import escape
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fitzsight.agent.planner import ConstrainedRulePlanner
from fitzsight.demo import DEMO_QUESTIONS
from fitzsight.runtime import build_agent_runtime
from fitzsight.ui.presenter import build_presentation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a self-contained offline FitzSight demo from verified deterministic Agent outputs."
    )
    parser.add_argument("--backend", choices=["auto", "duckdb", "sqlite"], default="sqlite")
    parser.add_argument(
        "--data-dir",
        default=str(ROOT / "data" / "generated"),
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "submission" / "FitzSight_Offline_Demo.html"),
    )
    parser.add_argument(
        "--json-output",
        default=str(ROOT / "submission" / "FitzSight_Offline_Demo.json"),
    )
    return parser.parse_args()


def _render_chart(view: dict) -> str:
    chart = view["chart"]
    series = chart["series"]
    values = [abs(float(v)) for s in series for v in s["values"]]
    scale = max(values) if values else 1.0
    if scale == 0:
        scale = 1.0

    rows = []
    for index, category in enumerate(chart["categories"]):
        cells = [f"<div class='category'>{escape(str(category))}</div>"]
        for item in series:
            value = float(item["values"][index])
            width = max(2.0, min(100.0, abs(value) / scale * 100.0))
            sign_class = "negative" if value < 0 else "positive"
            cells.append(
                "<div class='bar-row'>"
                f"<span class='series-label'>{escape(item['label'])}</span>"
                f"<span class='bar-track'><span class='bar {sign_class}' style='width:{width:.1f}%'></span></span>"
                f"<span class='bar-value'>{value:,.3g}</span>"
                "</div>"
            )
        rows.append("<div class='chart-row'>" + "".join(cells) + "</div>")
    return "".join(rows)


def _section(label: str, question: str, view: dict) -> str:
    kpis = "".join(
        f"<div class='kpi'><span>{escape(item['label'])}</span><strong>{escape(item['value'])}</strong></div>"
        for item in view["kpis"]
    )
    findings = "".join(f"<li>{escape(item)}</li>" for item in view["findings"])
    trace = "".join(
        "<tr>"
        f"<td>{escape(row['step'])}</td>"
        f"<td>{escape(row['action'])}</td>"
        f"<td>{escape(row['purpose'])}</td>"
        "</tr>"
        for row in view["trace"]
    )
    evidence = " ".join(
        f"<span class='evidence-pill'>{escape(item['evidence_id'])}: {escape(item['tool_name'])}</span>"
        for item in view["evidence_cards"][:12]
    )
    guardrail = (
        f"<div class='guardrail'><strong>Guardrail</strong><br>{escape(view['guardrail'])}</div>"
        if view["guardrail"]
        else ""
    )
    return f"""
<section class='workflow'>
  <div class='eyebrow'>{escape(label)}</div>
  <h2>{escape(question)}</h2>
  <div class='status-line'><span class='status verified'>{escape(view['status'])}</span><span>{view['verified_claims']}/{view['total_claims']} claims verified</span><span>backend: {escape(view['backend'])}</span></div>
  <div class='kpi-grid'>{kpis}</div>
  <div class='panel'><h3>{escape(view['chart']['title'])}</h3><p>{escape(view['chart']['caption'])}</p>{_render_chart(view)}</div>
  <div class='two-col'>
    <div class='panel'><h3>Verified findings</h3><ul>{findings}</ul>{guardrail}</div>
    <div class='panel'><h3>Investigation trace</h3><table><thead><tr><th>Step</th><th>Action</th><th>Purpose</th></tr></thead><tbody>{trace}</tbody></table></div>
  </div>
  <div class='panel'><h3>Evidence preview</h3><div class='evidence-list'>{evidence}</div></div>
</section>
"""


def _document(sections: str, summary: dict) -> str:
    return f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'>
<title>FitzSight Offline Demo</title>
<style>
:root {{ color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; }}
* {{ box-sizing: border-box; }}
body {{ margin:0; background:#0b1020; color:#eef2ff; line-height:1.45; }}
header {{ padding:72px max(28px,7vw) 52px; background:linear-gradient(135deg,#111a34,#0b1020); border-bottom:1px solid #283354; }}
header h1 {{ margin:0 0 12px; font-size:clamp(42px,7vw,84px); letter-spacing:-0.04em; }}
header p {{ max-width:950px; margin:0; color:#aeb9d6; font-size:20px; }}
.badges {{ display:flex; gap:10px; flex-wrap:wrap; margin-top:24px; }}
.badge,.status,.evidence-pill {{ display:inline-flex; padding:6px 10px; border-radius:999px; border:1px solid #354269; background:#141d38; color:#cbd5f3; font-size:13px; }}
.badge strong {{ color:#fff; margin-right:5px; }}
.workflow {{ padding:56px max(24px,6vw); border-bottom:1px solid #202943; }}
.eyebrow {{ color:#8fb2ff; text-transform:uppercase; font-size:13px; letter-spacing:.16em; font-weight:700; }}
h2 {{ font-size:clamp(28px,4vw,48px); line-height:1.08; max-width:1100px; margin:10px 0 16px; }}
h3 {{ margin-top:0; }}
.status-line {{ display:flex; flex-wrap:wrap; gap:10px; align-items:center; color:#aeb9d6; margin-bottom:22px; }}
.status.verified {{ color:#c7f9d9; border-color:#2f7650; background:#10281c; }}
.kpi-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:12px; margin:20px 0; }}
.kpi {{ padding:16px; border:1px solid #2a3659; background:#111a31; border-radius:14px; min-height:92px; }}
.kpi span {{ display:block; color:#8f9bb9; font-size:13px; margin-bottom:8px; }}
.kpi strong {{ font-size:24px; letter-spacing:-.03em; }}
.panel {{ border:1px solid #2a3659; background:#10172b; border-radius:16px; padding:20px; margin:14px 0; overflow:auto; }}
.panel p {{ color:#9da9c7; }}
.two-col {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; }}
@media(max-width:900px) {{ .two-col {{ grid-template-columns:1fr; }} }}
table {{ border-collapse:collapse; width:100%; font-size:13px; }}
th,td {{ border-bottom:1px solid #25304f; text-align:left; padding:9px; vertical-align:top; }}
th {{ color:#8fb2ff; }}
ul {{ padding-left:21px; }}
.guardrail {{ margin-top:16px; padding:14px; border-left:3px solid #e0b154; background:#2a2313; color:#f5ddb0; }}
.chart-row {{ display:grid; grid-template-columns:minmax(110px,160px) 1fr; gap:8px 14px; margin:13px 0; align-items:center; }}
.category {{ grid-row:1 / span 5; font-weight:700; }}
.bar-row {{ display:grid; grid-template-columns:minmax(160px,250px) 1fr 86px; align-items:center; gap:10px; }}
.series-label,.bar-value {{ color:#9da9c7; font-size:12px; }}
.bar-value {{ text-align:right; font-variant-numeric:tabular-nums; }}
.bar-track {{ height:10px; background:#1c2745; border-radius:999px; overflow:hidden; }}
.bar {{ display:block; height:100%; border-radius:999px; background:#6b91e8; }}
.bar.negative {{ background:#bd6f7f; }}
.evidence-list {{ display:flex; flex-wrap:wrap; gap:8px; }}
footer {{ padding:42px max(24px,6vw); color:#8490af; }}
</style>
</head>
<body>
<header>
  <div class='eyebrow'>GOAI 2026 · Boundless Agents · AI+Finance</div>
  <h1>FitzSight</h1>
  <p>Evidence-grounded Financial Operations Intelligence Agent. This offline backup is generated from actual deterministic Agent runs and renders only verified outputs; it does not create a second analytical path.</p>
  <div class='badges'>
    <span class='badge'><strong>{summary['scenario_count']}</strong> workflows</span>
    <span class='badge'><strong>{summary['verified_runs']}/{summary['scenario_count']}</strong> verified</span>
    <span class='badge'><strong>{summary['evidence_records']}</strong> audit records</span>
    <span class='badge'>No cloud model required</span>
  </div>
</header>
{sections}
<footer>Decision support only · Synthetic benchmark data · No investment advice, automated compliance conclusion, credit decision, or high-impact account action.</footer>
</body>
</html>
"""


def build_demo(*, data_dir: Path, backend: str) -> tuple[str, dict]:
    runs: list[dict] = []
    total_evidence = 0
    sections: list[str] = []
    for label, question in DEMO_QUESTIONS.items():
        store, _registry, agent = build_agent_runtime(
            data_dir=data_dir,
            backend=backend,
            planner=ConstrainedRulePlanner(),
        )
        try:
            result = agent.run(question).to_dict()
            view = build_presentation(result, backend=store.backend).to_dict()
        finally:
            store.close()
        if view["status"] != "verified" or not view["verification_passed"]:
            raise RuntimeError(f"Offline demo refused to package unverified workflow: {label}")
        total_evidence += len(view["evidence_cards"])
        sections.append(_section(label, question, view))
        runs.append(
            {
                "label": label,
                "question": question,
                "intent": view["intent"],
                "status": view["status"],
                "backend": view["backend"],
                "verified_claims": view["verified_claims"],
                "total_claims": view["total_claims"],
                "kpis": view["kpis"],
                "findings": view["findings"],
                "guardrail": view["guardrail"],
                "evidence_ids": [card["evidence_id"] for card in view["evidence_cards"]],
            }
        )

    summary = {
        "product": "FitzSight",
        "artifact": "offline_verified_demo",
        "scenario_count": len(runs),
        "verified_runs": sum(1 for run in runs if run["status"] == "verified"),
        "evidence_records": total_evidence,
        "backend": backend,
        "runs": runs,
    }
    return _document("".join(sections), summary), summary


def main() -> int:
    args = parse_args()
    data_dir = Path(args.data_dir)
    html, summary = build_demo(data_dir=data_dir, backend=args.backend)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    json_output = Path(args.json_output)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "verified",
        "html": str(output),
        "json": str(json_output),
        "scenario_count": summary["scenario_count"],
        "verified_runs": summary["verified_runs"],
        "evidence_records": summary["evidence_records"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
