from __future__ import annotations

import importlib.util
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class StoreError(RuntimeError):
    """Raised when the local analytical store cannot be initialized or queried."""


def _safe_identifier(value: str) -> str:
    if not _IDENTIFIER.fullmatch(value):
        raise ValueError(f"Unsafe SQL identifier: {value!r}")
    return value


def _quote_identifier(value: str) -> str:
    return f'"{_safe_identifier(value)}"'


@dataclass(frozen=True)
class StoreInfo:
    backend: str
    data_dir: str
    tables: tuple[str, ...]


class AnalyticsStore:
    """Local read-mostly analytical store.

    The preferred backend is DuckDB. A SQLite fallback exists so deterministic
    development tests can run in restricted/offline environments. The public
    competition deployment should install DuckDB via the project dependencies.
    """

    def __init__(self, data_dir: str | Path, backend: str = "auto") -> None:
        self.data_dir = Path(data_dir).resolve()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.backend = self._resolve_backend(backend)
        self._conn: Any = self._connect()
        self._loaded_tables: list[str] = []

    @staticmethod
    def duckdb_available() -> bool:
        return importlib.util.find_spec("duckdb") is not None

    @classmethod
    def _resolve_backend(cls, backend: str) -> str:
        normalized = backend.lower().strip()
        if normalized not in {"auto", "duckdb", "sqlite"}:
            raise ValueError("backend must be one of: auto, duckdb, sqlite")
        if normalized == "auto":
            return "duckdb" if cls.duckdb_available() else "sqlite"
        if normalized == "duckdb" and not cls.duckdb_available():
            raise StoreError(
                "DuckDB backend requested but the 'duckdb' package is not installed. "
                "Run `pip install -e \".[dev]\"` in an internet-enabled environment."
            )
        return normalized

    def _connect(self) -> Any:
        if self.backend == "duckdb":
            import duckdb  # type: ignore

            # In-memory connection keeps the demo self-contained. CSV files remain
            # the reproducible source data for the competition benchmark.
            return duckdb.connect(database=":memory:")
        return sqlite3.connect(":memory:")

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "AnalyticsStore":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()

    def load_csv_directory(self, include: Iterable[str] | None = None) -> StoreInfo:
        allowed = set(include) if include is not None else None
        csv_paths = sorted(self.data_dir.glob("*.csv"))
        if not csv_paths:
            raise StoreError(f"No CSV files found in {self.data_dir}")

        for path in csv_paths:
            table = _safe_identifier(path.stem)
            if allowed is not None and table not in allowed:
                continue
            self._load_csv(table, path)
            if table not in self._loaded_tables:
                self._loaded_tables.append(table)

        if not self._loaded_tables:
            raise StoreError("No requested CSV tables were loaded")
        return self.info()

    def _load_csv(self, table: str, path: Path) -> None:
        # The path is discovered from the configured local data directory, not from
        # user SQL. Resolve it again and ensure it remains within that directory.
        resolved = path.resolve()
        if resolved.parent != self.data_dir:
            raise StoreError("CSV path escaped configured data directory")

        if self.backend == "duckdb":
            escaped_path = str(resolved).replace("'", "''")
            self._conn.execute(
                f"CREATE OR REPLACE VIEW {_quote_identifier(table)} AS "
                f"SELECT * FROM read_csv_auto('{escaped_path}', HEADER=TRUE)"
            )
            return

        df = pd.read_csv(resolved)
        # Parse known timestamp/date columns so comparisons behave consistently.
        for column in df.columns:
            if column in {"registration_date", "lead_created_at", "timestamp", "date"}:
                parsed = pd.to_datetime(df[column], errors="coerce")
                df[column] = parsed.dt.strftime("%Y-%m-%d %H:%M:%S")
        df.to_sql(table, self._conn, if_exists="replace", index=False)

    def info(self) -> StoreInfo:
        return StoreInfo(
            backend=self.backend,
            data_dir=str(self.data_dir),
            tables=tuple(sorted(self._loaded_tables)),
        )

    def list_tables(self) -> list[str]:
        return list(self.info().tables)

    def table_columns(self, table: str) -> list[dict[str, Any]]:
        table = _safe_identifier(table)
        if table not in self._loaded_tables:
            raise StoreError(f"Unknown table: {table}")

        if self.backend == "duckdb":
            rows = self._conn.execute(f"DESCRIBE {_quote_identifier(table)}").fetchall()
            # DuckDB DESCRIBE currently returns column_name, column_type, null, key,
            # default, extra. Only expose the stable fields needed by the Agent.
            return [
                {"name": row[0], "type": row[1], "nullable": row[2] if len(row) > 2 else None}
                for row in rows
            ]

        rows = self._conn.execute(f"PRAGMA table_info({_quote_identifier(table)})").fetchall()
        return [
            {"name": row[1], "type": row[2], "nullable": not bool(row[3])}
            for row in rows
        ]

    def execute(self, sql: str) -> tuple[list[str], list[tuple[Any, ...]]]:
        cursor = self._conn.execute(sql)
        description = cursor.description or []
        columns = [item[0] for item in description]
        rows = cursor.fetchall()
        return columns, rows
