from __future__ import annotations

import re
from typing import Any

from fitzsight.evidence.registry import EvidenceRegistry
from .base import ToolResult
from .sql import ReadOnlySQLTool

_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _identifier(value: str) -> str:
    if not _IDENTIFIER.fullmatch(value):
        raise ValueError(f"Unsafe identifier: {value!r}")
    return value


class ContributionAnalysisTool:
    """Evidence-linked rate decomposition by a categorical dimension.

    The tool decomposes an aggregate binary-rate change into per-segment
    performance and composition effects using a symmetric two-part decomposition:

      ΔR_i = ((w0_i + w1_i)/2) * (r1_i - r0_i)
           + ((r0_i + r1_i)/2) * (w1_i - w0_i)

    where w is the segment population share and r is the segment rate. Segment
    contributions sum (up to floating-point error) to the aggregate rate change.
    This makes the result useful for ranking drivers without pretending a simple
    subgroup rate change is itself an additive contribution.
    """

    def __init__(self, sql_tool: ReadOnlySQLTool, registry: EvidenceRegistry) -> None:
        self.sql_tool = sql_tool
        self.registry = registry

    @staticmethod
    def _where(fragment: str) -> str:
        if not isinstance(fragment, str) or not fragment.strip():
            raise ValueError("WHERE fragment must be non-empty")
        if ";" in fragment or "--" in fragment or "/*" in fragment:
            raise ValueError("Unsafe WHERE fragment")
        return fragment.strip()

    def binary_rate_by_dimension(
        self,
        *,
        table: str,
        dimension: str,
        outcome_column: str,
        baseline_where: str,
        current_where: str,
        baseline_label: str = "baseline",
        current_label: str = "current",
    ) -> ToolResult:
        table = _identifier(table)
        dimension = _identifier(dimension)
        outcome_column = _identifier(outcome_column)
        baseline_where = self._where(baseline_where)
        current_where = self._where(current_where)

        def query(where: str) -> ToolResult:
            sql = (
                f"SELECT {dimension} AS segment, COUNT(*) AS n, "
                f"SUM(CASE WHEN {outcome_column} THEN 1 ELSE 0 END) AS successes, "
                f"AVG(CASE WHEN {outcome_column} THEN 1.0 ELSE 0.0 END) AS rate "
                f"FROM {table} WHERE {where} GROUP BY {dimension} ORDER BY {dimension}"
            )
            return self.sql_tool.run(sql)

        baseline = query(baseline_where)
        current = query(current_where)

        bmap = {str(row["segment"]): row for row in baseline.data["rows"]}
        cmap = {str(row["segment"]): row for row in current.data["rows"]}
        segments = sorted(set(bmap) | set(cmap))

        total_b = sum(int(row.get("n") or 0) for row in bmap.values())
        total_c = sum(int(row.get("n") or 0) for row in cmap.values())
        if total_b <= 0 or total_c <= 0:
            raise ValueError("Both baseline and current cohorts must contain rows")

        total_success_b = sum(int(row.get("successes") or 0) for row in bmap.values())
        total_success_c = sum(int(row.get("successes") or 0) for row in cmap.values())
        overall_rate_b = total_success_b / total_b
        overall_rate_c = total_success_c / total_c
        overall_change_pp = (overall_rate_c - overall_rate_b) * 100

        rows: list[dict[str, Any]] = []
        for segment in segments:
            br = bmap.get(segment, {})
            cr = cmap.get(segment, {})
            bn = int(br.get("n") or 0)
            cn = int(cr.get("n") or 0)
            bs = int(br.get("successes") or 0)
            cs = int(cr.get("successes") or 0)
            b_rate = (bs / bn) if bn else 0.0
            c_rate = (cs / cn) if cn else 0.0
            bw = bn / total_b
            cw = cn / total_c

            performance = ((bw + cw) / 2.0) * (c_rate - b_rate)
            composition = ((b_rate + c_rate) / 2.0) * (cw - bw)
            contribution_pp = (performance + composition) * 100

            rows.append(
                {
                    "segment": segment,
                    "baseline_n": bn,
                    "current_n": cn,
                    "baseline_successes": bs,
                    "current_successes": cs,
                    "baseline_rate": b_rate,
                    "current_rate": c_rate,
                    "rate_change_pp": (c_rate - b_rate) * 100,
                    "baseline_weight": bw,
                    "current_weight": cw,
                    "performance_effect_pp": performance * 100,
                    "composition_effect_pp": composition * 100,
                    "total_contribution_pp": contribution_pp,
                }
            )

        rows.sort(key=lambda row: (row["total_contribution_pp"], row["segment"]))
        reconstructed = sum(row["total_contribution_pp"] for row in rows)
        payload = {
            "metric": f"binary_rate:{outcome_column}",
            "table": table,
            "dimension": dimension,
            "baseline_label": baseline_label,
            "current_label": current_label,
            "baseline_n": total_b,
            "current_n": total_c,
            "baseline_rate": overall_rate_b,
            "current_rate": overall_rate_c,
            "overall_change_pp": overall_change_pp,
            "reconstructed_change_pp": reconstructed,
            "reconstruction_error_pp": reconstructed - overall_change_pp,
            "segments": rows,
            "most_negative_segments": [
                row["segment"] for row in rows if row["total_contribution_pp"] < 0
            ][:3],
            "source_evidence_ids": [baseline.evidence_id, current.evidence_id],
            "method": "symmetric_rate_decomposition",
        }
        record = self.registry.register(
            "contribution_analysis.binary_rate_by_dimension",
            {
                "table": table,
                "dimension": dimension,
                "outcome_column": outcome_column,
                "baseline_where": baseline_where,
                "current_where": current_where,
                "baseline_label": baseline_label,
                "current_label": current_label,
            },
            payload,
        )
        return ToolResult(
            record.evidence_id,
            "contribution_analysis.binary_rate_by_dimension",
            payload,
        )
