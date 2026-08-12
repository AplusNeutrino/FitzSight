from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any

import numpy as np

from fitzsight.data.scenarios import CRM_ROUTING_SCENARIO
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.tools.anomaly import AnomalyDetectionTool
from fitzsight.tools.contribution import ContributionAnalysisTool
from fitzsight.tools.document_evidence import DocumentEvidenceTool
from fitzsight.tools.schema import SchemaInspectorTool
from fitzsight.tools.sql import ReadOnlySQLTool
from fitzsight.tools.statistics import StatisticalTestTool
from .models import Claim, ExecutionTraceStep, InvestigationPlan, InvestigationResult, PlanStep


class UnsupportedQuestionError(ValueError):
    """Raised when the deterministic engine does not support a question."""


class DeterministicInvestigationEngine:
    """Deterministic FitzSight investigation engine.

    v0.3 extends the evidence-first v0.2 loop with additive rate-contribution
    decomposition and robust anomaly detection. It is intentionally still not an
    LLM Agent: all planning in this class is explicit and all numeric conclusions
    originate from deterministic tools.
    """

    def __init__(
        self,
        *,
        schema_tool: SchemaInspectorTool,
        sql_tool: ReadOnlySQLTool,
        stats_tool: StatisticalTestTool,
        registry: EvidenceRegistry,
        contribution_tool: ContributionAnalysisTool | None = None,
        anomaly_tool: AnomalyDetectionTool | None = None,
        document_tool: DocumentEvidenceTool | None = None,
    ) -> None:
        self.schema_tool = schema_tool
        self.sql_tool = sql_tool
        self.stats_tool = stats_tool
        self.registry = registry
        self.contribution_tool = contribution_tool or ContributionAnalysisTool(sql_tool, registry)
        self.anomaly_tool = anomaly_tool or AnomalyDetectionTool(registry)
        self.document_tool = document_tool or DocumentEvidenceTool(registry)

    @staticmethod
    def supports(question: str) -> bool:
        q = question.lower()
        return (
            ("ftd" in q or "conversion" in q or "转化" in q)
            and ("europe" in q or "european" in q or "欧洲" in q)
            and ("july" in q or "07-15" in q or "2026-07-15" in q or "7月15" in q or "7 月 15" in q)
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
                PlanStep("P4", "statistical_validation", "Test whether the affected conversion and response-time shifts are statistically distinguishable."),
                PlanStep("P5", "contribution_decomposition", "Decompose Europe-wide FTD-rate change by sales team and rank negative contributors."),
                PlanStep("P6", "anomaly_scan", "Compare post-change daily response-time medians against the robust pre-change baseline."),
                PlanStep("P7", "event_check", "Check nearby business events for a plausible operational explanation."),
                PlanStep("P8", "document_evidence_check", "Retrieve an approved synthetic operational-document paragraph to corroborate the routing-change context."),
                PlanStep("P9", "evidence_boundary", "Separate supported findings from causal overclaims."),
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

    @staticmethod
    def _daily_medians(rows: list[dict[str, Any]], value_column: str) -> tuple[list[str], list[float]]:
        by_day: dict[str, list[float]] = defaultdict(list)
        for row in rows:
            day = str(row["lead_created_at"])[:10]
            by_day[day].append(float(row[value_column]))
        labels = sorted(by_day)
        values = [float(np.median(by_day[label])) for label in labels]
        return labels, values

    def investigate(self, question: str) -> InvestigationResult:
        if not self.supports(question):
            raise UnsupportedQuestionError(
                "The deterministic engine currently supports the European FTD conversion / July 15 benchmark question only."
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

        # Explicitly avoid benchmark-only *_gt columns in normal investigation SQL.
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

        boundary = scenario.change_date.isoformat()
        contribution = self.contribution_tool.binary_rate_by_dimension(
            table="sales_activity",
            dimension="assigned_team",
            outcome_column="converted_ftd",
            baseline_where=f"region = 'Europe' AND lead_created_at < '{boundary}'",
            current_where=f"region = 'Europe' AND lead_created_at >= '{boundary}'",
            baseline_label="Europe pre-change",
            current_label="Europe post-change",
        )

        affected_change_pp = (ao["conversion"] - ap["conversion"]) * 100
        control_change_pp = (co["conversion"] - cp["conversion"]) * 100
        response_change = float(ao["median_response_minutes"]) - float(ap["median_response_minutes"])

        most_negative = contribution.data["segments"][0] if contribution.data["segments"] else None
        drilldown_trigger = bool(
            most_negative
            and affected_change_pp < 0
            and proportion_test.data["p_value"] < 0.05
        )
        branch_record = self.registry.register(
            "agent.branch_decision",
            {"after_action": "contribution_decomposition"},
            {
                "decision": "run_latency_anomaly_drilldown" if drilldown_trigger else "stop_at_insufficient_evidence",
                "approved_next_action": "anomaly_scan" if drilldown_trigger else None,
                "basis": {
                    "affected_conversion_change_pp": affected_change_pp,
                    "conversion_p_value": proportion_test.data["p_value"],
                    "top_negative_team_contributor": None if most_negative is None else most_negative["segment"],
                },
            },
        )

        response_anomaly_data: dict[str, Any]
        response_anomaly_evidence_id: str | None = None
        if drilldown_trigger:
            _pre_days, pre_daily_response = self._daily_medians(affected_pre, "response_time_minutes")
            post_days, post_daily_response = self._daily_medians(affected_post, "response_time_minutes")
            response_anomalies = self.anomaly_tool.baseline_threshold(
                baseline_values=pre_daily_response,
                current_values=post_daily_response,
                current_labels=post_days,
                direction="high",
                threshold=2.5,
            )
            response_anomaly_data = response_anomalies.data
            response_anomaly_evidence_id = response_anomalies.evidence_id
        else:
            response_anomaly_data = {
                "anomaly_count": 0,
                "current_n": 0,
                "status": "skipped_by_bounded_branch",
            }

        event_trigger = bool(
            drilldown_trigger
            and response_change > 0
            and response_test.data["p_value"] < 0.05
        )
        event_branch_record = self.registry.register(
            "agent.branch_decision",
            {"after_action": "anomaly_scan"},
            {
                "decision": "run_operational_context_check" if event_trigger else "withhold_operational_attribution",
                "approved_next_action": "event_check" if event_trigger else None,
                "basis": {
                    "response_median_change_minutes": response_change,
                    "response_p_value": response_test.data["p_value"],
                    "anomaly_count": response_anomaly_data["anomaly_count"],
                },
            },
        )

        matching_events: list[dict[str, Any]] = []
        event_evidence_id: str | None = None
        event_error_evidence_id: str | None = None
        event_status = "skipped_by_bounded_branch"
        if event_trigger:
            event_sql = (
                "SELECT event_id, date, event_type, region, affected_team, description "
                "FROM business_events WHERE region = 'Europe' "
                "AND date >= '2026-07-10' AND date <= '2026-07-20 23:59:59' ORDER BY date"
            )
            before_ids = {record.evidence_id for record in self.registry.records()}
            try:
                events = self.sql_tool.run(event_sql)
                event_evidence_id = events.evidence_id
                matching_events = [
                    row for row in events.data["rows"] if row.get("event_type") == scenario.event_type
                ]
                event_status = "executed"
            except RuntimeError:
                event_status = "tool_error_fail_closed"
                new_records = [
                    record
                    for record in self.registry.records()
                    if record.evidence_id not in before_ids and record.tool_name == "read_only_sql"
                ]
                if new_records:
                    event_error_evidence_id = new_records[-1].evidence_id

        document_data: dict[str, Any] | None = None
        document_evidence_id: str | None = None
        if matching_events:
            document = self.document_tool.lookup("CRM-CHANGE-2026-0715", "p1")
            document_data = document.data
            document_evidence_id = document.evidence_id

        evidence_boundary_record = self.registry.register(
            "agent.evidence_boundary",
            {"intent": "crm_routing_ftd_investigation"},
            {
                "event_check_status": event_status,
                "matching_operational_event_found": bool(matching_events),
                "document_source_ref": None if document_data is None else document_data["source_ref"],
                "policy": "Operational attribution is withheld unless quantitative evidence and approved operational context align.",
            },
        )

        metrics = {
            "change_date": scenario.change_date.isoformat(),
            "affected": {"pre": ap, "post": ao, "conversion_change_pp": affected_change_pp},
            "control": {"pre": cp, "post": co, "conversion_change_pp": control_change_pp},
            "affected_response_median_change_minutes": response_change,
            "conversion_test": proportion_test.data,
            "response_test": response_test.data,
            "team_contribution_analysis": contribution.data,
            "post_change_response_anomalies": response_anomaly_data,
            "nearby_business_events": matching_events,
            "document_evidence": document_data,
            "bounded_branching": {
                "drilldown_triggered": drilldown_trigger,
                "event_check_triggered": event_trigger,
                "event_check_status": event_status,
            },
        }

        diagnosis = {
            "affected_conversion_deteriorated": affected_change_pp < 0,
            "affected_response_time_increased": response_change > 0,
            "effect_stronger_than_control": affected_change_pp < control_change_pp,
            "conversion_shift_significant": proportion_test.data["p_value"] < 0.05,
            "response_shift_significant": response_test.data["p_value"] < 0.05,
            "matching_operational_event_found": bool(matching_events),
            "top_negative_team_contributor": None if most_negative is None else most_negative["segment"],
            "post_change_response_anomaly_count": response_anomaly_data["anomaly_count"],
            "document_evidence_found": document_data is not None,
            "root_cause_status": (
                "supported_candidate"
                if (
                    affected_change_pp < 0
                    and response_change > 0
                    and affected_change_pp < control_change_pp
                    and proportion_test.data["p_value"] < 0.05
                    and bool(matching_events)
                    and document_data is not None
                )
                else "insufficient_evidence"
            ),
            "causal_language_guardrail": (
                "The evidence supports the CRM routing change as the primary root-cause candidate in this synthetic benchmark; "
                "a real deployment should not convert temporal association into a causal claim without additional design/validation."
            ),
        }

        claims: list[Claim] = [
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
                tuple(
                    evidence_id
                    for evidence_id in (
                        event_evidence_id,
                        document_evidence_id,
                        affected_query.evidence_id,
                        proportion_test.evidence_id,
                        response_test.evidence_id,
                    )
                    if evidence_id is not None
                ),
            ),
        ]

        if most_negative is not None:
            claims.append(
                Claim(
                    "C5",
                    (
                        f"{most_negative['segment']} is the largest negative team-level contributor in the symmetric Europe FTD-rate decomposition "
                        f"({most_negative['total_contribution_pp']:.2f} pp contribution)."
                    ),
                    "supported",
                    "medium",
                    (contribution.evidence_id,),
                )
            )

        claims.append(
            Claim(
                "C6",
                (
                    f"{response_anomaly_data['anomaly_count']} of {response_anomaly_data['current_n']} post-change daily response-time medians "
                    "exceed the robust pre-change high-anomaly threshold."
                ),
                "supported" if response_anomaly_evidence_id else "insufficient_evidence",
                "medium" if response_anomaly_evidence_id else "low",
                () if response_anomaly_evidence_id is None else (response_anomaly_evidence_id,),
            )
        )

        execution_trace = (
            ExecutionTraceStep("P1", "inspect_schema", "executed", "Required operational fields were inspected.", (schema.evidence_id,)),
            ExecutionTraceStep("P2", "query_affected_cohort", "executed", "Affected Europe Team A+B cohort measured.", (affected_query.evidence_id,)),
            ExecutionTraceStep("P3", "query_control_cohort", "executed", "European control cohort measured.", (control_query.evidence_id,)),
            ExecutionTraceStep("P4", "statistical_validation", "executed", "Conversion and response-time shifts tested.", (proportion_test.evidence_id, response_test.evidence_id)),
            ExecutionTraceStep("P5", "contribution_decomposition", "executed", "Team contribution decomposition completed; result controls the next approved branch.", (contribution.evidence_id, branch_record.evidence_id)),
            ExecutionTraceStep(
                "P6",
                "anomaly_scan",
                "executed" if response_anomaly_evidence_id else "skipped",
                "Approved by contribution/statistical branch." if response_anomaly_evidence_id else "Skipped because the bounded drilldown trigger was not met.",
                () if response_anomaly_evidence_id is None else (response_anomaly_evidence_id, event_branch_record.evidence_id),
            ),
            ExecutionTraceStep(
                "P7",
                "event_check",
                event_status,
                "Operational event context checked after the latency/statistical signal." if event_status == "executed" else "Operational attribution withheld; event check was skipped or failed closed.",
                tuple(eid for eid in (event_evidence_id, event_error_evidence_id) if eid is not None),
            ),
            ExecutionTraceStep(
                "P8",
                "document_evidence_check",
                "executed" if document_evidence_id else "skipped",
                "Synthetic routing ticket paragraph linked by stable source reference." if document_evidence_id else "No matching approved operational event was available, so document corroboration was not asserted.",
                () if document_evidence_id is None else (document_evidence_id,),
            ),
            ExecutionTraceStep("P9", "evidence_boundary", "executed", "Fail-closed attribution boundary applied before verification.", (evidence_boundary_record.evidence_id,)),
        )

        return InvestigationResult(
            product="FitzSight",
            mode="deterministic_v0.12_bounded_adaptive",
            question=question,
            plan=plan,
            claims=tuple(claims),
            metrics=metrics,
            diagnosis=diagnosis,
            evidence=tuple(self.registry.to_dicts()),
            execution_trace=execution_trace,
        )
