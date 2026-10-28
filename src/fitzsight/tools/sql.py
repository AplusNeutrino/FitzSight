from __future__ import annotations

import math
import re
from typing import Any

from fitzsight.data.store import AnalyticsStore
from fitzsight.evidence.registry import EvidenceRegistry
from .base import ToolResult


class SQLSafetyError(ValueError):
    """Raised when a query violates FitzSight's read-only SQL policy."""


_BLOCKED_KEYWORDS = {
    "ALTER", "ATTACH", "CALL", "COPY", "CREATE", "DELETE", "DETACH",
    "DROP", "EXECUTE", "EXPORT", "GRANT", "IMPORT", "INSERT", "INSTALL",
    "LOAD", "MERGE", "PRAGMA", "PREPARE", "REPLACE", "RESET", "REVOKE",
    "SET", "TRUNCATE", "UPDATE", "VACUUM",
}
_BLOCKED_EXTERNAL_FUNCTIONS = {
    "read_csv", "read_csv_auto", "read_json", "read_json_auto", "read_parquet",
    "parquet_scan", "csv_scan", "sqlite_scan", "postgres_scan", "mysql_scan",
    "delta_scan", "iceberg_scan", "glob", "httpfs",
}


def _strip_trailing_semicolon(sql: str) -> str:
    stripped = sql.strip()
    if stripped.endswith(";"):
        stripped = stripped[:-1].rstrip()
    return stripped


def validate_read_only_sql(sql: str) -> str:
    if not isinstance(sql, str) or not sql.strip():
        raise SQLSafetyError("SQL query must be a non-empty string")
    if "--" in sql or "/*" in sql or "*/" in sql:
        raise SQLSafetyError("SQL comments are not allowed in read-only tool queries")

    normalized = _strip_trailing_semicolon(sql)
    if ";" in normalized:
        raise SQLSafetyError("Multiple SQL statements are not allowed")

    first = re.match(r"^\s*([A-Za-z]+)", normalized)
    if first is None or first.group(1).upper() not in {"SELECT", "WITH"}:
        raise SQLSafetyError("Only SELECT/WITH queries are allowed")

    tokens = {token.upper() for token in re.findall(r"\b[A-Za-z_]+\b", normalized)}
    blocked = sorted(tokens & _BLOCKED_KEYWORDS)
    if blocked:
        raise SQLSafetyError(f"Blocked SQL keyword(s): {', '.join(blocked)}")

    lowered = normalized.lower()
    for function_name in _BLOCKED_EXTERNAL_FUNCTIONS:
        if re.search(rf"\b{re.escape(function_name)}\s*\(", lowered):
            raise SQLSafetyError(f"External file/network function is not allowed: {function_name}")

    return normalized


class ReadOnlySQLTool:
    def __init__(
        self,
        store: AnalyticsStore,
        registry: EvidenceRegistry,
        *,
        max_rows: int = 5000,
    ) -> None:
        if max_rows <= 0:
            raise ValueError("max_rows must be positive")
        self.store = store
        self.registry = registry
        self.max_rows = max_rows

    def run(
        self,
        sql: str,
        *,
        parameters: tuple[Any, ...] | list[Any] | None = None,
        compact_evidence: bool = False,
        evidence_preview_rows: int = 20,
    ) -> ToolResult:
        if evidence_preview_rows < 0:
            raise ValueError("evidence_preview_rows must be non-negative")
        safe_sql = validate_read_only_sql(sql)
        # Snapshot primitive values before execution; never interpolate values into SQL.
        # Dates are supplied as explicit ISO strings by the caller, avoiding implicit
        # backend-specific datetime adapters. Identifiers cannot be bound as values.
        if parameters is not None and type(parameters) not in (tuple, list):
            raise ValueError("SQL parameters must be a tuple or list of primitive values")
        bound = None if parameters is None else tuple(parameters)
        for value in bound or ():
            if value is not None and type(value) not in (str, int, float, bool):
                raise ValueError("Unsupported SQL parameter type")
            if type(value) is float and not math.isfinite(value):
                raise ValueError("SQL parameters must be finite")
            if type(value) is int and not -(2**63) <= value < 2**63:
                raise ValueError("Integer SQL parameters must fit signed 64 bits")
        context = {"sql": safe_sql, "backend": self.store.backend, "max_rows": self.max_rows}
        if bound is not None:
            context["bound_parameters"] = list(bound)
        wrapped = (
            "SELECT * FROM (" + safe_sql + ") AS __fitzsight_safe_query "
            f"LIMIT {self.max_rows + 1}"
        )
        try:
            columns, rows = self.store.execute(wrapped) if bound is None else self.store.execute(wrapped, bound)
        except Exception as exc:  # backend errors become explicit failed evidence
            payload = {"error": type(exc).__name__, "message": str(exc)}
            record = self.registry.register(
                "read_only_sql",
                context,
                payload,
                status="error",
            )
            raise RuntimeError(f"SQL execution failed [{record.evidence_id}]: {exc}") from exc

        truncated = len(rows) > self.max_rows
        if truncated:
            rows = rows[: self.max_rows]

        records = [dict(zip(columns, row, strict=True)) for row in rows]
        payload: dict[str, Any] = {
            "columns": columns,
            "rows": records,
            "row_count": len(records),
            "truncated": truncated,
            "backend": self.store.backend,
        }
        evidence_payload = payload
        if compact_evidence:
            evidence_payload = {
                "columns": columns,
                "row_count": len(records),
                "truncated": truncated,
                "backend": self.store.backend,
                "rows_preview": records[:evidence_preview_rows],
                "preview_row_count": min(len(records), evidence_preview_rows),
                "full_result_digest": EvidenceRegistry.digest(payload),
                "evidence_mode": "compact_preview",
            }
        record = self.registry.register(
            "read_only_sql",
            {
                **context,
                "compact_evidence": compact_evidence,
            },
            evidence_payload,
        )
        return ToolResult(record.evidence_id, "read_only_sql", payload)
