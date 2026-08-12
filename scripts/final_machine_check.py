from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_script(name: str):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load script: {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_json_script(script: str, *args: str) -> tuple[dict[str, object], int]:
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    stdout = completed.stdout.strip()
    try:
        payload = json.loads(stdout) if stdout else {}
    except json.JSONDecodeError:
        payload = {
            "status": "invalid_json_output",
            "passed": False,
            "stdout_tail": stdout[-4000:],
            "stderr_tail": completed.stderr[-4000:],
        }
    return payload, completed.returncode


def _deterministic_agent_smoke() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="fitzsight_final_machine_") as tmp:
        output = Path(tmp) / "agent.json"
        report, code = _run_json_script(
            "agent_investigate.py",
            "--backend",
            "sqlite",
            "--data-dir",
            str(Path(tmp) / "data"),
            "--output",
            str(output),
        )
    final_status = report.get("final_answer", {}).get("status") if isinstance(report.get("final_answer"), dict) else None
    verification = report.get("verification", {}) if isinstance(report.get("verification"), dict) else {}
    passed = code == 0 and final_status == "verified" and verification.get("passed") is True
    return {
        "passed": passed,
        "return_code": code,
        "final_status": final_status,
        "verification_passed": verification.get("passed"),
        "planner_mode": report.get("planner_mode"),
        "intent": report.get("plan", {}).get("intent") if isinstance(report.get("plan"), dict) else None,
    }


def build_report(*, attempt_streamlit: bool = True, include_openai: bool = False) -> dict[str, object]:
    doctor = _load_script("runtime_doctor.py").build_report(ROOT / "data" / "generated")
    kit_present = (ROOT / "submission" / "FitzSight_Final_Machine_Kit.zip").exists()
    preflight = _load_script("preflight_submission.py").run_preflight(require_final_machine_kit=kit_present)
    handoff = _load_script("handoff_readiness.py").readiness_report(require_final_machine_kit=kit_present)
    deterministic = _deterministic_agent_smoke()

    streamlit_report: dict[str, object]
    if attempt_streamlit:
        streamlit_report, streamlit_code = _run_json_script("validate_streamlit_runtime.py")
        streamlit_report = {**streamlit_report, "return_code": streamlit_code}
    else:
        streamlit_report = {
            "runtime": "streamlit",
            "status": "not_requested",
            "passed": False,
            "return_code": None,
        }

    openai_report: dict[str, object]
    if include_openai:
        openai_report, openai_code = _run_json_script("validate_openai_runtime.py")
        openai_report = {**openai_report, "return_code": openai_code}
    else:
        openai_report = {
            "runtime": "openai_responses_planner",
            "status": "not_requested",
            "passed": False,
            "return_code": None,
            "note": "Live provider validation is opt-in because it can use configured credentials/network access.",
        }

    local_ready = bool(
        doctor.get("core_demo_ready")
        and preflight.get("passed")
        and handoff.get("ready_for_user_takeover")
        and deterministic.get("passed")
    )

    return {
        "product": "FitzSight",
        "version": "0.12.0",
        "purpose": "final_machine_local_readiness",
        "local_core_ready": local_ready,
        "deterministic_agent_smoke": deterministic,
        "runtime_doctor": doctor,
        "submission_preflight": {
            "passed": preflight.get("passed"),
            "missing_required_files": preflight.get("missing_required_files"),
            "secret_hits": preflight.get("secret_hits"),
            "generated_csv_files": preflight.get("generated_csv_files"),
        },
        "handoff_readiness": {
            "ready_for_user_takeover": handoff.get("ready_for_user_takeover"),
            "manual_handoff_zip_integrity": handoff.get("manual_handoff_zip_integrity"),
            "final_machine_kit_integrity": handoff.get("final_machine_kit_integrity"),
        },
        "streamlit_live": streamlit_report,
        "openai_live": openai_report,
        "external_write_actions_performed": False,
        "portal_or_email_actions_performed": False,
        "network_policy": {
            "default_run": "local_only_except_localhost_streamlit_health_check",
            "openai_live_requires_explicit_include_openai": True,
        },
        "remaining_user_manual_actions": [
            "Run this report on the final presentation machine and retain the JSON output",
            "If Streamlit is installed, require streamlit_live.passed=true before calling the live UI validated",
            "Only run --include-openai if you deliberately choose to validate a configured provider",
            "Perform timed pitch/demo and Q&A rehearsal",
            "Perform all competition portal upload/final-submit/confirmation steps manually",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="One-command FitzSight final-machine readiness check. External portal/email writes are never performed."
    )
    parser.add_argument("--skip-streamlit", action="store_true")
    parser.add_argument(
        "--include-openai",
        action="store_true",
        help="Explicitly opt in to the live OpenAI planner validator if credentials/model are configured.",
    )
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        attempt_streamlit=not args.skip_streamlit,
        include_openai=args.include_openai,
    )
    rendered = json.dumps(report, indent=2, ensure_ascii=False, default=str)
    print(rendered)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["local_core_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
