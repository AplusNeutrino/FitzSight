from fitzsight.evidence.registry import EvidenceRegistry


def test_evidence_ids_and_digest_are_traceable():
    registry = EvidenceRegistry()
    first = registry.register("demo", {"x": 1}, {"value": 10})
    second = registry.register("demo", {"x": 2}, {"value": 20})

    assert first.evidence_id == "E0001"
    assert second.evidence_id == "E0002"
    assert registry.get("E0001").result == {"value": 10}
    assert first.result_digest == EvidenceRegistry.digest({"value": 10})
