from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class PlanStep:
    step_id: str
    action: str
    purpose: str


@dataclass(frozen=True)
class InvestigationPlan:
    intent: str
    question: str
    steps: tuple[PlanStep, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Claim:
    claim_id: str
    text: str
    status: str
    confidence: str
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class ExecutionTraceStep:
    """Auditable execution outcome for one approved investigation action.

    The planner still publishes a bounded action catalog. The deterministic
    executor may execute or skip conditional actions based only on already
    observed tool results. No arbitrary SQL or free-form tool arguments are
    introduced by this trace.
    """

    step_id: str
    action: str
    status: str
    reason: str
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class InvestigationResult:
    product: str
    mode: str
    question: str
    plan: InvestigationPlan
    claims: tuple[Claim, ...]
    metrics: dict[str, Any]
    diagnosis: dict[str, Any]
    evidence: tuple[dict[str, Any], ...]
    execution_trace: tuple[ExecutionTraceStep, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
