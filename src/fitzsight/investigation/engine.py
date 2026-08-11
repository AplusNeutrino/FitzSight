from __future__ import annotations

from dataclasses import asdict
from datetime import date
from typing import Any

import numpy as np

from fitzsight.data.scenarios import CRM_ROUTING_SCENARIO
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.tools.schema import SchemaInspectorTool
from fitzsight.tools.sql import ReadOnlySQLTool
from fitzsight.tools.statistics import StatisticalTestTool
from .models import Claim, InvestigationPlan, InvestigationResult, PlanStep


class UnsupportedQuestionError(ValueError):
    """Raised when the deterministic v0.2 engine does not support a question."""


class DeterministicInvestigationEngine:
    """v0.2 deterministic investigation engine.

    This is intentionally *not* an LLM Agent. It proves the analytical tool and
    evidence loop before a language model is allowed to plan or narrate.
    """

    def __init__(
        self,
        *,
        schema_tool: SchemaInspectorTool,
        sql_tool: ReadOnlySQLTool,
        stats_tool: StatisticalTestTool,
        registry: EvidenceRegistry,
    ) -> None:
        self.schema_tool = schema_tool
        self.sql_tool = sql_tool
        self.stats_tool = stats_tool
        self.registry = registry

    @staticmethod
    def supports(question: str) -> bool:
        q = question.lower()
        return (
            ("ftd" in q or "conversion" in q or "转化" in q)
            and ("europe" in q or "european" in q or "欧洲" in q)
            and ("july" in q or "07-15" in q or "7月15" in q or "7 月 15" in q)
        )

    @staticmethod
    def plan(question: str) -> InvestigationPlan:
        return InvestigationPlan(
            intent="crm_routing_ftd_investigation",
            question=question,
            steps=(
                PlanStep("P1", "inspect_schema", "Confirm required operational fields exist without using evaluation-only ground-truth columns."),
                PlanStep("P2", "query_affected_cohort", "Measure pre/post FTD conversion and response time for Europe Team A+B."),
                PlanStep("P3", "query_control_cohort", "Measure the same metrics for other European teams."),
                PlanStep("P4", "statistical_validation", "Test whether the affected conversion shift is statistically distinguishable."),
                PlanStep("P5", "event_check", "Check nearby business events for a plausible operational explanation."),
                PlanStep("P6", "evidence_boundary", "Separate supported findings from causal overclaims."),
            ),
        )

    @staticmethod
    def _split_period(rows: list[dict[str, Any]], change_date: date) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        boundary = change_date.isoformat()
        pre = [row for row in rows if str(row["lead_created_at"])[:10] < boundary]
        post = [row for row in rows if str(row["lead_created_at"])[:10] >= boundary]
        return pre, post

    @staticmethod
    def _cohort_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
        if not rows:
            return {"n": 0, "successes": 0, "conversion": 0.0, "median_response_minutes": None}
        converted = [bool(row["converted_ftd"]) for row in rows]
        response = [float(row["response_time_minutes"]) for row in rows]
        successes = int(sum(converted))
        return {
            "n": len(rows),
            "successes": successes,
            "conversion": successes / len(rows),
            "median_response_minutes": float(np.median(response)),
        }

    def investigate(self, question: str) -> InvestigationResult:
        if not self.supports(question):
            raise UnsupportedQuestionError(
                "v0.2 deterministic engine currently supports the European FTD conversion / July 15 benchmark question only."
            )

        scenario = CRM_ROUTING_SCENARIO
        plan = self.plan(question)

        schema = self.schema_tool.run("sales_activity")
        exposed_columns = [col["name"] for col in schema.data["columns"]]
        required = {
            "lead_created_at",
            "region",
            "assigned_team",
            "response_time_minutes",
            "converted_ftd",
        }
        missing = sorted(required - set(exposed_columns))
        if missing:
            raise RuntimeError(f"sales_activity schema missing required fields: {missing}")

        # Explicitly avoid benchmark-only *_gt columns in the investigation query.
        select_columns = "lead_created_at, region, assigned_team, response_time_minutes, converted_ftd"
        affected_sql = (
            f"SELECT {select_columns} FROM sales_activity "
            "WHERE region = 'Europe' AND assigned_team IN ('Team A', 'Team B') "
            "ORDER BY lead_created_at"
        )
        control_sql = (
            f"SELECT {select_columns} FROM sales_activity "
            "WHERE region = 'Europe' AND assigned_team NOT IN ('Team A', 'Team B') "
            "ORDER BY lead_created_at"
        )
        affected_query = self.sql_tool.run(affected_sql)
        control_query = self.sql_tool.run(control_sql)

        affected_pre, affected_post = self._split_period(affected_query.data["rows"], scenario.change_date)
        control_pre, control_post = self._split_period(control_query.data["rows"], scenario.change_date)

        ap = self._cohort_metrics(affected_pre)
        ao = self._cohort_metrics(affected_post)
        cp = self._cohort_metrics(control_pre)
        co = self._cohort_metrics(control_post)

        proportion_test = self.stats_tool.two_proportion(
            success_a=ap["successes"],
            n_a=ap["n"],
            success_b=ao["successes"],
            n_b=ao["n"],
            label_a="affected_pre",
            label_b="affected_post",
        )
        response_test = self.stats_tool.continuous_two_sample(
            [float(row["response_time_minutes"]) for row in affected_pre],
            [float(row["response_time_minutes"]) for row in affected_post],
            method="mannwhitney",
            label_a="affected_pre",
            label_b="affected_post",
        )

        event_sql = (
            "SELECT event_id, date, event_type, region, affected_team, description "
            "FROM business_events WHERE region = 'Europe' "
            "AND date >= '2026-07-10' AND date <= '2026-07-20 23:59:59' ORDER BY date"
        )
        events = self.sql_tool.run(event_sql)
        matching_events = [
            row for row in events.data["rows"]
            if row.get("event_type") == scenario.event_type
        ]

        affected_change_pp = (ao["conversion"] - ap["conversion"]) * 100
        control_change_pp = (co["conversion"] - cp["conversion"]) * 100
        response_change = (
            float(ao["median_response_minutes"]) - float(ap["median_response_minutes"])
        )

        metrics = {
            "change_date": scenario.change_date.isoformat(),
            "affected": {"pre": ap, "post": ao, "conversion_change_pp": affected_change_pp},
            "control": {"pre": cp, "post": co, "conversion_change_pp": control_change_pp},
            "affected_response_median_change_minutes": response_change,
            "conversion_test": proportion_test.data,
            "response_test": response_test.data,
            "nearby_business_events": matching_events,
        }

        diagnosis = {
            "affected_conversion_deteriorated": affected_change_pp < 0,
            "affected_response_time_increased": response_change > 0,
            "effect_stronger_than_control": affected_change_pp < control_change_pp,
            "conversion_shift_significant": proportion_test.data["p_value"] < 0.05,
            "response_shift_significant": response_test.data["p_value"] < 0.05,
            "matching_operational_event_found": bool(matching_events),
            "root_cause_status": (
                "supported_candidate" if (
                    affected_change_pp < 0
                    and response_change > 0
                    and affected_change_pp < control_change_pp
                    and proportion_test.data["p_value"] < 0.05
                    and bool(matching_events)
                ) else "insufficient_evidence"
            ),
            "causal_language_guardrail": (
                "The evidence supports the CRM routing change as the primary root-cause candidate in this synthetic benchmark; "
                "a real deployment should not convert temporal association into a causal claim without additional design/validation."
            ),
        }

        claims = (
            Claim(
                "C1",
                f"Affected Europe Team A+B FTD conversion changed by {affected_change_pp:.2f} percentage points after {scenario.change_date.isoformat()}.",
                "supported",
                "high",
                (affected_query.evidence_id, proportion_test.evidence_id),
            ),
            Claim(
                "C2",
                f"Median response time in the affected cohort changed by {response_change:.2f} minutes.",
                "supported",
                "high",
                (affected_query.evidence_id, response_test.evidence_id),
            ),
            Claim(
                "C3",
                f"The European control cohort conversion changed by {control_change_pp:.2f} percentage points over the same split.",
                "supported",
                "high",
                (control_query.evidence_id,),
            ),
            Claim(
                "C4",
                "A CRM routing change is present in the nearby business-event log and is a supported root-cause candidate, not an automatically proven real-world causal conclusion.",
                "supported_with_guardrail" if matching_events else "insufficient_evidence",
                "high" if matching_events else "low",
                (events.evidence_id, affected_query.evidence_id, proportion_test.evidence_id, response_test.evidence_id),
            ),
        )

        return InvestigationResult(
            product="FitzSight",
            mode="deterministic_v0.2",
            question=question,
            plan=plan,
            claims=claims,
            metrics=metrics,
            diagnosis=diagnosis,
            evidence=tuple(self.registry.to_dicts()),
        )
