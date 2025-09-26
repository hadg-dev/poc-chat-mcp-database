"""Entrypoint for running the Demo MCP server."""

from __future__ import annotations

from src.server.mcp_server_cli import MCPServerManagerCLI


def main() -> None:
    """Initialize and run the MCP server application."""
    app = MCPServerManagerCLI()
    app.run()


if __name__ == "__main__":
    main()
