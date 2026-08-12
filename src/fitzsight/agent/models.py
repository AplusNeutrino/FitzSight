from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class AgentPlanStep:
    step_id: str
    action: str
    purpose: str


@dataclass(frozen=True)
class AgentPlan:
    plan_version: str
    intent: str
    question: str
    planner_mode: str
    steps: tuple[AgentPlanStep, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VerificationCheck:
    check_id: str
    passed: bool
    message: str


@dataclass(frozen=True)
class VerificationReport:
    passed: bool
    verified_claims: int
    total_claims: int
    checks: tuple[VerificationCheck, ...]
    violations: tuple[str, ...]
    evidence_id: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FinalAnswer:
    status: str
    headline: str
    findings: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    guardrail: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FollowUpAnswer:
    status: str
    question: str
    answer: str
    evidence_ids: tuple[str, ...]
    evidence_record_id: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentRunResult:
    product: str
    mode: str
    question: str
    planner_mode: str
    plan: AgentPlan
    plan_evidence_id: str
    investigation: dict[str, Any]
    verification: VerificationReport
    final_answer: FinalAnswer
    final_answer_evidence_id: str
    audit_evidence: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
