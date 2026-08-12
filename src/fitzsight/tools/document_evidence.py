from __future__ import annotations

from dataclasses import dataclass

from fitzsight.evidence.registry import EvidenceRegistry
from .base import ToolResult


@dataclass(frozen=True)
class SyntheticDocumentParagraph:
    document_id: str
    paragraph_id: str
    title: str
    text: str
    source_type: str = "synthetic_operational_document"


# Small, explicit competition-safe corpus. This is deliberately not a RAG/vector
# database. Every paragraph is synthetic, versioned in code, and addressable by
# a stable source/paragraph ID so it can participate in the Evidence Registry.
_APPROVED_PARAGRAPHS: dict[tuple[str, str], SyntheticDocumentParagraph] = {
    ("CRM-CHANGE-2026-0715", "p1"): SyntheticDocumentParagraph(
        document_id="CRM-CHANGE-2026-0715",
        paragraph_id="p1",
        title="Synthetic CRM routing change ticket",
        text=(
            "Effective 2026-07-15, Europe Team A and Team B move to the revised lead-routing "
            "queue. Operations should monitor assignment-to-first-response latency and FTD conversion "
            "during the post-change period."
        ),
    ),
    ("KPI-FTD-001", "p1"): SyntheticDocumentParagraph(
        document_id="KPI-FTD-001",
        paragraph_id="p1",
        title="Synthetic FTD KPI definition",
        text=(
            "FTD conversion is the share of sales leads that reach first-time-deposit status within "
            "the synthetic benchmark observation window. It is an operational KPI, not an investment "
            "or customer-eligibility decision."
        ),
    ),
    ("OPS-EVIDENCE-001", "p1"): SyntheticDocumentParagraph(
        document_id="OPS-EVIDENCE-001",
        paragraph_id="p1",
        title="Synthetic operations evidence policy",
        text=(
            "A nearby operational change may be reported as a supported root-cause candidate only when "
            "metric movement, control comparison, statistical evidence, and operational context align. "
            "Temporal proximity alone is insufficient for a causal conclusion."
        ),
    ),
}


class DocumentEvidenceTool:
    """Lookup a paragraph from the fixed synthetic operational-document corpus.

    The tool accepts only approved document and paragraph IDs. It performs no
    network access, no arbitrary filesystem reads, and no semantic retrieval.
    """

    def __init__(self, registry: EvidenceRegistry) -> None:
        self.registry = registry

    def lookup(self, document_id: str, paragraph_id: str) -> ToolResult:
        key = (document_id, paragraph_id)
        paragraph = _APPROVED_PARAGRAPHS.get(key)
        if paragraph is None:
            payload = {
                "error": "document_paragraph_not_approved",
                "document_id": document_id,
                "paragraph_id": paragraph_id,
            }
            record = self.registry.register(
                "document_evidence",
                {"document_id": document_id, "paragraph_id": paragraph_id},
                payload,
                status="error",
            )
            raise KeyError(
                f"Document paragraph is outside the approved synthetic corpus [{record.evidence_id}]"
            )

        payload = {
            "document_id": paragraph.document_id,
            "paragraph_id": paragraph.paragraph_id,
            "source_ref": f"{paragraph.document_id}#{paragraph.paragraph_id}",
            "title": paragraph.title,
            "source_type": paragraph.source_type,
            "text": paragraph.text,
        }
        record = self.registry.register(
            "document_evidence",
            {"document_id": document_id, "paragraph_id": paragraph_id},
            payload,
        )
        return ToolResult(record.evidence_id, "document_evidence", payload)


def approved_document_catalog() -> tuple[SyntheticDocumentParagraph, ...]:
    return tuple(_APPROVED_PARAGRAPHS[key] for key in sorted(_APPROVED_PARAGRAPHS))
