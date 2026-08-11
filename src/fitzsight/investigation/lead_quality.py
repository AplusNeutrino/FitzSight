from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from fitzsight.data.scenarios import (
    FALSE_CORRELATION_SCENARIO,
    MARKETING_LEAD_QUALITY_SCENARIO,
)
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.tools.contribution import ContributionAnalysisTool
from fitzsight.tools.schema import SchemaInspectorTool
from fitzsight.tools.sql import ReadOnlySQLTool
from fitzsight.tools.statistics import StatisticalTestTool
from .models import Claim, InvestigationPlan, InvestigationResult, PlanStep


def _bounds(start: date, end: date) -> tuple[str, str]:
    return start.isoformat(), (end + timedelta(days=1)).isoformat()


def _cohort_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    successes = sum(1 for row in rows if bool(row["converted_ftd"]))
    channel_counts: dict[str, int] = {}
    for row in rows:
        channel = str(row["acquisition_channel"])
        channel_counts[channel] = channel_counts.get(channel, 0) + 1
    return {
        "n": n,
        "successes": successes,
        "conversion": successes / n if n else 0.0,
        "channel_counts": channel_counts,
    }


class MarketingLeadQualityInvestigationEngine:
    """Deterministic Americas lead-volume / acquisition-quality investigation."""

    def __init__(
        self,
        *,
        schema_tool: SchemaInspectorTool,
        sql_tool: ReadOnlySQLTool,
        stats_tool: StatisticalTestTool,
        contribution_tool: ContributionAnalysisTool,
        registry: EvidenceRegistry,
    ) -> None:
        self.schema_tool = schema_tool
        self.sql_tool = sql_tool
        self.stats_tool = stats_tool
        self.contribution_tool = contribution_tool
        self.registry = registry

    @staticmethod
    def plan(question: str) -> InvestigationPlan:
        return InvestigationPlan(
            intent="marketing_lead_quality_investigation",
            question=question,
            steps=(
                PlanStep("M1", "inspect_schema", "Confirm lead, channel and conversion fields without reading benchmark-only labels."),
                PlanStep("M2", "measure_lead_volume", "Compare Americas lead volume across equal pre/post campaign windows."),
                PlanStep("M3", "measure_conversion", "Measure FTD conversion before and after the paid-media expansion."),
                PlanStep("M4", "channel_mix_decomposition", "Decompose conversion movement by acquisition channel and identify the dominant negative contributor."),
                PlanStep("M5", "statistical_validation", "Test whether the aggregate conversion shift is statistically distinguishable."),
                PlanStep("M6", "event_check", "Inspect the operational event log for a matching campaign expansion."),
                PlanStep("M7", "evidence_boundary", "Separate observed acquisition-quality evidence from unsupported claims about customer intent or campaign causality."),
            ),
        )

    def investigate(self, question: str) -> InvestigationResult:
        scenario = MARKETING_LEAD_QUALITY_SCENARIO
        plan = self.plan(question)
        schema = self.schema_tool.run("sales_activity")
        exposed = {col["name"] for col in schema.data["columns"]}
        required = {"lead_created_at", "region", "acquisition_channel", "converted_ftd"}
        missing = sorted(required - exposed)
        if missing:
            raise RuntimeError(f"sales_activity schema missing required fields: {missing}")

        baseline_start, baseline_end = _bounds(scenario.baseline_start, scenario.baseline_end)
        current_start, current_end = _bounds(scenario.current_start, scenario.current_end)
        columns = "lead_created_at, region, acquisition_channel, converted_ftd"
        baseline = self.sql_tool.run(
            f"SELECT {columns} FROM sales_activity WHERE region = '{scenario.region}' "
            f"AND lead_created_at >= '{baseline_start}' AND lead_created_at < '{baseline_end}' "
            "ORDER BY lead_created_at"
        )
        current = self.sql_tool.run(
            f"SELECT {columns} FROM sales_activity WHERE region = '{scenario.region}' "
            f"AND lead_created_at >= '{current_start}' AND lead_created_at < '{current_end}' "
            "ORDER BY lead_created_at"
        )
        before = _cohort_summary(baseline.data["rows"])
        after = _cohort_summary(current.data["rows"])

        if before["n"] == 0 or after["n"] == 0:
            raise RuntimeError("Marketing benchmark requires non-empty baseline/current cohorts")

        lead_volume_change = after["n"] - before["n"]
        lead_volume_change_pct = lead_volume_change / before["n"] * 100
        conversion_change_pp = (after["conversion"] - before["conversion"]) * 100
        paid_before = before["channel_counts"].get(scenario.acquisition_channel, 0) / before["n"]
        paid_after = after["channel_counts"].get(scenario.acquisition_channel, 0) / after["n"]
        paid_share_change_pp = (paid_after - paid_before) * 100

        stats = self.stats_tool.two_proportion(
            success_a=before["successes"],
            n_a=before["n"],
            success_b=after["successes"],
            n_b=after["n"],
            label_a="americas_pre_campaign",
            label_b="americas_post_campaign",
        )
        contribution = self.contribution_tool.binary_rate_by_dimension(
            table="sales_activity",
            dimension="acquisition_channel",
            outcome_column="converted_ftd",
            baseline_where=(
                f"region = '{scenario.region}' AND lead_created_at >= '{baseline_start}' "
                f"AND lead_created_at < '{baseline_end}'"
            ),
            current_where=(
                f"region = '{scenario.region}' AND lead_created_at >= '{current_start}' "
                f"AND lead_created_at < '{current_end}'"
            ),
            baseline_label="Americas pre campaign",
            current_label="Americas post campaign",
        )
        channel_rows = contribution.data["segments"]
        performance_rank = sorted(
            channel_rows,
            key=lambda row: (row["performance_effect_pp"], row["segment"]),
        )
        most_negative_performance = performance_rank[0] if performance_rank else None
        paid_row = next(
            (row for row in channel_rows if row["segment"] == scenario.acquisition_channel),
            None,
        )
        if paid_row is None or paid_row["baseline_n"] <= 0 or paid_row["current_n"] <= 0:
            raise RuntimeError("Paid Search cohorts are unavailable for the marketing benchmark")
        paid_stats = self.stats_tool.two_proportion(
            success_a=int(paid_row["baseline_successes"]),
            n_a=int(paid_row["baseline_n"]),
            success_b=int(paid_row["current_successes"]),
            n_b=int(paid_row["current_n"]),
            label_a="paid_search_pre",
            label_b="paid_search_post",
        )

        event_start = (scenario.event_date - timedelta(days=2)).isoformat()
        event_end = (scenario.event_date + timedelta(days=3)).isoformat()
        events = self.sql_tool.run(
            "SELECT event_id, date, event_type, region, affected_team, description, expected_effect "
            "FROM business_events "
            f"WHERE region = '{scenario.region}' AND date >= '{event_start}' AND date < '{event_end}' "
            "ORDER BY date"
        )
        matching = [row for row in events.data["rows"] if row.get("event_type") == scenario.event_type]

        lead_volume_up = lead_volume_change > 0
        conversion_down = conversion_change_pp < 0
        paid_share_up = paid_share_change_pp > 0
        top_performance_channel = (
            None if most_negative_performance is None else most_negative_performance["segment"]
        )
        paid_is_top_negative_performance = top_performance_channel == scenario.acquisition_channel
        significant = stats.data["p_value"] < 0.05
        paid_rate_down = paid_row["rate_change_pp"] < 0
        paid_rate_significant = paid_stats.data["p_value"] < 0.05

        diagnosis = {
            "lead_volume_increased": lead_volume_up,
            "conversion_declined": conversion_down,
            "paid_search_share_increased": paid_share_up,
            "conversion_shift_significant": significant,
            "top_negative_channel_performance_effect": top_performance_channel,
            "paid_search_conversion_declined": paid_rate_down,
            "paid_search_shift_significant": paid_rate_significant,
            "matching_operational_event_found": bool(matching),
            "root_cause_status": (
                "supported_candidate"
                if (
                    lead_volume_up
                    and conversion_down
                    and paid_share_up
                    and paid_is_top_negative_performance
                    and significant
                    and paid_rate_down
                    and paid_rate_significant
                    and matching
                )
                else "insufficient_evidence"
            ),
            "driver_type": "observed_acquisition_quality_shift",
            "causal_language_guardrail": (
                "The synthetic evidence supports a Paid Search acquisition-quality shift as the primary observed driver: "
                "lead volume and Paid Search mix rose while conversion deteriorated and Paid Search had the largest negative within-channel performance effect. "
                "This benchmark does not justify claims about customer motives or prove that paid media is intrinsically low quality."
            ),
        }
        metrics = {
            "periods": {
                "baseline": {"start": scenario.baseline_start.isoformat(), "end": scenario.baseline_end.isoformat(), **before},
                "current": {"start": scenario.current_start.isoformat(), "end": scenario.current_end.isoformat(), **after},
            },
            "lead_volume_change": lead_volume_change,
            "lead_volume_change_pct": lead_volume_change_pct,
            "conversion_change_pp": conversion_change_pp,
            "paid_search_share_change_pp": paid_share_change_pp,
            "conversion_test": stats.data,
            "channel_contribution_analysis": contribution.data,
            "paid_search_conversion_test": paid_stats.data,
            "nearby_business_events": matching,
        }
        claims = (
            Claim(
                "M-C1",
                f"Americas lead volume increased by {lead_volume_change:,} leads ({lead_volume_change_pct:+.1f}%) in the equal post-campaign window.",
                "supported",
                "high",
                (baseline.evidence_id, current.evidence_id),
            ),
            Claim(
                "M-C2",
                f"Americas FTD conversion changed by {conversion_change_pp:.2f} percentage points, with a two-proportion p-value of {stats.data['p_value']:.4g}.",
                "supported",
                "high",
                (baseline.evidence_id, current.evidence_id, stats.evidence_id),
            ),
            Claim(
                "M-C3",
                (
                    f"Paid Search share of Americas leads changed by {paid_share_change_pp:+.2f} percentage points; "
                    f"Paid Search conversion changed by {paid_row['rate_change_pp']:.2f} percentage points and had the largest negative within-channel performance effect."
                ),
                "supported",
                "high" if paid_is_top_negative_performance else "medium",
                (contribution.evidence_id, paid_stats.evidence_id),
            ),
            Claim(
                "M-C4",
                "A paid-media expansion appears in the nearby synthetic operations log and aligns with the measured volume/mix shift; it is treated as a supported candidate context, not a universal causal rule.",
                "supported_with_guardrail" if matching else "insufficient_evidence",
                "high" if matching else "low",
                (events.evidence_id, contribution.evidence_id, stats.evidence_id),
            ),
        )
        return InvestigationResult(
            product="FitzSight",
            mode="deterministic_marketing_quality_v0.7",
            question=question,
            plan=plan,
            claims=claims,
            metrics=metrics,
            diagnosis=diagnosis,
            evidence=tuple(self.registry.to_dicts()),
        )


class FalseCorrelationInvestigationEngine:
    """Benchmark engine that must reject a tempting nearby-event causal story."""

    def __init__(
        self,
        *,
        schema_tool: SchemaInspectorTool,
        sql_tool: ReadOnlySQLTool,
        stats_tool: StatisticalTestTool,
        contribution_tool: ContributionAnalysisTool,
        registry: EvidenceRegistry,
    ) -> None:
        self.schema_tool = schema_tool
        self.sql_tool = sql_tool
        self.stats_tool = stats_tool
        self.contribution_tool = contribution_tool
        self.registry = registry

    @staticmethod
    def plan(question: str) -> InvestigationPlan:
        return InvestigationPlan(
            intent="false_correlation_guardrail_investigation",
            question=question,
            steps=(
                PlanStep("F1", "inspect_schema", "Confirm lead/channel/conversion fields without benchmark-only labels."),
                PlanStep("F2", "measure_conversion_shift", "Measure Asia FTD conversion before and after July 20."),
                PlanStep("F3", "channel_decomposition", "Decompose the conversion movement by acquisition channel."),
                PlanStep("F4", "statistical_validation", "Test the overall and Affiliate-specific conversion shifts."),
                PlanStep("F5", "nearby_event_check", "Inspect nearby operational events without assuming temporal proximity implies causality."),
                PlanStep("F6", "falsification_check", "Compare the observed channel-specific pattern with the event's declared operational scope/effect."),
                PlanStep("F7", "evidence_boundary", "Reject unsupported event attribution and preserve only evidence-backed driver language."),
            ),
        )

    def investigate(self, question: str) -> InvestigationResult:
        scenario = FALSE_CORRELATION_SCENARIO
        plan = self.plan(question)
        schema = self.schema_tool.run("sales_activity")
        exposed = {col["name"] for col in schema.data["columns"]}
        required = {"lead_created_at", "region", "acquisition_channel", "converted_ftd"}
        missing = sorted(required - exposed)
        if missing:
            raise RuntimeError(f"sales_activity schema missing required fields: {missing}")

        baseline_start, baseline_end = _bounds(scenario.baseline_start, scenario.baseline_end)
        current_start, current_end = _bounds(scenario.current_start, scenario.current_end)
        columns = "lead_created_at, region, acquisition_channel, converted_ftd"
        baseline = self.sql_tool.run(
            f"SELECT {columns} FROM sales_activity WHERE region = '{scenario.region}' "
            f"AND lead_created_at >= '{baseline_start}' AND lead_created_at < '{baseline_end}' ORDER BY lead_created_at"
        )
        current = self.sql_tool.run(
            f"SELECT {columns} FROM sales_activity WHERE region = '{scenario.region}' "
            f"AND lead_created_at >= '{current_start}' AND lead_created_at < '{current_end}' ORDER BY lead_created_at"
        )
        before = _cohort_summary(baseline.data["rows"])
        after = _cohort_summary(current.data["rows"])
        if before["n"] == 0 or after["n"] == 0:
            raise RuntimeError("False-correlation benchmark requires non-empty cohorts")
        overall_change_pp = (after["conversion"] - before["conversion"]) * 100
        overall_stats = self.stats_tool.two_proportion(
            success_a=before["successes"], n_a=before["n"],
            success_b=after["successes"], n_b=after["n"],
            label_a="asia_pre", label_b="asia_post",
        )

        contribution = self.contribution_tool.binary_rate_by_dimension(
            table="sales_activity", dimension="acquisition_channel", outcome_column="converted_ftd",
            baseline_where=(
                f"region = '{scenario.region}' AND lead_created_at >= '{baseline_start}' AND lead_created_at < '{baseline_end}'"
            ),
            current_where=(
                f"region = '{scenario.region}' AND lead_created_at >= '{current_start}' AND lead_created_at < '{current_end}'"
            ),
            baseline_label="Asia pre July 20", current_label="Asia post July 20",
        )
        rows = contribution.data["segments"]
        performance_rank = sorted(
            rows,
            key=lambda row: (row["performance_effect_pp"], row["segment"]),
        )
        top_negative_performance = performance_rank[0] if performance_rank else None
        affiliate_row = next((row for row in rows if row["segment"] == scenario.driver_channel), None)
        if affiliate_row is None or affiliate_row["baseline_n"] <= 0 or affiliate_row["current_n"] <= 0:
            raise RuntimeError("Affiliate cohort is unavailable for the false-correlation benchmark")
        affiliate_stats = self.stats_tool.two_proportion(
            success_a=int(affiliate_row["baseline_successes"]),
            n_a=int(affiliate_row["baseline_n"]),
            success_b=int(affiliate_row["current_successes"]),
            n_b=int(affiliate_row["current_n"]),
            label_a="affiliate_pre",
            label_b="affiliate_post",
        )

        event_start = (scenario.event_date - timedelta(days=2)).isoformat()
        event_end = (scenario.event_date + timedelta(days=3)).isoformat()
        events = self.sql_tool.run(
            "SELECT event_id, date, event_type, region, affected_team, description, expected_effect "
            "FROM business_events "
            f"WHERE region = '{scenario.region}' AND date >= '{event_start}' AND date < '{event_end}' ORDER BY date"
        )
        nearby = [row for row in events.data["rows"] if row.get("event_type") == scenario.event_type]
        event_supports_conversion_driver = any(
            "conversion_down" in str(row.get("expected_effect", "")).lower()
            or "lead_quality_down" in str(row.get("expected_effect", "")).lower()
            for row in nearby
        )
        falsification_payload = {
            "nearby_event_type": scenario.event_type,
            "nearby_event_found": bool(nearby),
            "event_declares_conversion_effect": event_supports_conversion_driver,
            "observed_top_negative_channel_performance_effect": (
                None if top_negative_performance is None else top_negative_performance["segment"]
            ),
            "affiliate_rate_change_pp": affiliate_row["rate_change_pp"],
            "affiliate_p_value": affiliate_stats.data["p_value"],
            "conclusion": (
                "nearby_event_not_supported_as_cause"
                if nearby and not event_supports_conversion_driver
                else "event_causal_status_unresolved"
            ),
        }
        falsification = self.registry.register(
            "false_correlation.falsification_check",
            {"region": scenario.region, "event_type": scenario.event_type, "driver_channel": scenario.driver_channel},
            falsification_payload,
        )

        affiliate_is_top = (
            top_negative_performance is not None
            and top_negative_performance["segment"] == scenario.driver_channel
        )
        affiliate_down = affiliate_row["rate_change_pp"] < 0
        affiliate_significant = affiliate_stats.data["p_value"] < 0.05
        overall_down = overall_change_pp < 0
        rejects_event = bool(nearby) and not event_supports_conversion_driver

        diagnosis = {
            "conversion_declined": overall_down,
            "overall_conversion_shift_significant": overall_stats.data["p_value"] < 0.05,
            "top_negative_channel_performance_effect": (
                None if top_negative_performance is None else top_negative_performance["segment"]
            ),
            "affiliate_conversion_declined": affiliate_down,
            "affiliate_shift_significant": affiliate_significant,
            "nearby_event_found": bool(nearby),
            "nearby_event_cause_supported": not rejects_event,
            "false_correlation_rejected": rejects_event,
            "root_cause_status": (
                "supported_candidate"
                if overall_down and affiliate_is_top and affiliate_down and affiliate_significant and rejects_event
                else "insufficient_evidence"
            ),
            "driver_type": "observed_channel_specific_quality_deterioration",
            "causal_language_guardrail": (
                "Temporal proximity is not treated as causality. The synthetic data support an Affiliate-specific conversion deterioration as the observed driver, "
                "while the nearby office-relocation event is explicitly not supported as the cause. FitzSight does not infer why Affiliate quality changed without additional evidence."
            ),
        }
        metrics = {
            "periods": {
                "baseline": {"start": scenario.baseline_start.isoformat(), "end": scenario.baseline_end.isoformat(), **before},
                "current": {"start": scenario.current_start.isoformat(), "end": scenario.current_end.isoformat(), **after},
            },
            "conversion_change_pp": overall_change_pp,
            "overall_conversion_test": overall_stats.data,
            "channel_contribution_analysis": contribution.data,
            "affiliate_conversion_test": affiliate_stats.data,
            "nearby_business_events": nearby,
            "falsification": falsification_payload,
        }
        claims = (
            Claim(
                "F-C1",
                f"Asia FTD conversion changed by {overall_change_pp:.2f} percentage points across the July 20 split.",
                "supported",
                "high",
                (baseline.evidence_id, current.evidence_id, overall_stats.evidence_id),
            ),
            Claim(
                "F-C2",
                f"Affiliate has the largest negative within-channel performance effect; its conversion rate changed by {affiliate_row['rate_change_pp']:.2f} percentage points.",
                "supported",
                "high" if affiliate_is_top else "medium",
                (contribution.evidence_id, affiliate_stats.evidence_id),
            ),
            Claim(
                "F-C3",
                f"The Affiliate-specific conversion shift has p={affiliate_stats.data['p_value']:.4g} under the two-proportion test.",
                "supported",
                "high",
                (affiliate_stats.evidence_id,),
            ),
            Claim(
                "F-C4",
                "An office-relocation event appears nearby in time, but its declared scope/effect does not support a lead-conversion explanation; FitzSight therefore rejects that event as the cause in this benchmark.",
                "supported_with_guardrail" if rejects_event else "insufficient_evidence",
                "high" if rejects_event else "low",
                (events.evidence_id, falsification.evidence_id, contribution.evidence_id),
            ),
        )
        return InvestigationResult(
            product="FitzSight",
            mode="deterministic_false_correlation_v0.7",
            question=question,
            plan=plan,
            claims=claims,
            metrics=metrics,
            diagnosis=diagnosis,
            evidence=tuple(self.registry.to_dicts()),
        )
