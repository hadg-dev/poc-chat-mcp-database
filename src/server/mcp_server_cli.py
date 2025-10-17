import os

from src.server.services.mcp_main_instance import MCPMainInstance
from src.server.services.mcp_sqlite_instance import MCPSQLiteInstance
from src.server.utils.logger import logger


class MCPServerManagerCLI:
    def __init__(self):
        # Assuming the script is run from the root of the project
        db_path = os.path.join(os.path.dirname(__file__), "..", "..", "databases", "database.db")

        self.mcp_global = MCPMainInstance()
        #self.mcp_sqlite = MCPSQLiteInstance(db_path=db_path)

    def run(self):
        """Initialize and run the MCP server application."""
        logger.info("Initializing MCP instances...")

        self.mcp_global.init()
        self.mcp_global.init_mcp()

        # The __init__ is already called, so we just need to call init_mcp
        #self.mcp_sqlite.init_mcp()

        logger.info("MCP Global Instance Tools:", self.mcp_global.mcp.tools)
        logger.info("MCP SQLite Instance Tools:", self.mcp_sqlite.mcp.tools)

        # start mcp servers
        self.mcp_global.start_all()

        logger.info("MCP Server is running.")


if __name__ == "__main__":
    app = MCPServerManagerCLI()
    app.run()
