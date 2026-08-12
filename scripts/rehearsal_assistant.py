from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "submission" / "REHEARSAL_PLAN.json"


def load_plan() -> dict[str, object]:
    return json.loads(PLAN_PATH.read_text(encoding="utf-8"))


def evaluate(mode: str, elapsed_seconds: float) -> dict[str, object]:
    plan = load_plan()
    modes = plan["modes"]
    if mode not in modes:
        raise ValueError(f"Unknown rehearsal mode: {mode}")
    spec = modes[mode]
    minimum = spec.get("min_seconds")
    maximum = spec.get("max_seconds")
    passed = True
    if minimum is not None:
        passed = passed and elapsed_seconds >= float(minimum)
    if maximum is not None:
        passed = passed and elapsed_seconds <= float(maximum)
    return {
        "product": "FitzSight",
        "version": "0.11.0",
        "mode": mode,
        "elapsed_seconds": round(float(elapsed_seconds), 2),
        "target_min_seconds": minimum,
        "target_max_seconds": maximum,
        "timing_passed": passed,
        "human_rehearsal_evidence": True,
        "external_write_actions_performed": False,
        "note": spec.get("note", ""),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Record a local FitzSight rehearsal timing. No network or external submission is performed."
    )
    parser.add_argument("--mode", choices=["pitch", "demo", "qa"], default="pitch")
    parser.add_argument("--elapsed", type=float, default=None, help="Record a measured duration in seconds.")
    parser.add_argument("--interactive", action="store_true", help="Press Enter to start, then Enter to stop.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.dry_run:
        payload = {
            "product": "FitzSight",
            "version": "0.11.0",
            "mode": args.mode,
            "status": "dry_run",
            "plan": load_plan()["modes"][args.mode],
            "external_write_actions_performed": False,
        }
        code = 0
    else:
        elapsed = args.elapsed
        if args.interactive:
            input(f"[{args.mode}] Press Enter to START timing...")
            started = time.perf_counter()
            input(f"[{args.mode}] Press Enter to STOP timing...")
            elapsed = time.perf_counter() - started
        if elapsed is None:
            raise SystemExit("Provide --elapsed SECONDS or use --interactive.")
        payload = evaluate(args.mode, elapsed)
        code = 0 if payload["timing_passed"] else 1

    rendered = json.dumps(payload, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
