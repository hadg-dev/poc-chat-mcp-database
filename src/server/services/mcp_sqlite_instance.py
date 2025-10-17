from fastmcp import FastMCP
from pathlib import Path
from src.server.data_sources.sqlite import SQLiteDataSource
from src.server.services.abstract_mcp_instance import AbstractMCPInstance


class MCPSQLiteInstance(AbstractMCPInstance):

    def __init__(self, db_path: str):
        # check if db_path exists
        if not Path(db_path).exists():
            raise ValueError(f"Database path does not exist: {db_path}")

        self.sqlite_db_path = db_path
        self.mcp = FastMCP(name="MCP SQLite Demo")
        self.data_source = SQLiteDataSource(db_path)

        super().__init__(self.mcp)

    def init_mcp(self):
        @self.mcp.tool
        def query_data(sql: str) -> str:
            """Execute an SQL query against the SQLite database."""
            rows = self.data_source.execute(sql)
            if not rows:
                return "(no results)"
            return "\n".join(str(row) for row in rows)

        @self.mcp.prompt()
        def example_prompt(code: str) -> str:
            return f"Please review this code:\n\n{code}"
