from typing import Any, Dict, List

from anthropic.types import ToolUnionParam

from src.client.models.errors_model import MCPConnectionError
from src.client.services.anthropic_client import ClientSession
from src.client.utils.logger import logger


class ToolExecutor:
    """MCP Tool Execution Manager."""

    def __init__(self, session: ClientSession):
        self.session = session

    async def get_available_tools(self) -> List[ToolUnionParam]:
        """Retrieves the list of available tools."""
        try:
            response = await self.session.list_tools()
            return [
                {
                    "name": tool.name,
                    "description": tool.description or "",
                    "input_schema": tool.inputSchema,
                }
                for tool in response.tools
            ]
        except Exception as e:
            logger.error(f"Error while retrieving tools: {e}")
            raise MCPConnectionError(f"Could not retrieve tools: {e}")

    async def execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        """Executes a tool and returns the result."""
        try:
            result = await self.session.call_tool(tool_name, tool_args)
            return getattr(result.content[0], "text", "")
        except Exception as e:
            logger.error(f"Error during tool execution {tool_name}: {e}")
            return f"Error during tool execution: {e}"
