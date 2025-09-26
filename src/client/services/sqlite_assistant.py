import sys
from typing import Any, Dict, List, Optional, Union

from anthropic.types import MessageParam, ToolUseBlock
from mcp import ClientSession, StdioServerParameters, stdio_client

from src.client.models.chat_message import ChatMessage
from src.client.services.anthropic_client import AnthropicClient
from src.client.services.tool_executor import ToolExecutor
from src.client.utils.config import Config
from src.client.utils.logger import logger


class SQLiteAssistant:
    """Main SQLite assistant using MCP and Anthropic."""

    SYSTEM_PROMPT = """You are an expert SQLite assistant.
    Your job is to use the tools at your disposal to execute SQL queries and provide the results to the user.
    Always answer in English and explain your actions clearly."""

    def __init__(self, config: Config):
        self.config = config
        self.anthropic_client = AnthropicClient(config)
        self.messages: List[ChatMessage] = []
        self.tool_executor: Optional[ToolExecutor] = None

    def add_message(self, role: str, content: Union[str, List[Dict[str, Any]]]) -> None:
        """Adds a message to the history."""
        message = ChatMessage(role=role, content=content)
        self.messages.append(message)
        logger.debug(f"Message added: {role}")

    def get_message_params(self) -> List[MessageParam]:
        """Converts messages to MessageParam for the API."""
        return [msg.to_message_param() for msg in self.messages]

    async def process_tool_use(self, content: ToolUseBlock) -> str:
        """Processes a tool use."""
        if not self.tool_executor:
            return "Error: Tool executor not available"

        logger.info(f"Executing tool: {content.name}")
        result = await self.tool_executor.execute_tool(content.name, content.input or {})

        # Add the tool result to the messages
        self.add_message(
            "user",
            [
                {
                    "type": "tool_result",
                    "tool_use_id": content.id,
                    "content": result,
                }
            ],
        )

        return result

    async def process_query(self, query: str) -> None:
        """Processes a user query."""
        if not self.tool_executor:
            print("Error: MCP session not initialized")
            return

        # Add the user query
        self.add_message("user", query)

        try:
            # Get available tools
            available_tools = await self.tool_executor.get_available_tools()

            # Initial call to Claude
            response = await self.anthropic_client.create_message(
                messages=self.get_message_params(), tools=available_tools, system_prompt=self.SYSTEM_PROMPT
            )

            # Process the response
            assistant_content = []
            text_responses = []

            for content in response.content:
                if content.type == "text":
                    assistant_content.append(content)
                    text_responses.append(content.text)
                    print(content.text)
                elif content.type == "tool_use":
                    assistant_content.append(content)
                    await self.process_tool_use(content)

            # Add the assistant's response
            if assistant_content:
                self.add_message("assistant", assistant_content)

            # If tools were used, get the final response
            if any(content.type == "tool_use" for content in response.content):
                final_response = await self.anthropic_client.create_message(
                    messages=self.get_message_params(), tools=available_tools, system_prompt=self.SYSTEM_PROMPT
                )

                final_text = ""
                for content in final_response.content:
                    if hasattr(content, "text"):
                        final_text += content.text

                if final_text:
                    self.add_message("assistant", final_text)
                    print(final_text)

        except Exception as e:
            error_msg = f"Error while processing the query: {e}"
            logger.error(error_msg)
            print(error_msg)

    async def chat_loop(self) -> None:
        """Interactive chat loop."""
        print("SQLite Assistant - Type 'quit' to exit\n")

        while True:
            try:
                query = input("Query: ").strip()
                if query.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break

                if not query:
                    continue

                await self.process_query(query)

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break

    async def run(self) -> None:
        """Runs the assistant."""
        server_params = StdioServerParameters(
            command=self.config.server_command,
            args=[self.config.server_script],
            env=None,
        )

        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the connection
                    await session.initialize()
                    self.tool_executor = ToolExecutor(session)

                    logger.info("MCP session initialized successfully")
                    await self.chat_loop()

        except Exception as e:
            logger.error(f"Error during MCP initialization: {e}")
            print(f"Could not connect to MCP server: {e}")
            sys.exit(1)
