import os
import json
import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# pip install mistralai
from mistralai import Mistral

load_dotenv()

# ---- Mistral client ----
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
mistral_client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

# ---- MCP server (same as original) ----
server_params = StdioServerParameters(
    command="python",
    args=["./mcp_server.py"],
    env=None,
)


def _mcp_tools_to_mistral_tools(mcp_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert MCP tool descriptors (name, description, input_schema) to
    Mistral/OpenAI-style function tools.
    """
    out = []
    for t in mcp_tools:
        out.append(
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t.get("description", "") or "",
                    "parameters": t["input_schema"],  # already JSON schema
                },
            }
        )
    return out


@dataclass
class Chat:
    # we’ll keep a plain list of dicts to stay close to wire format
    messages: List[Dict[str, Any]] = field(default_factory=list)

    # keep your original system prompt
    system_prompt: str = (
        "You are a master SQLite assistant. "
        "Your job is to use the tools at your dispoal to execute SQL queries and provide the results to the user."
    )

    async def _mistral_complete(
        self,
        tools: List[Dict[str, Any]],
        extra_messages: List[Dict[str, Any]] = None,
    ):
        """
        Call Mistral chat.completions with tools + current history.
        Returns (message_dict, raw_response).
        """
        msgs = []
        # System message first
        msgs.append({"role": "system", "content": self.system_prompt})
        # Then the accumulated conversation
        msgs.extend(self.messages)
        # Then any extra batch (e.g., current user query)
        if extra_messages:
            msgs.extend(extra_messages)

        return mistral_client.chat.complete(
            model=MISTRAL_MODEL,
            messages=msgs,
            tools=tools,
            max_tokens=8000,
        )

    async def process_query(self, session: ClientSession, query: str) -> None:
        # Fetch tools from MCP server
        response = await session.list_tools()
        available_tools = [
            {
                "name": tool.name,
                "description": tool.description or "",
                "input_schema": tool.inputSchema,
            }
            for tool in response.tools
        ]
        mistral_tools = _mcp_tools_to_mistral_tools(available_tools)

        # Append the user's message to our rolling history
        self.messages.append({"role": "user", "content": query})

        # Tool-use loop (keep calling until no tool_calls)
        while True:
            res = await self._mistral_complete(mistral_tools)
            msg = res.choices[0].message

            # Print any assistant text
            if msg.content:
                print(msg.content)

            tool_calls = getattr(msg, "tool_calls", None)
            if not tool_calls:
                # No tool calls → finalize this turn
                self.messages.append({"role": "assistant", "content": msg.content or ""})
                break

            # We must add the assistant message with its tool_calls into history
            assistant_entry = {
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [],
            }
            # Execute each tool call via MCP and append tool results
            tool_result_messages: List[Dict[str, Any]] = []

            for tc in tool_calls:
                # tc.function.name, tc.function.arguments (JSON string)
                fn_name = tc.function.name
                try:
                    fn_args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    fn_args = {}

                # Call MCP tool
                result = await session.call_tool(fn_name, fn_args)
                # Text result from MCP
                result_text = getattr(result.content[0], "text", "")

                # Record the tool call in the assistant message
                assistant_entry["tool_calls"].append(
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": fn_name, "arguments": tc.function.arguments or "{}"},
                    }
                )

                # Append the tool result message (linked via tool_call_id)
                tool_result_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": fn_name,
                        "content": result_text,
                    }
                )

            # Push assistant (with tool_calls) and the subsequent tool results into history
            self.messages.append(assistant_entry)
            self.messages.extend(tool_result_messages)

            # And loop again to let the model continue with the new info

    async def chat_loop(self, session: ClientSession):
        while True:
            query = input("\nQuery: ").strip()
            await self.process_query(session, query)

    async def run(self):
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                await self.chat_loop(session)


if __name__ == "__main__":
    chat = Chat()
    asyncio.run(chat.run())
