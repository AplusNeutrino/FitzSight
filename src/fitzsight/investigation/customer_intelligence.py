from __future__ import annotations

from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.tools.schema import SchemaInspectorTool
from fitzsight.tools.segmentation import CustomerSegmentationTool
from .models import Claim, InvestigationPlan, InvestigationResult, PlanStep


class CustomerIntelligenceInvestigationEngine:
    """Deterministic customer-value segmentation and profile investigation."""

    intent = "customer_intelligence_segmentation"

    def __init__(
        self,
        *,
        schema_tool: SchemaInspectorTool,
        segmentation_tool: CustomerSegmentationTool,
        registry: EvidenceRegistry,
    ) -> None:
        self.schema_tool = schema_tool
        self.segmentation_tool = segmentation_tool
        self.registry = registry

    @staticmethod
    def supports(question: str) -> bool:
        q = " ".join(question.lower().split())
        europe = any(token in q for token in ("europe", "european", "欧洲"))
        segmentation = any(
            token in q
            for token in (
                "customer segment",
                "customer segments",
                "segmentation",
                "segment customers",
                "customer intelligence",
                "high value customers",
                "high-value customers",
                "客户分群",
                "客户细分",
                "高价值客户",
            )
        )
        value = any(
            token in q
            for token in (
                "value",
                "deposit",
                "deposits",
                "contribute",
                "contribution",
                "价值",
                "入金",
                "贡献",
            )
        )
        return europe and segmentation and value

    @staticmethod
    def plan(question: str) -> InvestigationPlan:
        return InvestigationPlan(
            intent=CustomerIntelligenceInvestigationEngine.intent,
            question=question,
            steps=(
                PlanStep("S1", "inspect_customer_schema", "Confirm customer and behavioral transaction fields exist without using benchmark-only labels."),
                PlanStep("S2", "build_customer_behavior_features", "Aggregate observable deposits, withdrawals and trading activity per European customer."),
                PlanStep("S3", "segment_customer_value", "Apply a transparent deterministic behavioral-value scoring policy."),
                PlanStep("S4", "profile_segment_deposits", "Compare customer counts, deposits, net deposits and trading behavior across the derived segments."),
                PlanStep("S5", "compare_withdrawal_pressure", "Describe segment-level withdrawal pressure without inferring customer motives."),
                PlanStep("S6", "evidence_boundary", "Keep segmentation descriptive and outside credit, AML, suitability or adverse-action use."),
            ),
        )

    def investigate(self, question: str) -> InvestigationResult:
        if not self.supports(question):
            raise ValueError("Customer-intelligence engine received an unsupported question.")

        plan = self.plan(question)
        schema_evidence: list[str] = []
        required_by_table = {
            "customers": {"customer_id", "region", "acquisition_channel", "assigned_team"},
            "deposits": {"customer_id", "amount", "status"},
            "withdrawals": {"customer_id", "amount", "status"},
            "trades": {"customer_id", "volume"},
        }
        for table, required in required_by_table.items():
            result = self.schema_tool.run(table)
            schema_evidence.append(result.evidence_id)
            columns = {column["name"] for column in result.data["columns"]}
            missing = sorted(required - columns)
            if missing:
                raise RuntimeError(f"{table} schema missing required fields: {missing}")

        segmentation = self.segmentation_tool.run(region="Europe")
        data = segmentation.data
        profiles = data["profiles"]
        by_name = {profile["segment"]: profile for profile in profiles}
        high = by_name.get("High Value")
        low = by_name.get("Low Activity")
        top_deposit_segment = data["top_deposit_segment"]
        top_deposit_profile = by_name[top_deposit_segment]
        top_withdrawal_profile = max(
            profiles,
            key=lambda item: (item["withdrawal_share"], item["segment"]),
        )

        high_vs_low_multiple = None
        if high is not None and low is not None:
            denominator = float(low["avg_deposits"])
            if denominator > 0:
                high_vs_low_multiple = float(high["avg_deposits"] / denominator)

        metrics = {
            "segmentation": data,
            "top_deposit_segment": top_deposit_segment,
            "top_deposit_segment_share": float(data["top_deposit_segment_share"]),
            "top_withdrawal_segment": top_withdrawal_profile["segment"],
            "top_withdrawal_segment_share": float(top_withdrawal_profile["withdrawal_share"]),
            "high_value_vs_low_activity_avg_deposit_multiple": high_vs_low_multiple,
        }
        diagnosis = {
            "analysis_type": "customer_intelligence_segmentation",
            "root_cause_status": "descriptive_profile",
            "driver_type": "behavioral_value_segmentation",
            "segmentation_method": data["method"],
            "segmentation_coverage": data["coverage"],
            "segment_count": data["segment_count"],
            "top_deposit_segment": top_deposit_segment,
            "causal_language_guardrail": data["guardrail"],
        }

        claims: list[Claim] = [
            Claim(
                "S-C1",
                (
                    f"FitzSight segmented {data['customer_count']:,} European customers into "
                    f"{data['segment_count']} transparent behavioral-value groups with 100% coverage."
                ),
                "supported",
                "high",
                (*schema_evidence, segmentation.evidence_id),
            ),
            Claim(
                "S-C2",
                (
                    f"{top_deposit_segment} is the largest deposit-value segment, accounting for "
                    f"{data['top_deposit_segment_share']:.1%} of completed European deposits in the synthetic dataset."
                ),
                "supported",
                "high",
                (segmentation.evidence_id,),
            ),
        ]

        if high is not None and low is not None:
            claims.append(
                Claim(
                    "S-C3",
                    (
                        f"High Value customers average ${high['avg_deposits']:,.2f} in completed deposits, "
                        f"versus ${low['avg_deposits']:,.2f} for Low Activity customers."
                    ),
                    "supported",
                    "high",
                    (segmentation.evidence_id,),
                )
            )

        claims.extend(
            [
                Claim(
                    "S-C4",
                    (
                        f"{top_withdrawal_profile['segment']} accounts for the largest segment share of completed "
                        f"withdrawals ({top_withdrawal_profile['withdrawal_share']:.1%}); this is descriptive withdrawal "
                        "pressure, not evidence of customer motive or suspicious behavior."
                    ),
                    "supported_with_guardrail",
                    "medium",
                    (segmentation.evidence_id,),
                ),
                Claim(
                    "S-C5",
                    (
                        "The segmentation is a descriptive operational analytics layer and must not be used as an automated "
                        "credit, AML, suitability, eligibility or adverse-action decision."
                    ),
                    "supported_with_guardrail",
                    "high",
                    (segmentation.evidence_id,),
                ),
            ]
        )

        return InvestigationResult(
            product="FitzSight",
            mode="deterministic_customer_intelligence_v0.6",
            question=question,
            plan=plan,
            claims=tuple(claims),
            metrics=metrics,
            diagnosis=diagnosis,
            evidence=tuple(self.registry.to_dicts()),
        )
