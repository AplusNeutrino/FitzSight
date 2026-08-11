from __future__ import annotations

from fitzsight.investigation.models import InvestigationResult
from .models import FinalAnswer, VerificationReport


def render_verified_answer(
    result: InvestigationResult,
    verification: VerificationReport,
) -> FinalAnswer:
    """Render only previously verified claim text; never recompute metrics here."""

    if not verification.passed:
        return FinalAnswer(
            status="rejected_by_verifier",
            headline="FitzSight withheld the analytical answer because verification failed.",
            findings=(),
            evidence_ids=(verification.evidence_id,),
            guardrail=(
                "Resolve verifier violations before presenting the result as decision support."
            ),
        )

    findings = tuple(
        claim.text
        for claim in result.claims
        if claim.status in {"supported", "supported_with_guardrail"}
    )
    evidence_ids = tuple(
        dict.fromkeys(
            evidence_id
            for claim in result.claims
            if claim.status in {"supported", "supported_with_guardrail"}
            for evidence_id in claim.evidence_ids
        )
    )

    root_status = result.diagnosis.get("root_cause_status")
    driver_type = result.diagnosis.get("driver_type")
    if root_status == "supported_candidate" and driver_type == "observed_withdrawal_concentration":
        headline = "A supported financial-operations driver was identified."
    elif root_status == "supported_candidate":
        headline = "A supported root-cause candidate was identified."
    else:
        headline = "The available evidence is insufficient for a supported driver/root-cause candidate."

    return FinalAnswer(
        status="verified",
        headline=headline,
        findings=findings,
        evidence_ids=evidence_ids,
        guardrail=str(result.diagnosis.get("causal_language_guardrail", "")),
    )
