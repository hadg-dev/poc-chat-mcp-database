from fastmcp import FastMCP

from src.server.services.abstract_mcp_instance import AbstractMCPInstance


class MCPMainInstance(AbstractMCPInstance):

    def init(self):
        self.mcp = FastMCP(
            name="MCP Global Demo",
            include_tags={"public", "api"},  # Only expose these tagged components
            exclude_tags={"internal", "deprecated"},  # Hide these tagged components
            on_duplicate_tools="error",  # Handle duplicate registrations
            on_duplicate_resources="warn",
            on_duplicate_prompts="replace",
            include_fastmcp_meta=False,
        )
        super().__init__(self.mcp)

    def init_mcp(self):
        @self.mcp.tool
        def hello():
            return "hi"

        @self.mcp.tool
        def greet(name: str) -> str:
            """Greet a user by name."""
            return f"Hello, {name}!"

        @self.mcp.resource("data://config")
        def get_config() -> dict:
            """Provides the application configuration."""
            return {"version": "1.0", "providers": ["sqlite", "postgres"]}

        @self.mcp.tool
        def multiply(a: float, b: float) -> float:
            """Multiplies two numbers together."""
            return a * b
