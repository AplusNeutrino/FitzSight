from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fitzsight.agent.orchestrator import FitzSightAgent
from fitzsight.agent.planner import ConstrainedRulePlanner, StructuredJSONPlanner
from fitzsight.agent.verifier import EvidenceClaimVerifier
from fitzsight.data.generator import GeneratorConfig, write_csv_bundle
from fitzsight.data.store import AnalyticsStore
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.investigation.engine import DeterministicInvestigationEngine
from fitzsight.tools.schema import SchemaInspectorTool
from fitzsight.tools.sql import ReadOnlySQLTool
from fitzsight.tools.statistics import StatisticalTestTool

DEFAULT_QUESTION = "Why did European FTD conversion deteriorate after July 15?"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the FitzSight v0.4 constrained Agent investigation.")
    parser.add_argument("--question", default=DEFAULT_QUESTION)
    parser.add_argument("--data-dir", default=str(ROOT / "data" / "generated"))
    parser.add_argument("--backend", choices=["auto", "duckdb", "sqlite"], default="auto")
    parser.add_argument(
        "--planner",
        choices=["deterministic", "json-file"],
        default="deterministic",
        help="Use the reliable deterministic fallback or validate a pre-generated structured planner JSON file.",
    )
    parser.add_argument("--plan-json", default=None, help="Required when --planner json-file")
    parser.add_argument("--output", default=None, help="Optional JSON output path")
    return parser.parse_args()


def build_planner(args: argparse.Namespace):
    if args.planner == "deterministic":
        return ConstrainedRulePlanner()
    if not args.plan_json:
        raise SystemExit("--plan-json is required with --planner json-file")
    raw = Path(args.plan_json).read_text(encoding="utf-8")
    return StructuredJSONPlanner(lambda _prompt: raw)


def main() -> None:
    args = parse_args()
    data_dir = Path(args.data_dir)
    if not (data_dir / "sales_activity.csv").exists():
        write_csv_bundle(data_dir, GeneratorConfig())

    registry = EvidenceRegistry()
    with AnalyticsStore(data_dir, backend=args.backend) as store:
        store.load_csv_directory()
        engine = DeterministicInvestigationEngine(
            schema_tool=SchemaInspectorTool(store, registry),
            sql_tool=ReadOnlySQLTool(store, registry, max_rows=5000),
            stats_tool=StatisticalTestTool(registry),
            registry=registry,
        )
        agent = FitzSightAgent(
            planner=build_planner(args),
            engine=engine,
            verifier=EvidenceClaimVerifier(registry),
            registry=registry,
        )
        result = agent.run(args.question).to_dict()
        result["runtime"] = {"backend": store.backend, "data_dir": str(data_dir.resolve())}

    rendered = json.dumps(result, indent=2, ensure_ascii=False, default=str)
    print(rendered)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
