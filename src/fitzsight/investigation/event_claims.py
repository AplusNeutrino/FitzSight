"""Fixed-scenario event facts, independently checked against full SQL results.

SQL execution and registry authenticity remain trusted; this is not proof of
real-world causality or a tamper-proof audit store.
"""
from dataclasses import dataclass
from datetime import date, datetime

from .numeric_claims import complete_sql_rows


@dataclass(frozen=True)
class EventBinding:
    evidence_id: str
    matched_event_ids: tuple[str, ...]
    region: str = "Europe"
    event_type: str = "HIGH_VALUE_WITHDRAWAL_CLUSTER"
    period_start: str = "2026-08-03"
    period_end_exclusive: str = "2026-08-08"
    metric_id: str = "nearby_operational_event.v1"


def event_query(start: str, end: str) -> str:
    return ("SELECT event_id, date, event_type, region, affected_team, description "
            "FROM business_events WHERE region = 'Europe' "
            f"AND date >= '{start}' AND date < '{end}' ORDER BY date")


def render_event(b: EventBinding) -> str:
    if b.matched_event_ids:
        return ("A high-value withdrawal-cluster event is present in the nearby operational event log. "
                "The log records an operational event, not evidence of why individual customers withdrew.")
    return ("No matching high-value withdrawal-cluster event was found in the nearby European "
            "operational event log. This does not establish that no event occurred or why customers withdrew.")


def verify_event(claim, registry) -> bool:
    b = claim.event_binding
    if type(b) is not EventBinding or claim.claim_id != "N-C5":
        return False
    if (b.region, b.event_type, b.period_start, b.period_end_exclusive, b.metric_id) != (
        "Europe", "HIGH_VALUE_WITHDRAWAL_CLUSTER", "2026-08-03", "2026-08-08", "nearby_operational_event.v1"
    ):
        return False
    if type(b.matched_event_ids) is not tuple or any(type(x) is not str or not x for x in b.matched_event_ids):
        return False
    try:
        source = registry.get(b.evidence_id)
        if (b.evidence_id not in claim.evidence_ids or source.tool_name != "read_only_sql"
                or source.status != "success" or registry.digest(source.result) != source.result_digest
                or source.parameters["sql"] != event_query(b.period_start, b.period_end_exclusive)):
            return False
        payload = source.result
        if not complete_sql_rows(payload):
            return False
        rows = payload["rows"]
        matched, seen = [], set()
        for row in rows:
            event_id = row["event_id"]
            if type(event_id) is not str or not event_id or event_id in seen:
                return False
            seen.add(event_id)
            # SQLite normalizes dates to naive timestamps; DuckDB can return dates.
            day = row["date"]
            if type(day) is not date:
                stamp = day if type(day) is datetime else datetime.fromisoformat(day)
                if stamp.tzinfo is not None:
                    return False
                day = stamp.date()
            if type(row["region"]) is not str or type(row["event_type"]) is not str:
                return False
            if (row["region"] == b.region and row["event_type"] == b.event_type
                    and date.fromisoformat(b.period_start) <= day < date.fromisoformat(b.period_end_exclusive)):
                matched.append(event_id)
        if tuple(sorted(matched)) != b.matched_event_ids:
            return False
        present = bool(matched)
        return (claim.status == ("supported_with_guardrail" if present else "insufficient_evidence")
                and claim.confidence == ("high" if present else "low")
                and claim.text == render_event(b))
    except (KeyError, TypeError, ValueError, AttributeError):
        return False
