"""Entrypoint for running the Demo MCP client."""

from __future__ import annotations

import sys

from src.client.mcp_client_cli import MCPClientCLI
from src.client.utils.logger import logger


def main() -> None:
    """Initialize and run the MCP client application."""
    try:
        logger.info("Starting MCP client...")
        app = MCPClientCLI()
        app.run()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
