from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fitzsight.agent.planner import ConstrainedRulePlanner
from fitzsight.demo import DEMO_QUESTIONS
from fitzsight.runtime import build_agent_runtime


def percentile(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("values must be non-empty")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Measure deterministic FitzSight end-to-end latency without external model cost.")
    parser.add_argument("--backend", choices=["auto", "duckdb", "sqlite"], default="sqlite")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--data-dir", default=str(ROOT / "data" / "generated"))
    parser.add_argument("--output", default=str(ROOT / "docs" / "V0.9_DETERMINISTIC_LATENCY.json"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.repeats <= 0:
        raise SystemExit("--repeats must be positive")
    data_dir = Path(args.data_dir)

    # Warm the reproducible synthetic dataset once so timed runs represent Agent/runtime work,
    # not CSV generation.
    warm_store, _registry, _agent = build_agent_runtime(
        data_dir=data_dir,
        backend=args.backend,
        planner=ConstrainedRulePlanner(),
    )
    actual_backend = warm_store.backend
    warm_store.close()

    results: list[dict[str, object]] = []
    all_ms: list[float] = []
    for label, question in DEMO_QUESTIONS.items():
        samples: list[float] = []
        statuses: list[str] = []
        for _ in range(args.repeats):
            started = time.perf_counter()
            store, _registry, agent = build_agent_runtime(
                data_dir=data_dir,
                backend=args.backend,
                planner=ConstrainedRulePlanner(),
            )
            try:
                run = agent.run(question).to_dict()
            finally:
                store.close()
            elapsed_ms = (time.perf_counter() - started) * 1000
            samples.append(elapsed_ms)
            all_ms.append(elapsed_ms)
            statuses.append(run["final_answer"]["status"])
        if any(status != "verified" for status in statuses):
            raise RuntimeError(f"Latency measurement encountered an unverified run: {label}")
        results.append(
            {
                "label": label,
                "question": question,
                "samples_ms": samples,
                "mean_ms": statistics.fmean(samples),
                "p50_ms": percentile(samples, 0.50),
                "p95_ms": percentile(samples, 0.95),
                "verified_runs": len(samples),
            }
        )

    report = {
        "product": "FitzSight",
        "measurement": "deterministic_end_to_end_latency",
        "backend": actual_backend,
        "repeats_per_workflow": args.repeats,
        "workflow_count": len(DEMO_QUESTIONS),
        "total_runs": len(all_ms),
        "overall_mean_ms": statistics.fmean(all_ms),
        "overall_p50_ms": percentile(all_ms, 0.50),
        "overall_p95_ms": percentile(all_ms, 0.95),
        "provider_cost_measured": False,
        "provider_cost_note": "DeepSeek live planner cost and latency were deliberately not measured. Offline deterministic latency and mock request-contract tests are the v0.13 release evidence; scripts/validate_deepseek_runtime.py remains an explicit opt-in.",
        "results": results,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
