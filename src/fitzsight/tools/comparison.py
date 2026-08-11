from __future__ import annotations

from fitzsight.evidence.registry import EvidenceRegistry
from .base import ToolResult
from .kpi import KPITool


class PeriodComparisonTool:
    def __init__(self, kpi_tool: KPITool, registry: EvidenceRegistry) -> None:
        self.kpi_tool = kpi_tool
        self.registry = registry

    def run(
        self,
        metric: str,
        *,
        current_where: str,
        baseline_where: str,
        current_label: str = "current",
        baseline_label: str = "baseline",
    ) -> ToolResult:
        current = self.kpi_tool.run(metric, where=current_where)
        baseline = self.kpi_tool.run(metric, where=baseline_where)
        current_value = float(current.data["value"])
        baseline_value = float(baseline.data["value"])
        absolute = current_value - baseline_value
        relative = None if baseline_value == 0 else absolute / baseline_value * 100
        payload = {
            "metric": metric,
            "current_label": current_label,
            "baseline_label": baseline_label,
            "current": current_value,
            "baseline": baseline_value,
            "absolute_change": absolute,
            "relative_change_pct": relative,
            "source_evidence_ids": [baseline.evidence_id, current.evidence_id],
        }
        record = self.registry.register(
            "period_comparison",
            {
                "metric": metric,
                "current_where": current_where,
                "baseline_where": baseline_where,
                "current_label": current_label,
                "baseline_label": baseline_label,
            },
            payload,
        )
        return ToolResult(record.evidence_id, "period_comparison", payload)
