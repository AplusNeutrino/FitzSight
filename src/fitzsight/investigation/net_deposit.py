from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from statistics import median
from typing import Any

from fitzsight.data.scenarios import NET_DEPOSIT_SCENARIO
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.tools.schema import SchemaInspectorTool
from fitzsight.tools.sql import ReadOnlySQLTool
from .models import Claim, InvestigationPlan, InvestigationResult, PlanStep


class NetDepositInvestigationEngine:
    """Deterministic engine for the second FitzSight v0.5 business intent."""

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
        start_s, end_exclusive = self._period_bounds(start, end)
        region_clause = ""
        if region is not None:
            safe_region = region.replace("'", "''")
            region_clause = f" AND c.region = '{safe_region}'"
        sql = (
            f"SELECT t.customer_id, t.timestamp, t.amount, c.region, c.assigned_team "
            f"FROM {table} AS t JOIN customers AS c ON c.customer_id = t.customer_id "
            f"WHERE t.status = 'completed' "
            f"AND t.timestamp >= '{start_s}' AND t.timestamp < '{end_exclusive}'"
            f"{region_clause} ORDER BY t.timestamp, t.customer_id"
        )
        return self.sql_tool.run(sql)

    def _regional_net_per_customer(self, start: date, end: date):
        start_s, end_exclusive = self._period_bounds(start, end)
        deposit_sql = (
            "SELECT c.region, COUNT(DISTINCT c.customer_id) AS customer_count, "
            "COALESCE(SUM(d.amount), 0) AS deposits "
            "FROM customers c LEFT JOIN deposits d ON d.customer_id = c.customer_id "
            f"AND d.status = 'completed' AND d.timestamp >= '{start_s}' AND d.timestamp < '{end_exclusive}' "
            "GROUP BY c.region ORDER BY c.region"
        )
        withdrawal_sql = (
            "SELECT c.region, COALESCE(SUM(w.amount), 0) AS withdrawals "
            "FROM customers c LEFT JOIN withdrawals w ON w.customer_id = c.customer_id "
            f"AND w.status = 'completed' AND w.timestamp >= '{start_s}' AND w.timestamp < '{end_exclusive}' "
            "GROUP BY c.region ORDER BY c.region"
        )
        deposits = self.sql_tool.run(deposit_sql)
        withdrawals = self.sql_tool.run(withdrawal_sql)
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
                "net_deposits_per_customer": net / customers if customers else 0.0,
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
            "deposits": {"customer_id", "timestamp", "amount", "status"},
            "withdrawals": {"customer_id", "timestamp", "amount", "status"},
            "business_events": {"event_id", "date", "event_type", "region", "description"},
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
        driver_record = self.registry.register(
            "net_deposit_driver_decomposition",
            {
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
            "SELECT w.customer_id, c.assigned_team, SUM(w.amount) AS withdrawal_amount "
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
            top_n_amount / current_withdrawals if current_withdrawals > 0 else 0.0
        )
        concentration_payload = {
            "customer_count": scenario.customer_count,
            "top_customer_withdrawal_amount": top_n_amount,
            "current_total_withdrawals": current_withdrawals,
            "share_of_current_withdrawals": concentration_share,
            "top_customers": top_n,
        }
        concentration_record = self.registry.register(
            "withdrawal_customer_concentration",
            {"region": scenario.region, "period_start": current_start},
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
            before = baseline_regions.get(region, {}).get("net_deposits_per_customer", 0.0)
            after = current_regions.get(region, {}).get("net_deposits_per_customer", 0.0)
            regional_changes[region] = float(after) - float(before)

        other_changes = [
            value for region, value in regional_changes.items() if region != scenario.region
        ]
        control_median_change = float(median(other_changes)) if other_changes else 0.0
        regional_payload = {
            "net_deposit_per_customer_change": regional_changes,
            "europe_change": regional_changes.get(scenario.region, 0.0),
            "other_region_median_change": control_median_change,
        }
        regional_record = self.registry.register(
            "regional_net_deposit_control",
            {
                "baseline_start": scenario.baseline_start.isoformat(),
                "current_start": scenario.current_start.isoformat(),
            },
            regional_payload,
        )

        event_start = (scenario.event_date - timedelta(days=2)).isoformat()
        event_end = (scenario.event_date + timedelta(days=2) + timedelta(days=1)).isoformat()
        event_sql = (
            "SELECT event_id, date, event_type, region, affected_team, description "
            "FROM business_events WHERE region = 'Europe' "
            f"AND date >= '{event_start}' AND date < '{event_end}' ORDER BY date"
        )
        events = self.sql_tool.run(event_sql)
        matching_events = [
            row
            for row in events.data["rows"]
            if row.get("event_type") == scenario.event_type
        ]

        withdrawal_pressure = withdrawal_change > 0
        decline = net_change < 0
        concentrated = concentration_share >= 0.35
        europe_worse_than_control = (
            regional_payload["europe_change"] < regional_payload["other_region_median_change"]
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
            "driver_type": "observed_withdrawal_concentration",
            "causal_language_guardrail": (
                "The evidence supports concentrated high-value withdrawals as an observed driver of the synthetic "
                "net-deposit deterioration. It does not establish why those customers withdrew or justify an "
                "investment, compliance, or customer-risk conclusion without additional evidence."
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

        claims = (
            Claim(
                "N-C1",
                (
                    f"European net deposits changed by ${net_change:,.2f} week over week "
                    f"({scenario.baseline_start.isoformat()}–{scenario.baseline_end.isoformat()} versus "
                    f"{scenario.current_start.isoformat()}–{scenario.current_end.isoformat()})."
                ),
                "supported",
                "high",
                (
                    baseline_dep.evidence_id,
                    baseline_wd.evidence_id,
                    current_dep.evidence_id,
                    current_wd.evidence_id,
                    driver_record.evidence_id,
                ),
            ),
            Claim(
                "N-C2",
                (
                    f"Deposits changed by ${deposit_change:,.2f}, while withdrawals changed by "
                    f"${withdrawal_change:,.2f}; the decomposition exactly reconstructs the net-deposit movement."
                ),
                "supported",
                "high",
                (driver_record.evidence_id,),
            ),
            Claim(
                "N-C3",
                (
                    f"The largest {scenario.customer_count} European customer withdrawals account for "
                    f"{concentration_share:.1%} of current-week European withdrawals."
                ),
                "supported",
                "high",
                (concentration_query.evidence_id, concentration_record.evidence_id),
            ),
            Claim(
                "N-C4",
                (
                    f"Europe's weekly net-deposit movement per registered customer was "
                    f"${regional_payload['europe_change']:,.2f}, versus a median of "
                    f"${regional_payload['other_region_median_change']:,.2f} across the other regions."
                ),
                "supported",
                "medium",
                (
                    *baseline_region_evidence,
                    *current_region_evidence,
                    regional_record.evidence_id,
                ),
            ),
            Claim(
                "N-C5",
                (
                    "A high-value withdrawal-cluster event is present in the nearby operational event log. "
                    "Together with the measured withdrawal concentration, this is a supported observed driver, "
                    "not evidence of why individual customers withdrew."
                ),
                "supported_with_guardrail" if matching_events else "insufficient_evidence",
                "high" if matching_events else "low",
                (
                    events.evidence_id,
                    concentration_record.evidence_id,
                    driver_record.evidence_id,
                ),
            ),
        )

        return InvestigationResult(
            product="FitzSight",
            mode="deterministic_net_deposit_v0.5",
            question=question,
            plan=plan,
            claims=claims,
            metrics=metrics,
            diagnosis=diagnosis,
            evidence=tuple(self.registry.to_dicts()),
        )
