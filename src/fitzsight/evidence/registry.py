from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from typing import Any


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    tool_name: str
    parameters: dict[str, Any]
    result_digest: str
    created_at: str
    status: str
    result: Any


class EvidenceRegistry:
    """Append-only evidence registry for tool executions.

    Each tool call receives an Evidence ID and a stable digest of the returned
    payload. The full compact payload is retained for demo traceability.
    """

    def __init__(self) -> None:
        self._records: list[EvidenceRecord] = []

    @staticmethod
    def digest(result: Any) -> str:
        encoded = json.dumps(result, sort_keys=True, default=str, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()[:16]

    def register(
        self,
        tool_name: str,
        parameters: dict[str, Any],
        result: Any,
        *,
        status: str = "success",
    ) -> EvidenceRecord:
        record = EvidenceRecord(
            evidence_id=f"E{len(self._records) + 1:04d}",
            tool_name=tool_name,
            parameters=parameters,
            result_digest=self.digest(result),
            created_at=datetime.now(timezone.utc).isoformat(),
            status=status,
            result=result,
        )
        self._records.append(record)
        return record

    def get(self, evidence_id: str) -> EvidenceRecord:
        for record in self._records:
            if record.evidence_id == evidence_id:
                return record
        raise KeyError(evidence_id)

    def records(self) -> tuple[EvidenceRecord, ...]:
        """Return an immutable snapshot of registered evidence records."""
        return tuple(self._records)

    def to_dicts(self) -> list[dict[str, Any]]:
        return [asdict(record) for record in self._records]
