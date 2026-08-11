from __future__ import annotations

from fitzsight.data.store import AnalyticsStore
from fitzsight.evidence.registry import EvidenceRegistry
from .base import ToolResult


class SchemaInspectorTool:
    def __init__(self, store: AnalyticsStore, registry: EvidenceRegistry) -> None:
        self.store = store
        self.registry = registry

    def run(self, table: str | None = None) -> ToolResult:
        if table is None:
            payload = {
                "backend": self.store.backend,
                "tables": [
                    {"name": name, "columns": self.store.table_columns(name)}
                    for name in self.store.list_tables()
                ],
            }
            params = {"table": None}
        else:
            payload = {
                "backend": self.store.backend,
                "table": table,
                "columns": self.store.table_columns(table),
            }
            params = {"table": table}

        record = self.registry.register("schema_inspector", params, payload)
        return ToolResult(record.evidence_id, "schema_inspector", payload)
