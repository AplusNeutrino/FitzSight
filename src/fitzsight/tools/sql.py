from __future__ import annotations

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

    def run(self, sql: str) -> ToolResult:
        safe_sql = validate_read_only_sql(sql)
        wrapped = (
            "SELECT * FROM (" + safe_sql + ") AS __fitzsight_safe_query "
            f"LIMIT {self.max_rows + 1}"
        )
        try:
            columns, rows = self.store.execute(wrapped)
        except Exception as exc:  # backend errors become explicit failed evidence
            payload = {"error": type(exc).__name__, "message": str(exc)}
            record = self.registry.register(
                "read_only_sql",
                {"sql": safe_sql, "backend": self.store.backend, "max_rows": self.max_rows},
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
        record = self.registry.register(
            "read_only_sql",
            {"sql": safe_sql, "backend": self.store.backend, "max_rows": self.max_rows},
            payload,
        )
        return ToolResult(record.evidence_id, "read_only_sql", payload)
