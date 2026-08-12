import pytest

from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.tools.document_evidence import DocumentEvidenceTool, approved_document_catalog


def test_approved_synthetic_document_paragraph_is_evidence_linked():
    registry = EvidenceRegistry()
    tool = DocumentEvidenceTool(registry)
    result = tool.lookup("CRM-CHANGE-2026-0715", "p1")

    assert result.data["source_ref"] == "CRM-CHANGE-2026-0715#p1"
    assert result.data["source_type"] == "synthetic_operational_document"
    record = registry.get(result.evidence_id)
    assert record.tool_name == "document_evidence"
    assert record.status == "success"
    assert len(approved_document_catalog()) == 3


def test_document_tool_rejects_arbitrary_source_ids():
    registry = EvidenceRegistry()
    tool = DocumentEvidenceTool(registry)
    with pytest.raises(KeyError):
        tool.lookup("../../private", "p1")
    record = registry.records()[-1]
    assert record.tool_name == "document_evidence"
    assert record.status == "error"
