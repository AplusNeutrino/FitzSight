from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fitzsight.agent.catalog import CRM_INTENT, FALSE_CORRELATION_INTENT
from fitzsight.agent.planner import ConstrainedRulePlanner
from fitzsight.data.generator import GeneratorConfig
from fitzsight.runtime import build_agent_runtime


HOLDOUT_SEEDS = (20260821, 20260831)
CASES = (
    {
        "case_id": "crm_paraphrase_a",
        "intent": CRM_INTENT,
        "question": "Investigate the drop in Europe FTD conversion after July 15 and tell me what the evidence supports.",
        "expects_refusal": False,
    },
    {
        "case_id": "crm_paraphrase_b",
        "intent": CRM_INTENT,
        "question": "For Europe, what explains the FTD conversion deterioration after 2026-07-15?",
        "expects_refusal": False,
    },
    {
        "case_id": "false_corr_paraphrase_a",
        "intent": FALSE_CORRELATION_INTENT,
        "question": "Asia FTD conversion fell after July 20. Does evidence support the nearby office relocation as the cause?",
        "expects_refusal": True,
    },
    {
        "case_id": "false_corr_paraphrase_b",
        "intent": FALSE_CORRELATION_INTENT,
        "question": "Investigate Asia conversion after 2026-07-20; should we attribute it to the office relocation?",
        "expects_refusal": True,
    },
)


def _evidence_coverage(payload: dict) -> float:
    claims = payload["investigation"]["claims"]
    supported = [c for c in claims if c["status"] in {"supported", "supported_with_guardrail"}]
    if not supported:
        return 1.0
    covered = sum(1 for c in supported if c["evidence_ids"])
    return covered / len(supported)


def run_holdout(*, backend: str = "sqlite", n_customers: int = 10_000) -> dict:
    rows: list[dict] = []
    temp_root = Path(tempfile.mkdtemp(prefix="fitzsight_v012_holdout_"))
    try:
        for seed in HOLDOUT_SEEDS:
            data_dir = temp_root / str(seed)
            store, _registry, agent = build_agent_runtime(
                data_dir=data_dir,
                backend=backend,
                planner=ConstrainedRulePlanner(),
                generator_config=GeneratorConfig(seed=seed, n_customers=n_customers, n_salespeople=50),
            )
            try:
                for case in CASES:
                    result = agent.run(case["question"]).to_dict()
                    diagnosis = result["investigation"]["diagnosis"]
                    routed = result["plan"]["intent"] == case["intent"]
                    refusal_correct = None
                    if case["expects_refusal"]:
                        refusal_correct = (
                            diagnosis.get("false_correlation_rejected") is True
                            and diagnosis.get("nearby_event_cause_supported") is False
                        )
                    rows.append(
                        {
                            "seed": seed,
                            "case_id": case["case_id"],
                            "question": case["question"],
                            "expected_intent": case["intent"],
                            "actual_intent": result["plan"]["intent"],
                            "intent_routing_stable": routed,
                            "verification_passed": bool(result["verification"]["passed"]),
                            "root_cause_status": diagnosis.get("root_cause_status"),
                            "evidence_coverage": _evidence_coverage(result),
                            "refusal_correct": refusal_correct,
                        }
                    )
            finally:
                store.close()
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

    routing_rate = sum(row["intent_routing_stable"] for row in rows) / len(rows)
    verification_rate = sum(row["verification_passed"] for row in rows) / len(rows)
    mean_coverage = sum(row["evidence_coverage"] for row in rows) / len(rows)
    refusal_rows = [row for row in rows if row["refusal_correct"] is not None]
    refusal_rate = sum(bool(row["refusal_correct"]) for row in refusal_rows) / len(refusal_rows)
    supported_rows = [row for row in rows if row["root_cause_status"] == "supported_candidate"]

    return {
        "product": "FitzSight",
        "evaluation_version": "0.12",
        "evaluation_type": "holdout_seed_and_question_paraphrase",
        "construction": {
            "training_or_showcase_seed_excluded": 20260811,
            "holdout_seeds": list(HOLDOUT_SEEDS),
            "cases_per_seed": len(CASES),
            "n_customers_per_seed": n_customers,
            "backend": backend,
            "scope": "CRM/FTD hero plus false-correlation refusal only; synthetic benchmark generalization check, not real-client performance.",
        },
        "metrics": {
            "case_runs": len(rows),
            "intent_routing_stability": routing_rate,
            "verification_pass_rate": verification_rate,
            "supported_candidate_rate": len(supported_rows) / len(rows),
            "mean_evidence_coverage": mean_coverage,
            "false_correlation_refusal_correctness": refusal_rate,
        },
        "results": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run FitzSight v0.12 holdout seed/paraphrase evaluation.")
    parser.add_argument("--backend", choices=["sqlite", "duckdb", "auto"], default="sqlite")
    parser.add_argument("--n-customers", type=int, default=10_000)
    parser.add_argument("--output", default=str(ROOT / "docs" / "V0.12_HOLDOUT_RESULTS.json"))
    args = parser.parse_args()

    payload = run_holdout(backend=args.backend, n_customers=args.n_customers)
    rendered = json.dumps(payload, indent=2, ensure_ascii=False, default=str)
    print(rendered)
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered + "\n", encoding="utf-8")
    if payload["metrics"]["intent_routing_stability"] < 1.0 or payload["metrics"]["verification_pass_rate"] < 1.0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
