from src.client.mcp_client_cli import MCPClientCLI
from src.client.utils.logger import logger

if __name__ == "__main__":
    logger.info("Starting MCP client...")
    app = MCPClientCLI()
    app.run()