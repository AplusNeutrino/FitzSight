from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fitzsight.agent.planner import ConstrainedRulePlanner, StructuredJSONPlanner
from fitzsight.providers.openai_planner import OpenAIResponsesPlanner
from fitzsight.runtime import build_agent_runtime


DEFAULT_QUESTION = "Why did European FTD conversion deteriorate after July 15?"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the FitzSight v0.6 multi-intent Agent investigation."
    )
    parser.add_argument("--question", default=DEFAULT_QUESTION)
    parser.add_argument("--data-dir", default=str(ROOT / "data" / "generated"))
    parser.add_argument(
        "--backend",
        choices=["auto", "duckdb", "sqlite"],
        default="auto",
    )
    parser.add_argument(
        "--planner",
        choices=["deterministic", "json-file", "openai"],
        default="deterministic",
        help=(
            "Use the reliable local fallback, a pre-generated constrained JSON plan, "
            "or the optional OpenAI Responses planner."
        ),
    )
    parser.add_argument("--plan-json", default=None)
    parser.add_argument("--model", default=None, help="OpenAI model; otherwise FITZSIGHT_MODEL")
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def build_planner(args: argparse.Namespace):
    if args.planner == "deterministic":
        return ConstrainedRulePlanner()
    if args.planner == "json-file":
        if not args.plan_json:
            raise SystemExit("--plan-json is required with --planner json-file")
        raw = Path(args.plan_json).read_text(encoding="utf-8")
        return StructuredJSONPlanner(lambda _prompt: raw)
    return OpenAIResponsesPlanner(model=args.model)


def main() -> None:
    args = parse_args()
    data_dir = Path(args.data_dir)
    store, _registry, agent = build_agent_runtime(
        data_dir=data_dir,
        backend=args.backend,
        planner=build_planner(args),
    )
    try:
        result = agent.run(args.question).to_dict()
        result["runtime"] = {
            "backend": store.backend,
            "data_dir": str(data_dir.resolve()),
        }
    finally:
        store.close()

    rendered = json.dumps(result, indent=2, ensure_ascii=False, default=str)
    print(rendered)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
