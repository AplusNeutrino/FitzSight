import json
from pathlib import Path


def test_v06_benchmark_catalog_has_three_distinct_supported_intents():
    root = Path(__file__).resolve().parents[1]
    catalog = json.loads(
        (root / "evaluation" / "benchmark_catalog.json").read_text(encoding="utf-8")
    )
    intents = [scenario["intent"] for scenario in catalog["scenarios"]]
    assert catalog["catalog_version"] == "0.6"
    assert intents == [
        "crm_routing_ftd_investigation",
        "net_deposit_anomaly_investigation",
        "customer_intelligence_segmentation",
    ]
