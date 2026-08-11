from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.tools.anomaly import AnomalyDetectionTool


def test_robust_high_anomaly_detector_flags_extreme_value():
    registry = EvidenceRegistry()
    tool = AnomalyDetectionTool(registry)
    result = tool.baseline_threshold(
        baseline_values=[9, 10, 10, 10, 11, 10, 9.5],
        current_values=[10, 25, 9.5],
        current_labels=["normal", "spike", "normal2"],
        direction="high",
        threshold=3.0,
    )
    flagged = [row for row in result.data["observations"] if row["is_anomaly"]]
    assert [row["label"] for row in flagged] == ["spike"]
    assert result.data["anomaly_count"] == 1
    assert registry.get(result.evidence_id).tool_name == "anomaly_detection.baseline_threshold"
