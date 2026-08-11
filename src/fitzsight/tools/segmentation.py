from __future__ import annotations

from typing import Any

import pandas as pd

from fitzsight.evidence.registry import EvidenceRegistry
from .base import ToolResult
from .sql import ReadOnlySQLTool


SEGMENT_ORDER = ("High Value", "Growth", "Core", "Low Activity")


class CustomerSegmentationTool:
    """Transparent, deterministic behavioral-value segmentation.

    This tool deliberately avoids hidden benchmark labels (``*_gt``). It derives
    customer value from observable synthetic operations data only:

    - completed deposit value;
    - trading volume;
    - trading frequency.

    Customers with no deposit/trading activity are placed in ``Low Activity``.
    Active customers are scored using percentile ranks and split into transparent
    value bands. The method is intentionally interpretable for the competition
    demo; it is not a credit, AML, suitability, or adverse-action model.
    """

    method = "behavioral_value_score_v1"

    def __init__(self, sql_tool: ReadOnlySQLTool, registry: EvidenceRegistry) -> None:
        self.sql_tool = sql_tool
        self.registry = registry

    @staticmethod
    def _safe_region(region: str | None) -> str:
        if region is None:
            return ""
        cleaned = region.strip()
        if not cleaned:
            raise ValueError("region must be non-empty when provided")
        if any(token in cleaned for token in (";", "--", "/*", "*/", "'")):
            raise ValueError("Unsafe region value")
        return cleaned

    def run(self, *, region: str | None = None) -> ToolResult:
        region = self._safe_region(region)
        where = f"WHERE c.region = '{region}'" if region else ""
        sql = f"""
WITH dep AS (
    SELECT customer_id,
           COUNT(*) AS deposit_count,
           COALESCE(SUM(amount), 0) AS total_deposits
    FROM deposits
    WHERE status = 'completed'
    GROUP BY customer_id
),
wd AS (
    SELECT customer_id,
           COUNT(*) AS withdrawal_count,
           COALESCE(SUM(amount), 0) AS total_withdrawals
    FROM withdrawals
    WHERE status = 'completed'
    GROUP BY customer_id
),
tr AS (
    SELECT customer_id,
           COUNT(*) AS trade_count,
           COALESCE(SUM(volume), 0) AS trade_volume
    FROM trades
    GROUP BY customer_id
)
SELECT c.customer_id,
       c.region,
       c.acquisition_channel,
       c.assigned_team,
       COALESCE(dep.deposit_count, 0) AS deposit_count,
       COALESCE(dep.total_deposits, 0) AS total_deposits,
       COALESCE(wd.withdrawal_count, 0) AS withdrawal_count,
       COALESCE(wd.total_withdrawals, 0) AS total_withdrawals,
       COALESCE(tr.trade_count, 0) AS trade_count,
       COALESCE(tr.trade_volume, 0) AS trade_volume
FROM customers c
LEFT JOIN dep ON dep.customer_id = c.customer_id
LEFT JOIN wd ON wd.customer_id = c.customer_id
LEFT JOIN tr ON tr.customer_id = c.customer_id
{where}
ORDER BY c.customer_id
""".strip()
        raw = self.sql_tool.run(sql, compact_evidence=True, evidence_preview_rows=12)
        rows = raw.data["rows"]
        if not rows:
            raise ValueError("No customers available for segmentation")
        if raw.data.get("truncated"):
            raise RuntimeError(
                "Customer feature query was truncated; increase ReadOnlySQLTool.max_rows"
            )

        frame = pd.DataFrame(rows)
        numeric = (
            "deposit_count",
            "total_deposits",
            "withdrawal_count",
            "total_withdrawals",
            "trade_count",
            "trade_volume",
        )
        for column in numeric:
            frame[column] = pd.to_numeric(frame[column], errors="coerce").fillna(0.0)

        frame["net_deposits"] = frame["total_deposits"] - frame["total_withdrawals"]
        frame["withdrawal_ratio"] = (
            frame["total_withdrawals"] / frame["total_deposits"].where(frame["total_deposits"] > 0, 1.0)
        )
        frame["is_active"] = (
            (frame["total_deposits"] > 0)
            | (frame["trade_count"] > 0)
            | (frame["total_withdrawals"] > 0)
        )
        frame["value_score"] = 0.0
        frame["segment"] = "Low Activity"

        active = frame["is_active"]
        if active.any():
            active_frame = frame.loc[active].copy()
            dep_pct = active_frame["total_deposits"].rank(method="average", pct=True)
            vol_pct = active_frame["trade_volume"].rank(method="average", pct=True)
            count_pct = active_frame["trade_count"].rank(method="average", pct=True)
            score = 0.55 * dep_pct + 0.30 * vol_pct + 0.15 * count_pct
            frame.loc[active, "value_score"] = score
            frame.loc[active & (frame["value_score"] >= 0.75), "segment"] = "High Value"
            frame.loc[
                active & (frame["value_score"] >= 0.50) & (frame["value_score"] < 0.75),
                "segment",
            ] = "Growth"
            frame.loc[
                active & (frame["value_score"] < 0.50),
                "segment",
            ] = "Core"

        total_customers = int(len(frame))
        total_deposits = float(frame["total_deposits"].sum())
        total_withdrawals = float(frame["total_withdrawals"].sum())

        profiles: list[dict[str, Any]] = []
        samples: list[dict[str, Any]] = []
        for segment in SEGMENT_ORDER:
            subset = frame.loc[frame["segment"] == segment].copy()
            if subset.empty:
                continue
            segment_deposits = float(subset["total_deposits"].sum())
            segment_withdrawals = float(subset["total_withdrawals"].sum())
            segment_net = float(subset["net_deposits"].sum())
            profile = {
                "segment": segment,
                "customer_count": int(len(subset)),
                "customer_share": float(len(subset) / total_customers),
                "active_customer_count": int(subset["is_active"].sum()),
                "avg_value_score": float(subset["value_score"].mean()),
                "total_deposits": segment_deposits,
                "avg_deposits": float(subset["total_deposits"].mean()),
                "deposit_share": float(segment_deposits / total_deposits) if total_deposits else 0.0,
                "total_withdrawals": segment_withdrawals,
                "avg_withdrawals": float(subset["total_withdrawals"].mean()),
                "withdrawal_share": float(segment_withdrawals / total_withdrawals) if total_withdrawals else 0.0,
                "net_deposits": segment_net,
                "avg_net_deposits": float(subset["net_deposits"].mean()),
                "total_trade_volume": float(subset["trade_volume"].sum()),
                "avg_trade_volume": float(subset["trade_volume"].mean()),
                "avg_trade_count": float(subset["trade_count"].mean()),
                "avg_withdrawal_ratio": float(subset["withdrawal_ratio"].mean()),
            }
            profiles.append(profile)

            top = subset.sort_values(
                ["value_score", "total_deposits", "customer_id"],
                ascending=[False, False, True],
            ).head(3)
            for row in top.itertuples(index=False):
                samples.append(
                    {
                        "customer_id": str(row.customer_id),
                        "segment": segment,
                        "value_score": float(row.value_score),
                        "total_deposits": float(row.total_deposits),
                        "total_withdrawals": float(row.total_withdrawals),
                        "trade_volume": float(row.trade_volume),
                    }
                )

        if not profiles:
            raise RuntimeError("Segmentation produced no segment profiles")

        top_deposit = max(profiles, key=lambda item: (item["total_deposits"], item["segment"]))
        top_net = max(profiles, key=lambda item: (item["net_deposits"], item["segment"]))
        high_value = next((p for p in profiles if p["segment"] == "High Value"), None)
        low_activity = next((p for p in profiles if p["segment"] == "Low Activity"), None)

        payload = {
            "method": self.method,
            "region": region or "All",
            "customer_count": total_customers,
            "active_customer_count": int(frame["is_active"].sum()),
            "coverage": 1.0,
            "segment_count": len(profiles),
            "segment_order": list(SEGMENT_ORDER),
            "score_formula": {
                "deposit_percentile_weight": 0.55,
                "trade_volume_percentile_weight": 0.30,
                "trade_count_percentile_weight": 0.15,
                "high_value_threshold": 0.75,
                "growth_threshold": 0.50,
                "low_activity_rule": "no completed deposits, withdrawals, or trades",
            },
            "profiles": profiles,
            "top_deposit_segment": top_deposit["segment"],
            "top_deposit_segment_share": top_deposit["deposit_share"],
            "top_net_deposit_segment": top_net["segment"],
            "high_value_avg_deposits": None if high_value is None else high_value["avg_deposits"],
            "low_activity_avg_deposits": None if low_activity is None else low_activity["avg_deposits"],
            "sample_assignments": samples,
            "source_evidence_id": raw.evidence_id,
            "guardrail": (
                "Behavioral segments are descriptive analytical groupings only. They are not credit, AML, "
                "suitability, eligibility, or adverse-action decisions."
            ),
        }
        record = self.registry.register(
            "customer_segmentation.behavioral_value",
            {"region": region or "All", "method": self.method},
            payload,
        )
        return ToolResult(record.evidence_id, "customer_segmentation.behavioral_value", payload)
