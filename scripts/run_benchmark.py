from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fitzsight.agent.planner import ConstrainedRulePlanner
from fitzsight.runtime import build_agent_runtime


def parse_args():
    parser = argparse.ArgumentParser(description="Run the FitzSight v0.9 deterministic benchmark catalog.")
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


def claim_evidence_coverage(result: dict) -> float:
    claims = result["investigation"].get("claims", [])
    if not claims:
        return 0.0
    covered = sum(1 for claim in claims if claim.get("evidence_ids"))
    return covered / len(claims)


def evaluate(scenario, result):
    expected = scenario["expected"]
    investigation = result["investigation"]
    diagnosis = investigation["diagnosis"]
    metrics = investigation["metrics"]

    checks = {
        "verification_passed": result["verification"]["passed"] is expected["verification_passed"],
        "root_cause_status": diagnosis["root_cause_status"] == expected["root_cause_status"],
        "final_answer_verified": result["final_answer"]["status"] == "verified",
        "evidence_coverage_complete": claim_evidence_coverage(result) == 1.0,
        "verifier_has_no_violations": not result["verification"]["violations"],
    }

    intent = scenario["intent"]
    if intent == "crm_routing_ftd_investigation":
        checks["affected_conversion_change_sign"] = sign_ok(
            metrics["affected"]["conversion_change_pp"], expected["affected_conversion_change_sign"]
        )
        checks["affected_response_change_sign"] = sign_ok(
            metrics["affected_response_median_change_minutes"], expected["affected_response_change_sign"]
        )
    elif intent == "net_deposit_anomaly_investigation":
        checks["net_deposit_change_sign"] = sign_ok(
            metrics["driver_decomposition"]["net_change"], expected["net_deposit_change_sign"]
        )
        checks["withdrawal_change_sign"] = sign_ok(
            metrics["driver_decomposition"]["withdrawal_change"], expected["withdrawal_change_sign"]
        )
        checks["minimum_top_11_withdrawal_share"] = (
            metrics["customer_concentration"]["share_of_current_withdrawals"]
            >= expected["minimum_top_11_withdrawal_share"]
        )
    elif intent == "customer_intelligence_segmentation":
        segmentation = metrics["segmentation"]
        checks["segmentation_method"] = segmentation["method"] == expected["segmentation_method"]
        checks["minimum_coverage"] = segmentation["coverage"] >= expected["minimum_coverage"]
        checks["minimum_segment_count"] = segmentation["segment_count"] >= expected["minimum_segment_count"]
        checks["expected_top_deposit_segment"] = (
            segmentation["top_deposit_segment"] == expected["expected_top_deposit_segment"]
        )
        if expected["high_value_avg_deposits_exceeds_low_activity"]:
            checks["high_value_avg_deposits_exceeds_low_activity"] = (
                segmentation["high_value_avg_deposits"] > segmentation["low_activity_avg_deposits"]
            )
    elif intent == "marketing_lead_quality_investigation":
        checks["lead_volume_change_sign"] = sign_ok(
            metrics["lead_volume_change"], expected["lead_volume_change_sign"]
        )
        checks["conversion_change_sign"] = sign_ok(
            metrics["conversion_change_pp"], expected["conversion_change_sign"]
        )
        checks["paid_search_share_change_sign"] = sign_ok(
            metrics["paid_search_share_change_pp"], expected["paid_search_share_change_sign"]
        )
        checks["top_negative_performance_channel"] = (
            diagnosis["top_negative_channel_performance_effect"]
            == expected["top_negative_performance_channel"]
        )
        checks["paid_search_shift_significant"] = (
            diagnosis["paid_search_shift_significant"] is expected["paid_search_shift_significant"]
        )
    elif intent == "false_correlation_guardrail_investigation":
        checks["conversion_change_sign"] = sign_ok(
            metrics["conversion_change_pp"], expected["conversion_change_sign"]
        )
        checks["top_negative_performance_channel"] = (
            diagnosis["top_negative_channel_performance_effect"]
            == expected["top_negative_performance_channel"]
        )
        checks["affiliate_shift_significant"] = (
            diagnosis["affiliate_shift_significant"] is expected["affiliate_shift_significant"]
        )
        checks["nearby_event_cause_supported"] = (
            diagnosis["nearby_event_cause_supported"] is expected["nearby_event_cause_supported"]
        )
        checks["false_correlation_rejected"] = (
            diagnosis["false_correlation_rejected"] is expected["false_correlation_rejected"]
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
            data_dir=Path(args.data_dir), backend=args.backend, planner=ConstrainedRulePlanner()
        )
        started = time.perf_counter()
        try:
            run = agent.run(scenario["question"]).to_dict()
            backend = store.backend
        finally:
            store.close()
        latency_ms = (time.perf_counter() - started) * 1000

        checks = evaluate(scenario, run)
        results.append(
            {
                "id": scenario["id"],
                "intent": scenario["intent"],
                "passed": all(checks.values()),
                "checks": checks,
                "verification": run["verification"],
                "final_answer_status": run["final_answer"]["status"],
                "evidence_coverage": claim_evidence_coverage(run),
                "verifier_violation_count": len(run["verification"]["violations"]),
                "latency_ms": latency_ms,
                "backend": backend,
            }
        )

    root_cause_scenarios = [
        item for item in results if item["intent"] != "customer_intelligence_segmentation"
    ]
    false_corr = [
        item for item in results if item["intent"] == "false_correlation_guardrail_investigation"
    ]
    payload = {
        "product": "FitzSight",
        "benchmark_version": catalog["catalog_version"],
        "scenario_count": len(results),
        "passed": sum(1 for item in results if item["passed"]),
        "failed": sum(1 for item in results if not item["passed"]),
        "metrics": {
            "scenario_pass_rate": (
                sum(1 for item in results if item["passed"]) / len(results) if results else 0.0
            ),
            "root_cause_scenario_accuracy": (
                sum(1 for item in root_cause_scenarios if item["passed"]) / len(root_cause_scenarios)
                if root_cause_scenarios else None
            ),
            "false_correlation_rejection_accuracy": (
                sum(1 for item in false_corr if item["passed"]) / len(false_corr)
                if false_corr else None
            ),
            "mean_evidence_coverage": (
                sum(item["evidence_coverage"] for item in results) / len(results) if results else 0.0
            ),
            "total_verifier_violations": sum(item["verifier_violation_count"] for item in results),
            "mean_latency_ms": (
                sum(item["latency_ms"] for item in results) / len(results) if results else 0.0
            ),
        },
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
