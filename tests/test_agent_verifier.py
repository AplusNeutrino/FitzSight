from dataclasses import replace
from pathlib import Path

from fitzsight.agent.verifier import EvidenceClaimVerifier
from fitzsight.data.generator import GeneratorConfig, write_csv_bundle
from fitzsight.data.store import AnalyticsStore
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.investigation.engine import DeterministicInvestigationEngine
from fitzsight.tools.schema import SchemaInspectorTool
from fitzsight.tools.sql import ReadOnlySQLTool
from fitzsight.tools.statistics import StatisticalTestTool

QUESTION = "Why did European FTD conversion deteriorate after July 15?"


def _run(tmp_path: Path):
    data_dir = tmp_path / "data"
    write_csv_bundle(data_dir, GeneratorConfig(seed=20260811, n_customers=10_000, n_salespeople=50))
    registry = EvidenceRegistry()
    store = AnalyticsStore(data_dir, backend="sqlite")
    store.load_csv_directory()
    engine = DeterministicInvestigationEngine(
        schema_tool=SchemaInspectorTool(store, registry),
        sql_tool=ReadOnlySQLTool(store, registry, max_rows=5000),
        stats_tool=StatisticalTestTool(registry),
        registry=registry,
    )
    return store, registry, engine.investigate(QUESTION)


def test_verifier_accepts_current_evidence_graph(tmp_path):
    store, registry, result = _run(tmp_path)
    try:
        report = EvidenceClaimVerifier(registry).verify(result)
        assert report.passed is True
        assert report.verified_claims == len(result.claims)
        assert not report.violations
        assert registry.get(report.evidence_id).tool_name == "agent.verifier"
    finally:
        store.close()


def test_verifier_rejects_supported_claim_with_missing_evidence(tmp_path):
    store, registry, result = _run(tmp_path)
    try:
        bad_claim = replace(result.claims[0], evidence_ids=("E9999",))
        tampered = replace(result, claims=(bad_claim,) + result.claims[1:])
        report = EvidenceClaimVerifier(registry).verify(tampered)
        assert report.passed is False
        assert any("missing Evidence IDs" in violation for violation in report.violations)
    finally:
        store.close()


def test_verifier_rejects_unqualified_causal_overclaim(tmp_path):
    store, registry, result = _run(tmp_path)
    try:
        original = result.claims[0]
        bad_claim = replace(original, text="The CRM change caused by itself proves the conversion decline.")
        tampered = replace(result, claims=(bad_claim,) + result.claims[1:])
        report = EvidenceClaimVerifier(registry).verify(tampered)
        assert report.passed is False
        assert any("causal wording" in violation for violation in report.violations)
    finally:
        store.close()
