from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fitzsight.data.generator import GeneratorConfig, write_csv_bundle
from fitzsight.data.store import AnalyticsStore
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.investigation.engine import DeterministicInvestigationEngine
from fitzsight.tools.schema import SchemaInspectorTool
from fitzsight.tools.sql import ReadOnlySQLTool
from fitzsight.tools.statistics import StatisticalTestTool

DEFAULT_QUESTION = "Why did European FTD conversion deteriorate after July 15?"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the FitzSight v0.2 deterministic investigation.")
    parser.add_argument("--question", default=DEFAULT_QUESTION)
    parser.add_argument("--data-dir", default=str(ROOT / "data" / "generated"))
    parser.add_argument("--backend", choices=["auto", "duckdb", "sqlite"], default="auto")
    parser.add_argument("--output", default=None, help="Optional JSON output path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_dir = Path(args.data_dir)
    if not (data_dir / "sales_activity.csv").exists():
        write_csv_bundle(data_dir, GeneratorConfig())

    registry = EvidenceRegistry()
    with AnalyticsStore(data_dir, backend=args.backend) as store:
        store.load_csv_directory()
        sql_tool = ReadOnlySQLTool(store, registry, max_rows=5000)
        engine = DeterministicInvestigationEngine(
            schema_tool=SchemaInspectorTool(store, registry),
            sql_tool=sql_tool,
            stats_tool=StatisticalTestTool(registry),
            registry=registry,
        )
        result = engine.investigate(args.question).to_dict()
        result["runtime"] = {"backend": store.backend, "data_dir": str(data_dir.resolve())}

    rendered = json.dumps(result, indent=2, ensure_ascii=False, default=str)
    print(rendered)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
