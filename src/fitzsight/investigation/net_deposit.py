from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from statistics import median
from typing import Any

from fitzsight.data.scenarios import NET_DEPOSIT_SCENARIO
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.metrics import get_metric, net_deposit_definitions
from fitzsight.tools.schema import SchemaInspectorTool
from fitzsight.tools.sql import ReadOnlySQLTool
from .numeric_claims import complete_sql_rows, NetChangeBinding, NetDecompositionBinding, render_net_change, render_net_decomposition
from .concentration_claims import ConcentrationBinding, render_concentration
from .regional_claims import RegionAmounts, RegionalBinding, render_regional
from .event_claims import EventBinding, event_query, render_event
from .cashflow_queries import cashflow_sql
from .regional_queries import regional_sql
from .models import Claim, InvestigationPlan, InvestigationResult, PlanStep


class NetDepositInvestigationEngine:
    """Deterministic engine for the second FitzSight financial-operations business intent."""

    intent = "net_deposit_anomaly_investigation"

    def __init__(
        self,
        *,
        schema_tool: SchemaInspectorTool,
        sql_tool: ReadOnlySQLTool,
        registry: EvidenceRegistry,
    ) -> None:
        self.schema_tool = schema_tool
        self.sql_tool = sql_tool
        self.registry = registry

    @staticmethod
    def supports(question: str) -> bool:
        q = " ".join(question.lower().split())
        return (
            any(token in q for token in ("net deposit", "net deposits", "net-deposit", "净入金", "净存款"))
            and any(token in q for token in ("europe", "european", "欧洲"))
            and any(token in q for token in ("august", "aug 3", "2026-08-03", "8月", "8 月", "week", "weekly", "本周", "这周"))
        )

    @staticmethod
    def plan(question: str) -> InvestigationPlan:
        return InvestigationPlan(
            intent=NetDepositInvestigationEngine.intent,
            question=question,
            steps=(
                PlanStep("N1", "inspect_schema", "Confirm customers, deposits, withdrawals, and event fields exist."),
                PlanStep("N2", "measure_period_net_deposits", "Measure Europe deposits, withdrawals, and net deposits in baseline/current weeks."),
                PlanStep("N3", "decompose_deposit_withdrawal_drivers", "Separate deposit-side and withdrawal-side contributions to the weekly net-deposit change."),
                PlanStep("N4", "identify_customer_concentration", "Measure how much current European withdrawal volume is concentrated in the largest customer withdrawals."),
                PlanStep("N5", "compare_regional_control", "Compare Europe's per-customer weekly net-deposit movement with other regions."),
                PlanStep("N6", "event_check", "Check nearby operational events for context."),
                PlanStep("N7", "evidence_boundary", "Report an observed driver without inventing why customers withdrew."),
            ),
        )

    @staticmethod
    def _period_bounds(start: date, end: date) -> tuple[str, str]:
        return start.isoformat(), (end + timedelta(days=1)).isoformat()

    @staticmethod
    def _sum_amount(rows: list[dict[str, Any]]) -> float:
        return float(sum(float(row["amount"]) for row in rows))

    def _money_rows(
        self,
        table: str,
        *,
        region: str | None,
        start: date,
        end: date,
    ):
        if table not in {"deposits", "withdrawals"}:
            raise ValueError("Unsupported cash-flow table")
        start_s, end_exclusive = self._period_bounds(start, end)
        parameters = [start_s, end_exclusive]
        if region is not None:
            parameters.append(region)
        sql = cashflow_sql(table, region_filter=region is not None)
        result = self.sql_tool.run(sql, parameters=parameters)
        if not complete_sql_rows(result.data):
            raise ValueError("Net-deposit amounts require complete SQL rows; truncated or incomplete result")
        if any(row["currency"] != "USD" for row in result.data["rows"]):
            raise ValueError("Net-deposit demo requires USD cash flows; currency conversion is not implemented")
        return result

    def _regional_net_per_customer(self, start: date, end: date):
        start_s, end_exclusive = self._period_bounds(start, end)
        deposit_sql = regional_sql("deposits")
        withdrawal_sql = regional_sql("withdrawals")
        deposits = self.sql_tool.run(deposit_sql, parameters=(start_s, end_exclusive))
        withdrawals = self.sql_tool.run(withdrawal_sql, parameters=(start_s, end_exclusive))
        if not all(complete_sql_rows(result.data) for result in (deposits, withdrawals)):
            raise ValueError("Regional comparison requires complete SQL rows; truncated or incomplete result")
        if any(row["invalid_currency_count"] for result in (deposits, withdrawals) for row in result.data["rows"]):
            raise ValueError("Regional net-deposit comparison requires USD cash flows")
        withdrawal_by_region = {
            row["region"]: float(row["withdrawals"] or 0.0)
            for row in withdrawals.data["rows"]
        }
        output = {}
        for row in deposits.data["rows"]:
            region = row["region"]
            customers = int(row["customer_count"] or 0)
            dep = float(row["deposits"] or 0.0)
            wd = withdrawal_by_region.get(region, 0.0)
            net = dep - wd
            output[region] = {
                "customer_count": customers,
                "deposits": dep,
                "withdrawals": wd,
                "net_deposits": net,
                "net_deposits_per_customer": net / customers if customers else None,
            }
        return output, (deposits.evidence_id, withdrawals.evidence_id)

    def investigate(self, question: str) -> InvestigationResult:
        if not self.supports(question):
            raise ValueError("Net-deposit engine received an unsupported question.")

        scenario = NET_DEPOSIT_SCENARIO
        plan = self.plan(question)

        # Schema checks are evidence-bearing and explicitly avoid *_gt fields.
        schema_evidence = []
        required_by_table = {
            "customers": {"customer_id", "region", "assigned_team"},
            "deposits": {"customer_id", "timestamp", "amount", "currency", "status"},
            "withdrawals": {"customer_id", "timestamp", "amount", "currency", "status"},
            "business_events": {"event_id", "date", "event_type", "region", "affected_team", "description"},
        }
        for table, required in required_by_table.items():
            result = self.schema_tool.run(table)
            schema_evidence.append(result.evidence_id)
            columns = {column["name"] for column in result.data["columns"]}
            missing = sorted(required - columns)
            if missing:
                raise RuntimeError(f"{table} schema missing required fields: {missing}")

        baseline_dep = self._money_rows(
            "deposits",
            region=scenario.region,
            start=scenario.baseline_start,
            end=scenario.baseline_end,
        )
        baseline_wd = self._money_rows(
            "withdrawals",
            region=scenario.region,
            start=scenario.baseline_start,
            end=scenario.baseline_end,
        )
        current_dep = self._money_rows(
            "deposits",
            region=scenario.region,
            start=scenario.current_start,
            end=scenario.current_end,
        )
        current_wd = self._money_rows(
            "withdrawals",
            region=scenario.region,
            start=scenario.current_start,
            end=scenario.current_end,
        )

        baseline_deposits = self._sum_amount(baseline_dep.data["rows"])
        baseline_withdrawals = self._sum_amount(baseline_wd.data["rows"])
        current_deposits = self._sum_amount(current_dep.data["rows"])
        current_withdrawals = self._sum_amount(current_wd.data["rows"])

        baseline_net = baseline_deposits - baseline_withdrawals
        current_net = current_deposits - current_withdrawals
        net_change = current_net - baseline_net
        deposit_change = current_deposits - baseline_deposits
        withdrawal_change = current_withdrawals - baseline_withdrawals

        driver_payload = {
            "baseline_net_deposits": baseline_net,
            "current_net_deposits": current_net,
            "net_change": net_change,
            "deposit_change": deposit_change,
            "withdrawal_change": withdrawal_change,
            "identity_check": net_change - (deposit_change - withdrawal_change),
        }
        metric = get_metric("net_deposits.v1")
        driver_record = self.registry.register(
            "net_deposit_driver_decomposition",
            {
                "currency": metric.currency,
                "metric_definitions": net_deposit_definitions(),
                "source_evidence_ids": [baseline_dep.evidence_id, baseline_wd.evidence_id,
                                        current_dep.evidence_id, current_wd.evidence_id],
                "region": scenario.region,
                "baseline_start": scenario.baseline_start.isoformat(),
                "baseline_end": scenario.baseline_end.isoformat(),
                "current_start": scenario.current_start.isoformat(),
                "current_end": scenario.current_end.isoformat(),
            },
            driver_payload,
        )

        # Rank current-week European withdrawals by customer using an explicit
        # deterministic SQL aggregation. No hidden ground-truth fields are queried.
        current_start, current_end_exclusive = self._period_bounds(
            scenario.current_start, scenario.current_end
        )
        concentration_sql = (
            "SELECT w.customer_id, c.assigned_team, SUM(CAST(w.amount AS DOUBLE)) AS withdrawal_amount "
            "FROM withdrawals w JOIN customers c ON c.customer_id = w.customer_id "
            "WHERE w.status = 'completed' AND c.region = 'Europe' "
            f"AND w.timestamp >= '{current_start}' AND w.timestamp < '{current_end_exclusive}' "
            "GROUP BY w.customer_id, c.assigned_team "
            "ORDER BY withdrawal_amount DESC, w.customer_id ASC"
        )
        concentration_query = self.sql_tool.run(concentration_sql)
        ranked = concentration_query.data["rows"]
        top_n = ranked[: scenario.customer_count]
        top_n_amount = float(sum(float(row["withdrawal_amount"]) for row in top_n))
        concentration_share = (
            top_n_amount / current_withdrawals if current_withdrawals > 0 else None
        )
        concentration_payload = {
            "customer_count": scenario.customer_count,
            "top_customer_withdrawal_amount": top_n_amount,
            "current_total_withdrawals": current_withdrawals,
            "share_of_current_withdrawals": concentration_share,
            "calculation_status": "computed" if concentration_share is not None else "unavailable",
            "unavailable_reason": None if concentration_share is not None else "nonpositive_total_withdrawals",
            "top_customers": top_n,
        }
        concentration_record = self.registry.register(
            "withdrawal_customer_concentration",
            {"region": scenario.region, "period_start": current_start,
             "period_end_exclusive": current_end_exclusive, "currency": "USD",
             "customer_count": scenario.customer_count, "source_evidence_id": current_wd.evidence_id},
            concentration_payload,
        )

        baseline_regions, baseline_region_evidence = self._regional_net_per_customer(
            scenario.baseline_start, scenario.baseline_end
        )
        current_regions, current_region_evidence = self._regional_net_per_customer(
            scenario.current_start, scenario.current_end
        )
        regional_changes = {}
        for region in sorted(set(baseline_regions) | set(current_regions)):
            before = baseline_regions.get(region, {}).get("net_deposits_per_customer")
            after = current_regions.get(region, {}).get("net_deposits_per_customer")
            regional_changes[region] = float(after) - float(before) if before is not None and after is not None else None

        other_changes = [
            value for region, value in regional_changes.items() if region != scenario.region and value is not None
        ]
        control_median_change = float(median(other_changes)) if other_changes else None
        europe_change = regional_changes.get(scenario.region)
        regional_comparison_available = europe_change is not None and control_median_change is not None
        regional_payload = {
            "net_deposit_per_customer_change": regional_changes,
            "europe_change": europe_change,
            "calculation_status": "computed" if regional_comparison_available else "unavailable",
            "unavailable_reason": ("missing_target_region" if europe_change is None else
                                   "missing_control_regions" if control_median_change is None else None),
            "control_region_count": len(other_changes),
            "other_region_median_change": control_median_change,
        }
        regional_record = self.registry.register(
            "regional_net_deposit_control",
            {
                "baseline_start": scenario.baseline_start.isoformat(),
                "current_start": scenario.current_start.isoformat(),
                "baseline_end": scenario.baseline_end.isoformat(),
                "current_end": scenario.current_end.isoformat(),
                "region": scenario.region, "currency": "USD",
                "source_evidence_ids": [*baseline_region_evidence, *current_region_evidence],
            },
            regional_payload,
        )

        event_start = (scenario.event_date - timedelta(days=2)).isoformat()
        event_end = (scenario.event_date + timedelta(days=2) + timedelta(days=1)).isoformat()
        event_sql = event_query(event_start, event_end)
        events = self.sql_tool.run(event_sql)
        if not complete_sql_rows(events.data):
            raise ValueError("Event facts require complete SQL rows")
        matching_events = [
            row
            for row in events.data["rows"]
            if row.get("event_type") == scenario.event_type
        ]

        withdrawal_pressure = withdrawal_change > 0
        decline = net_change < 0
        concentrated = concentration_share >= 0.35 if concentration_share is not None else None
        europe_worse_than_control = (
            regional_payload["europe_change"] < regional_payload["other_region_median_change"]
            if regional_comparison_available else None
        )

        diagnosis = {
            "net_deposit_declined": decline,
            "withdrawal_pressure_increased": withdrawal_pressure,
            "deposit_change": deposit_change,
            "withdrawal_change": withdrawal_change,
            "withdrawal_concentration_high": concentrated,
            "europe_worse_than_other_region_median": europe_worse_than_control,
            "matching_operational_event_found": bool(matching_events),
            "root_cause_status": (
                "supported_candidate"
                if decline and withdrawal_pressure and concentrated
                else "insufficient_evidence"
            ),
            "driver_type": "observed_withdrawal_concentration" if concentrated else "undetermined",
            "causal_language_guardrail": (
                "The evidence supports concentrated high-value withdrawals as an observed driver of the synthetic "
                "net-deposit deterioration. It does not establish why those customers withdrew or justify an "
                "investment, compliance, or customer-risk conclusion without additional evidence."
                if concentrated else
                "The evidence does not establish concentrated withdrawals as a driver or a causal explanation."
            ),
        }

        metrics = {
            "periods": {
                "baseline": {
                    "start": scenario.baseline_start.isoformat(),
                    "end": scenario.baseline_end.isoformat(),
                    "deposits": baseline_deposits,
                    "withdrawals": baseline_withdrawals,
                    "net_deposits": baseline_net,
                },
                "current": {
                    "start": scenario.current_start.isoformat(),
                    "end": scenario.current_end.isoformat(),
                    "deposits": current_deposits,
                    "withdrawals": current_withdrawals,
                    "net_deposits": current_net,
                },
            },
            "driver_decomposition": driver_payload,
            "customer_concentration": concentration_payload,
            "regional_control": regional_payload,
            "nearby_business_events": matching_events,
        }

        net_binding = NetChangeBinding(
            value=net_change, evidence_id=driver_record.evidence_id,
            baseline_start=scenario.baseline_start.isoformat(),
            baseline_end=scenario.baseline_end.isoformat(),
            current_start=scenario.current_start.isoformat(),
            current_end=scenario.current_end.isoformat(),
        )
        decomposition_binding = NetDecompositionBinding(
            **{field: getattr(net_binding, field) for field in
               ('value', 'evidence_id', 'baseline_start', 'baseline_end', 'current_start', 'current_end')},
            deposit_change=deposit_change, withdrawal_change=withdrawal_change,
        )
        concentration_binding = ConcentrationBinding(
            value=concentration_share, numerator=top_n_amount, denominator=current_withdrawals,
            customer_count=scenario.customer_count, period_start=current_start,
            period_end_exclusive=current_end_exclusive, evidence_id=concentration_record.evidence_id,
            source_evidence_id=current_wd.evidence_id,
        )
        def amounts(regions):
            return tuple(RegionAmounts(r, v["customer_count"], v["deposits"], v["withdrawals"])
                         for r, v in sorted(regions.items()))
        regional_binding = RegionalBinding(
            value=europe_change, control_value=control_median_change,
            baseline=amounts(baseline_regions), current=amounts(current_regions),
            baseline_start=scenario.baseline_start.isoformat(), baseline_end=scenario.baseline_end.isoformat(),
            current_start=scenario.current_start.isoformat(), current_end=scenario.current_end.isoformat(),
            evidence_id=regional_record.evidence_id,
            source_evidence_ids=(*baseline_region_evidence, *current_region_evidence),
        )
        event_binding = EventBinding(events.evidence_id,
            tuple(sorted(row["event_id"] for row in matching_events)),
            period_start=event_start, period_end_exclusive=event_end)
        claims = (
            Claim(
                "N-C1",
                render_net_change(net_binding),
                "supported",
                "high",
                (
                    baseline_dep.evidence_id,
                    baseline_wd.evidence_id,
                    current_dep.evidence_id,
                    current_wd.evidence_id,
                    driver_record.evidence_id,
                ),
                numeric_binding=net_binding,
            ),
            Claim(
                "N-C2",
                render_net_decomposition(decomposition_binding),
                "supported",
                "high",
                (baseline_dep.evidence_id, baseline_wd.evidence_id,
                 current_dep.evidence_id, current_wd.evidence_id, driver_record.evidence_id),
                numeric_binding=decomposition_binding,
            ),
            Claim(
                "N-C3",
                render_concentration(concentration_binding),
                "supported" if concentration_share is not None else "insufficient_evidence",
                "high",
                (concentration_query.evidence_id, concentration_record.evidence_id, current_wd.evidence_id),
                numeric_binding=concentration_binding,
            ),
            Claim(
                "N-C4",
                render_regional(regional_binding),
                "supported" if regional_comparison_available else "insufficient_evidence",
                "medium",
                (
                    *baseline_region_evidence,
                    *current_region_evidence,
                    regional_record.evidence_id,
                ),
                numeric_binding=regional_binding,
            ),
            Claim(
                "N-C5",
                render_event(event_binding),
                "supported_with_guardrail" if matching_events else "insufficient_evidence",
                "high" if matching_events else "low",
                (
                    events.evidence_id,
                    concentration_record.evidence_id,
                    driver_record.evidence_id,
                ),
                event_binding=event_binding,
            ),
        )

        return InvestigationResult(
            product="FitzSight",
            mode="deterministic_net_deposit_v0.6",
            question=question,
            plan=plan,
            claims=claims,
            metrics=metrics,
            diagnosis=diagnosis,
            evidence=tuple(self.registry.to_dicts()),
        )
