from __future__ import annotations

from fitzsight.evidence.registry import EvidenceRegistry
from .base import ToolResult
from .sql import ReadOnlySQLTool


class KPITool:
    """Canonical KPI definitions executed through the read-only SQL tool."""

    SUPPORTED = {
        "ftd_conversion_rate",
        "total_deposits",
        "total_withdrawals",
        "trading_volume",
    }

    def __init__(self, sql_tool: ReadOnlySQLTool, registry: EvidenceRegistry) -> None:
        self.sql_tool = sql_tool
        self.registry = registry

    @staticmethod
    def _where(where: str | None) -> str:
        if where is None or not where.strip():
            return ""
        # The fragment remains inside the SQL safety validator when executed.
        if ";" in where or "--" in where or "/*" in where:
            raise ValueError("Unsafe WHERE fragment")
        return f" WHERE {where.strip()}"

    def run(self, metric: str, *, where: str | None = None) -> ToolResult:
        metric = metric.strip().lower()
        if metric not in self.SUPPORTED:
            raise ValueError(f"Unsupported KPI: {metric}")
        suffix = self._where(where)

        if metric == "ftd_conversion_rate":
            sql = (
                "SELECT COUNT(*) AS n, "
                "SUM(CASE WHEN converted_ftd THEN 1 ELSE 0 END) AS successes, "
                "AVG(CASE WHEN converted_ftd THEN 1.0 ELSE 0.0 END) AS value "
                "FROM sales_activity" + suffix
            )
        elif metric == "total_deposits":
            condition = "status = 'completed'"
            condition += f" AND ({where})" if where else ""
            sql = f"SELECT SUM(amount) AS value FROM deposits WHERE {condition}"
        elif metric == "total_withdrawals":
            condition = "status = 'completed'"
            condition += f" AND ({where})" if where else ""
            sql = f"SELECT SUM(amount) AS value FROM withdrawals WHERE {condition}"
        else:
            sql = "SELECT SUM(volume) AS value FROM trades" + suffix

        raw = self.sql_tool.run(sql)
        rows = raw.data["rows"]
        row = rows[0] if rows else {"value": None}
        value = row.get("value")
        payload = {
            "metric": metric,
            "value": 0.0 if value is None else float(value),
            "where": where,
            "source_evidence_id": raw.evidence_id,
        }
        if "n" in row:
            payload["n"] = int(row["n"])
        if "successes" in row:
            payload["successes"] = int(row["successes"] or 0)
        record = self.registry.register("kpi", {"metric": metric, "where": where}, payload)
        return ToolResult(record.evidence_id, "kpi", payload)
