from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fitzsight.agent.planner import ConstrainedRulePlanner
from fitzsight.data.generator import GeneratorConfig
from fitzsight.runtime import build_agent_runtime

QUESTION = "Why did European FTD conversion deteriorate after July 15?"
FOLLOW_UP = "What evidence supports the CRM routing change candidate?"


def _render_html(payload: dict) -> str:
    run = payload["run"]
    investigation = run["investigation"]
    verification = run["verification"]
    final = run["final_answer"]
    follow = payload["follow_up"]
    trace_rows = []
    for row in investigation.get("execution_trace", []):
        trace_rows.append(
            "<tr>"
            f"<td>{escape(str(row['step_id']))}</td>"
            f"<td>{escape(str(row['action']))}</td>"
            f"<td><strong>{escape(str(row['status']))}</strong></td>"
            f"<td>{escape(str(row['reason']))}</td>"
            f"<td>{escape(', '.join(row.get('evidence_ids') or []))}</td>"
            "</tr>"
        )
    evidence_rows = []
    for record in run["audit_evidence"]:
        if record["tool_name"] in {
            "agent.plan", "agent.branch_decision", "contribution_analysis", "anomaly_detection",
            "read_only_sql", "document_evidence", "agent.evidence_boundary", "agent.verifier", "agent.final_answer"
        }:
            evidence_rows.append(
                "<tr>"
                f"<td>{escape(record['evidence_id'])}</td>"
                f"<td>{escape(record['tool_name'])}</td>"
                f"<td>{escape(record['status'])}</td>"
                f"<td>{escape(record['result_digest'])}</td>"
                "</tr>"
            )
    findings = "".join(f"<li>{escape(item)}</li>" for item in final["findings"])
    return f"""<!doctype html>
<html lang=\"en\"><head><meta charset=\"utf-8\"><title>FitzSight v0.12 Hero Run Evidence</title>
<style>
body{{font-family:Arial,Helvetica,sans-serif;margin:0;background:#f5f7fb;color:#172033}}
main{{max-width:1400px;margin:0 auto;padding:34px}} h1{{margin:0 0 4px;font-size:34px}} h2{{margin-top:30px}}
.tag{{font-weight:700;color:#334a7d}} .card{{background:white;border:1px solid #dbe1ec;border-radius:12px;padding:18px;margin:14px 0;box-shadow:0 3px 12px rgba(30,50,80,.05)}}
.ok{{display:inline-block;padding:5px 10px;border-radius:20px;background:#e6f5eb;color:#166534;font-weight:700}}
table{{width:100%;border-collapse:collapse;font-size:13px}} th,td{{padding:9px;border-bottom:1px solid #e4e8f0;text-align:left;vertical-align:top}} th{{background:#f4f6fa}}
code{{background:#edf0f5;padding:2px 5px;border-radius:4px}} .guard{{border-left:4px solid #7357c5;padding-left:12px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:14px}} .small{{font-size:12px;color:#5d687b}}
</style></head><body><main>
<div class=\"tag\">FitzSight v0.12 · Brokerage / FinTech Operations Analyst</div>
<h1>Autonomous investigation. Human decision.</h1>
<div class=\"card\"><strong>User question</strong><p>{escape(run['question'])}</p><span class=\"ok\">Verifier: {escape(str(verification['passed']))}</span></div>
<div class=\"card\"><h2>Bounded adaptive execution trace</h2><p class=\"small\">Conditional actions are selected only from the approved catalog; no planner-generated SQL or arbitrary tool arguments.</p>
<table><thead><tr><th>Step</th><th>Approved action</th><th>Status</th><th>Why this branch</th><th>Evidence IDs</th></tr></thead><tbody>{''.join(trace_rows)}</tbody></table></div>
<div class=\"grid\"><div class=\"card\"><h2>Verified answer</h2><strong>{escape(final['headline'])}</strong><ul>{findings}</ul><p class=\"guard\">{escape(final.get('guardrail') or '')}</p></div>
<div class=\"card\"><h2>Approved follow-up</h2><strong>{escape(follow['question'])}</strong><p>{escape(follow['answer'])}</p><p class=\"small\">Follow-up status: {escape(follow['status'])} · record {escape(follow['evidence_record_id'])}</p></div></div>
<div class=\"card\"><h2>Evidence registry excerpt</h2><table><thead><tr><th>ID</th><th>Tool / gate</th><th>Status</th><th>Digest</th></tr></thead><tbody>{''.join(evidence_rows)}</tbody></table></div>
<div class=\"card\"><strong>Evidence boundary</strong><p>This is a synthetic benchmark run. The system reports a supported root-cause candidate only after quantitative, control, operational-event and document evidence align. Final business decisions remain human.</p></div>
</main></body></html>"""


def build(*, backend: str = "sqlite", n_customers: int = 20_000) -> dict:
    with tempfile.TemporaryDirectory(prefix="fitzsight_v012_hero_") as temp:
        store, registry, agent = build_agent_runtime(
            data_dir=Path(temp) / "data",
            backend=backend,
            planner=ConstrainedRulePlanner(),
            generator_config=GeneratorConfig(seed=20260811, n_customers=n_customers, n_salespeople=50),
        )
        try:
            run = agent.run(QUESTION)
            follow_up = agent.answer_follow_up(run, FOLLOW_UP)
            payload = {
                "product": "FitzSight",
                "version": "0.12.1",
                "artifact_type": "verified_hero_product_process_evidence",
                "persona": "Brokerage / FinTech Operations Analyst",
                "tagline": "Autonomous investigation. Human decision.",
                "synthetic_data": True,
                "backend": backend,
                "seed": 20260811,
                "n_customers": n_customers,
                "run": run.to_dict(),
                "follow_up": follow_up.to_dict(),
            }
            # The follow-up record was appended after AgentRunResult captured its
            # audit snapshot; expose the final append-only registry as well.
            payload["final_registry"] = registry.to_dicts()
            return payload
        finally:
            store.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a real verified FitzSight v0.12 hero-run evidence artifact.")
    parser.add_argument("--backend", choices=["sqlite", "duckdb", "auto"], default="sqlite")
    parser.add_argument("--n-customers", type=int, default=20_000)
    parser.add_argument("--json-output", default=str(ROOT / "docs" / "V0.12_HERO_RUN.json"))
    parser.add_argument("--html-output", default=str(ROOT / "submission" / "FitzSight_Hero_Run_Evidence.html"))
    args = parser.parse_args()

    payload = build(backend=args.backend, n_customers=args.n_customers)
    json_path = Path(args.json_output)
    html_path = Path(args.html_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    html_path.write_text(_render_html(payload), encoding="utf-8")
    print(json.dumps({
        "verification_passed": payload["run"]["verification"]["passed"],
        "root_cause_status": payload["run"]["investigation"]["diagnosis"]["root_cause_status"],
        "document_source_ref": payload["run"]["investigation"]["metrics"]["document_evidence"]["source_ref"],
        "execution_trace_steps": len(payload["run"]["investigation"]["execution_trace"]),
        "follow_up_status": payload["follow_up"]["status"],
        "json_output": str(json_path),
        "html_output": str(html_path),
    }, indent=2))


if __name__ == "__main__":
    main()
