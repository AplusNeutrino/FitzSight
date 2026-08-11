from __future__ import annotations

import re

from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.investigation.models import InvestigationResult
from .models import VerificationCheck, VerificationReport


_CAUSAL_OVERCLAIM = re.compile(
    r"\b(proves?|definitively caused|confirmed cause|caused by)\b",
    flags=re.IGNORECASE,
)


class EvidenceClaimVerifier:
    """Fail-closed verifier for evidence-linked Agent claims."""

    def __init__(self, registry: EvidenceRegistry) -> None:
        self.registry = registry

    def verify(self, result: InvestigationResult) -> VerificationReport:
        checks: list[VerificationCheck] = []
        violations: list[str] = []
        evidence_ids = {record.evidence_id for record in self.registry.records()}  # append-only registry

        def add(check_id: str, passed: bool, message: str) -> None:
            checks.append(VerificationCheck(check_id, passed, message))
            if not passed:
                violations.append(message)

        referenced: set[str] = set()
        verified_claims = 0
        for claim in result.claims:
            claim_ok = True
            if claim.status not in {"supported", "supported_with_guardrail", "insufficient_evidence"}:
                claim_ok = False
                add(f"claim_status:{claim.claim_id}", False, f"{claim.claim_id}: unsupported claim status {claim.status!r}")
            else:
                add(f"claim_status:{claim.claim_id}", True, f"{claim.claim_id}: claim status allowed")

            if claim.status.startswith("supported") and not claim.evidence_ids:
                claim_ok = False
                add(f"claim_evidence:{claim.claim_id}", False, f"{claim.claim_id}: supported claim has no evidence")
            else:
                missing = [eid for eid in claim.evidence_ids if eid not in evidence_ids]
                if missing:
                    claim_ok = False
                    add(
                        f"claim_evidence:{claim.claim_id}",
                        False,
                        f"{claim.claim_id}: missing Evidence IDs: {', '.join(missing)}",
                    )
                else:
                    add(f"claim_evidence:{claim.claim_id}", True, f"{claim.claim_id}: evidence references exist")

            for evidence_id in claim.evidence_ids:
                referenced.add(evidence_id)
                if evidence_id in evidence_ids:
                    record = self.registry.get(evidence_id)
                    digest_ok = record.result_digest == EvidenceRegistry.digest(record.result)
                    status_ok = record.status == "success"
                    if not digest_ok or not status_ok:
                        claim_ok = False
                    add(
                        f"evidence_integrity:{claim.claim_id}:{evidence_id}",
                        digest_ok and status_ok,
                        (
                            f"{claim.claim_id}/{evidence_id}: evidence integrity OK"
                            if digest_ok and status_ok
                            else f"{claim.claim_id}/{evidence_id}: evidence digest/status failed"
                        ),
                    )

            if claim.status == "supported_with_guardrail":
                guardrail = str(result.diagnosis.get("causal_language_guardrail", "")).strip()
                guardrail_ok = bool(guardrail)
                if not guardrail_ok:
                    claim_ok = False
                add(
                    f"guardrail:{claim.claim_id}",
                    guardrail_ok,
                    f"{claim.claim_id}: causal-language guardrail {'present' if guardrail_ok else 'missing'}",
                )

            if result.diagnosis.get("root_cause_status") != "confirmed" and _CAUSAL_OVERCLAIM.search(claim.text):
                claim_ok = False
                add(
                    f"causal_overclaim:{claim.claim_id}",
                    False,
                    f"{claim.claim_id}: causal wording exceeds current evidence status",
                )
            else:
                add(f"causal_overclaim:{claim.claim_id}", True, f"{claim.claim_id}: causal wording within policy")

            if claim_ok:
                verified_claims += 1

        # Normal Agent execution may never use benchmark-only *_gt fields.
        sql_records = [record for record in self.registry.records() if record.tool_name == "read_only_sql"]
        gt_leak = [
            record.evidence_id
            for record in sql_records
            if "_gt" in str(record.parameters.get("sql", "")).lower()
        ]
        add(
            "evaluation_boundary",
            not gt_leak,
            (
                "No evaluation-only *_gt columns were queried"
                if not gt_leak
                else f"Evaluation-only ground-truth fields appeared in SQL evidence: {', '.join(gt_leak)}"
            ),
        )

        # At least one factual claim must be backed by actual tool evidence.
        add(
            "nonempty_evidence_graph",
            bool(referenced),
            "Claims reference tool evidence" if referenced else "No claim-to-evidence links were produced",
        )

        passed = not violations and verified_claims == len(result.claims)
        payload = {
            "passed": passed,
            "verified_claims": verified_claims,
            "total_claims": len(result.claims),
            "violations": violations,
            "checks": [
                {"check_id": c.check_id, "passed": c.passed, "message": c.message}
                for c in checks
            ],
        }
        record = self.registry.register(
            "agent.verifier",
            {"claim_count": len(result.claims), "root_cause_status": result.diagnosis.get("root_cause_status")},
            payload,
            status="success" if passed else "error",
        )
        return VerificationReport(
            passed=passed,
            verified_claims=verified_claims,
            total_claims=len(result.claims),
            checks=tuple(checks),
            violations=tuple(violations),
            evidence_id=record.evidence_id,
        )
