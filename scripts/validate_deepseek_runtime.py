from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fitzsight.demo import DEFAULT_QUESTION
from fitzsight.providers.deepseek_planner import (
    DEFAULT_DEEPSEEK_MODEL,
    DeepSeekChatPlanner,
)
from fitzsight.runtime import build_agent_runtime


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the bounded DeepSeek V4 planner through a verified FitzSight Agent run."
    )
    parser.add_argument("--question", default=DEFAULT_QUESTION)
    parser.add_argument("--data-dir", default=str(ROOT / "data" / "generated"))
    parser.add_argument("--backend", choices=["auto", "duckdb", "sqlite"], default="auto")
    parser.add_argument(
        "--model",
        choices=["deepseek-v4-flash", "deepseek-v4-pro"],
        default=None,
    )
    parser.add_argument("--output", default=None)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configured_model = (
        args.model
        or os.getenv("FITZSIGHT_DEEPSEEK_MODEL")
        or DEFAULT_DEEPSEEK_MODEL
    )
    key_present = bool(os.getenv("DEEPSEEK_API_KEY"))
    report: dict[str, object] = {
        "product": "FitzSight",
        "runtime": "deepseek_chat_planner",
        "question": args.question,
        "backend_requested": args.backend,
        "model": configured_model,
        "api_key_present": key_present,
        "api_key_disclosed": False,
        "passed": False,
    }
    if args.dry_run:
        report["status"] = "dry_run"
        code = 0
    elif not key_present:
        report["status"] = "not_run_missing_configuration"
        report["message"] = "Set DEEPSEEK_API_KEY before explicit live validation."
        code = 2
    else:
        planner = DeepSeekChatPlanner(model=configured_model)
        started = time.perf_counter()
        store, _registry, agent = build_agent_runtime(
            data_dir=Path(args.data_dir), backend=args.backend, planner=planner
        )
        try:
            result = agent.run(args.question).to_dict()
            report.update(
                {
                    "status": (
                        "passed"
                        if result["final_answer"]["status"] == "verified"
                        and result["verification"]["passed"]
                        else "failed"
                    ),
                    "passed": bool(
                        result["verification"]["passed"]
                        and result["final_answer"]["status"] == "verified"
                    ),
                    "backend_actual": store.backend,
                    "planner_mode": result["planner_mode"],
                    "intent": result["plan"]["intent"],
                    "verification_evidence_id": result["verification"]["evidence_id"],
                    "total_runtime_seconds": time.perf_counter() - started,
                    "provider_telemetry": planner.last_telemetry,
                }
            )
        finally:
            store.close()
        code = 0 if report["passed"] else 1

    rendered = json.dumps(report, indent=2, ensure_ascii=False, default=str)
    print(rendered)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
