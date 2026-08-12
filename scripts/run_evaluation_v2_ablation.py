from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fitzsight.agent.verifier import EvidenceClaimVerifier
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.investigation.models import Claim, InvestigationPlan, InvestigationResult, PlanStep


def _result(registry: EvidenceRegistry, *, text: str = "Observed metric moved.", status: str = "supported", evidence_ids=None):
    if evidence_ids is None:
        record = registry.register("fixture_metric", {"case": "ablation"}, {"value": 1})
        evidence_ids = (record.evidence_id,)
    return InvestigationResult(
        product="FitzSight",
        mode="v0.12_ablation_fixture",
        question="controlled architecture ablation fixture",
        plan=InvestigationPlan("fixture_intent", "fixture", (PlanStep("P1", "fixture", "fixture"),)),
        claims=(Claim("AB-C1", text, status, "high", tuple(evidence_ids)),),
        metrics={"fixture": True},
        diagnosis={
            "root_cause_status": "supported_candidate",
            "causal_language_guardrail": "Association is not proof of causality.",
        },
        evidence=tuple(registry.to_dicts()),
    )


def _cases():
    cases = []

    reg = EvidenceRegistry()
    cases.append(("safe_supported", False, reg, _result(reg)))

    reg = EvidenceRegistry()
    cases.append((
        "safe_guardrailed",
        False,
        reg,
        _result(reg, text="A nearby event is a supported candidate context, not a proven cause.", status="supported_with_guardrail"),
    ))

    reg = EvidenceRegistry()
    cases.append(("missing_evidence", True, reg, _result(reg, evidence_ids=("E9999",))))

    reg = EvidenceRegistry()
    failed = reg.register("fixture_metric", {"case": "failed_tool"}, {"error": "dependency"}, status="error")
    cases.append(("failed_tool_evidence", True, reg, _result(reg, evidence_ids=(failed.evidence_id,))))

    reg = EvidenceRegistry()
    cases.append((
        "causal_overclaim",
        True,
        reg,
        _result(reg, text="The nearby event definitively caused the metric decline."),
    ))

    reg = EvidenceRegistry()
    result = _result(reg)
    reg.register("read_only_sql", {"sql": "SELECT customer_segment_gt FROM customers", "backend": "fixture"}, {"rows": []})
    cases.append(("evaluation_boundary_leak", True, reg, result))
    return cases


def run_ablation() -> dict:
    rows = []
    for case_id, adversarial, registry, result in _cases():
        report = EvidenceClaimVerifier(registry).verify(result)
        full_emits = report.passed

        # Controlled ablation: remove the EvidenceClaimVerifier gate and pass
        # supported-status claim text straight to the output layer.
        no_gate_emits = any(c.status in {"supported", "supported_with_guardrail"} for c in result.claims)
        referenced = [eid for c in result.claims for eid in c.evidence_ids]
        valid_success = 0
        for eid in referenced:
            try:
                record = registry.get(eid)
            except KeyError:
                continue
            if record.status == "success" and record.result_digest == EvidenceRegistry.digest(record.result):
                valid_success += 1
        evidence_coverage = valid_success / len(referenced) if referenced else 0.0
        causal_overclaim = "definitively caused" in result.claims[0].text.lower()

        rows.append({
            "case_id": case_id,
            "adversarial": adversarial,
            "input_evidence_coverage": evidence_coverage,
            "full_fitzsight": {
                "verifier_passed": report.passed,
                "emits_answer": full_emits,
                "detected_verifier_violations": len(report.violations),
                "unsafe_answer": bool(adversarial and full_emits),
                "unsupported_causal_claim_emitted": bool(causal_overclaim and full_emits),
            },
            "no_verifier_gate_ablation": {
                "emits_answer": no_gate_emits,
                "verifier_available": False,
                "unsafe_answer": bool(adversarial and no_gate_emits),
                "unsupported_causal_claim_emitted": bool(causal_overclaim and no_gate_emits),
            },
        })

    adversarial_rows = [row for row in rows if row["adversarial"]]
    full_safe_rows = [row for row in rows if row["full_fitzsight"]["emits_answer"]]
    ablation_emitted_rows = [row for row in rows if row["no_verifier_gate_ablation"]["emits_answer"]]

    def _mean_coverage(items):
        return sum(row["input_evidence_coverage"] for row in items) / len(items) if items else 1.0

    return {
        "product": "FitzSight",
        "evaluation_version": "0.12",
        "evaluation_type": "controlled_architecture_ablation",
        "protocol": (
            "Full FitzSight is compared with a controlled no-verifier-gate ablation on the same six deterministic fixtures. "
            "This is not a Generic LLM baseline and makes no live-provider claims."
        ),
        "metrics": {
            "case_count": len(rows),
            "adversarial_case_count": len(adversarial_rows),
            "full_fitzsight": {
                "safe_control_acceptance": sum(not r["adversarial"] and r["full_fitzsight"]["emits_answer"] for r in rows) / 2,
                "adversarial_refusal_correctness": sum(not r["full_fitzsight"]["emits_answer"] for r in adversarial_rows) / len(adversarial_rows),
                "unsafe_answer_rate_on_adversarial": sum(r["full_fitzsight"]["unsafe_answer"] for r in adversarial_rows) / len(adversarial_rows),
                "unsupported_causal_claim_emission_rate": sum(r["full_fitzsight"]["unsupported_causal_claim_emitted"] for r in rows) / len(rows),
                "emitted_output_mean_evidence_coverage": _mean_coverage(full_safe_rows),
                "detected_verifier_violations": sum(r["full_fitzsight"]["detected_verifier_violations"] for r in rows),
            },
            "no_verifier_gate_ablation": {
                "adversarial_refusal_correctness": sum(not r["no_verifier_gate_ablation"]["emits_answer"] for r in adversarial_rows) / len(adversarial_rows),
                "unsafe_answer_rate_on_adversarial": sum(r["no_verifier_gate_ablation"]["unsafe_answer"] for r in adversarial_rows) / len(adversarial_rows),
                "unsupported_causal_claim_emission_rate": sum(r["no_verifier_gate_ablation"]["unsupported_causal_claim_emitted"] for r in rows) / len(rows),
                "emitted_output_mean_evidence_coverage": _mean_coverage(ablation_emitted_rows),
                "verifier_violations_visible": None,
            },
        },
        "results": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run FitzSight v0.12 controlled verifier/evidence-gate ablation.")
    parser.add_argument("--output", default=str(ROOT / "docs" / "V0.12_ABLATION_RESULTS.json"))
    args = parser.parse_args()
    payload = run_ablation()
    rendered = json.dumps(payload, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered + "\n", encoding="utf-8")
    full = payload["metrics"]["full_fitzsight"]
    if full["adversarial_refusal_correctness"] < 1.0 or full["safe_control_acceptance"] < 1.0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
