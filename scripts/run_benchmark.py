from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fitzsight.agent.planner import ConstrainedRulePlanner
from fitzsight.runtime import build_agent_runtime


def parse_args():
    parser = argparse.ArgumentParser(description="Run the FitzSight v0.5 deterministic benchmark catalog.")
    parser.add_argument("--catalog", default=str(ROOT / "evaluation" / "benchmark_catalog.json"))
    parser.add_argument("--data-dir", default=str(ROOT / "data" / "generated"))
    parser.add_argument("--backend", choices=["auto", "duckdb", "sqlite"], default="auto")
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def sign_ok(value: float, expected: str) -> bool:
    if expected == "negative":
        return value < 0
    if expected == "positive":
        return value > 0
    if expected == "zero":
        return value == 0
    raise ValueError(f"Unsupported expected sign: {expected}")


def evaluate(scenario, result):
    expected = scenario["expected"]
    investigation = result["investigation"]
    diagnosis = investigation["diagnosis"]
    metrics = investigation["metrics"]

    checks = {
        "verification_passed": result["verification"]["passed"] is expected["verification_passed"],
        "root_cause_status": diagnosis["root_cause_status"] == expected["root_cause_status"],
    }

    if scenario["intent"] == "crm_routing_ftd_investigation":
        checks["affected_conversion_change_sign"] = sign_ok(
            metrics["affected"]["conversion_change_pp"],
            expected["affected_conversion_change_sign"],
        )
        checks["affected_response_change_sign"] = sign_ok(
            metrics["affected_response_median_change_minutes"],
            expected["affected_response_change_sign"],
        )
    elif scenario["intent"] == "net_deposit_anomaly_investigation":
        checks["net_deposit_change_sign"] = sign_ok(
            metrics["driver_decomposition"]["net_change"],
            expected["net_deposit_change_sign"],
        )
        checks["withdrawal_change_sign"] = sign_ok(
            metrics["driver_decomposition"]["withdrawal_change"],
            expected["withdrawal_change_sign"],
        )
        checks["minimum_top_11_withdrawal_share"] = (
            metrics["customer_concentration"]["share_of_current_withdrawals"]
            >= expected["minimum_top_11_withdrawal_share"]
        )
    else:
        checks["known_intent"] = False

    return checks


def main():
    args = parse_args()
    catalog = json.loads(Path(args.catalog).read_text(encoding="utf-8"))
    results = []

    for scenario in catalog["scenarios"]:
        store, _registry, agent = build_agent_runtime(
            data_dir=Path(args.data_dir),
            backend=args.backend,
            planner=ConstrainedRulePlanner(),
        )
        try:
            run = agent.run(scenario["question"]).to_dict()
            backend = store.backend
        finally:
            store.close()

        checks = evaluate(scenario, run)
        results.append(
            {
                "id": scenario["id"],
                "intent": scenario["intent"],
                "passed": all(checks.values()),
                "checks": checks,
                "verification": run["verification"],
                "final_answer_status": run["final_answer"]["status"],
                "backend": backend,
            }
        )

    payload = {
        "product": "FitzSight",
        "benchmark_version": catalog["catalog_version"],
        "scenario_count": len(results),
        "passed": sum(1 for item in results if item["passed"]),
        "failed": sum(1 for item in results if not item["passed"]),
        "results": results,
    }

    rendered = json.dumps(payload, indent=2, ensure_ascii=False, default=str)
    print(rendered)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")

    if payload["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
