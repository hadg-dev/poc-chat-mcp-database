from __future__ import annotations

from abc import ABC, abstractmethod


class AbstractDataSource(ABC):
    """Abstract data source capable of executing queries."""

    @abstractmethod
    def execute(self, sql: str):
        """Execute the given SQL query and return the resulting rows."""
