"""SQLite implementation of the data source abstraction."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Sequence, Tuple

from server.data_sources.abstract_base import AbstractDataSource
from src.server.utils.logger import logger

Row = Tuple[object, ...]
Rows = Sequence[Row]


class SQLiteDataSource(AbstractDataSource):
    """Execute SQL queries against a SQLite database file."""

    def __init__(self, database_path: str | Path) -> None:
        self._database_path = Path(database_path)

    def execute(self, sql: str) -> Rows:
        logger.debug("SQLiteDataSource executing query: {}", sql)
        with sqlite3.connect(self._database_path) as connection:
            cursor = connection.execute(sql)
            rows: Sequence[Tuple[object, ...]] = cursor.fetchall()
        return rows  # type: ignore[return-value]

    def __repr__(self) -> str:
        return f"SQLiteDataSource(database_path='{self._database_path}')"
