from src.client.mcp_client_cli import MCPClientCLI
from src.client.utils.logger import logger

if __name__ == "__main__":
    try:
        logger.info("Starting MCP client...")
        app = MCPClientCLI()
        app.run()
    except KeyboardInterrupt:
        logger.info("Client interrupted by user")
    except Exception as e:
        logger.error(f"Error running MCP client: {e}", exc_info=True)
        raise