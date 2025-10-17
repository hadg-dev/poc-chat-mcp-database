import json
from dataclasses import dataclass, field
import os
from typing import Any, Dict, List

from src.client.business.llm_provider import LiteLLMProvider
from mcp import ClientSession, StdioServerParameters, stdio_client

from src.client.utils.logger import logger


@dataclass
class MCPChatClient:
    """Client de chat unifié avec support MCP"""
    
    llm_provider: LiteLLMProvider
    messages: List[Dict[str, Any]] = field(default_factory=list)
    system_prompt: str = (
        "You are a master SQLite assistant. "
        "Your job is to use the tools at your disposal to execute SQL queries "
        "and provide the results to the user."
    )
    
    async def process_query(self, session: ClientSession, query: str) -> None:
        """Traite une requête utilisateur avec support des outils MCP"""
        
        # Récupération des outils MCP
        response = await session.list_tools()
        available_tools = [
            {
                "name": tool.name,
                "description": tool.description or "",
                "input_schema": tool.inputSchema,
            }
            for tool in response.tools
        ]
        tools = LiteLLMProvider.mcp_tools_to_openai_format(available_tools)
        
        # Construction des messages avec système + historique + requête
        current_messages = [
            {"role": "system", "content": self.system_prompt},
            *self.messages,
            {"role": "user", "content": query}
        ]
        
        # Ajout de la requête utilisateur à l'historique
        self.messages.append({"role": "user", "content": query})
        
        # Boucle d'exécution des outils
        while True:
            response = await self.llm_provider.complete(
                messages=current_messages,
                tools=tools
            )

            # Affichage du contenu textuel
            content = self.llm_provider.extract_content(response)
            if content:
                print(content)
            
            # Vérification des appels d'outils
            tool_calls = self.llm_provider.extract_tool_calls(response)
            
            if not tool_calls:
                # Pas d'appel d'outil → fin du tour
                self.messages.append({
                    "role": "assistant",
                    "content": content or ""
                })
                break
            
            # Préparation du message assistant avec tool_calls
            assistant_msg = {
                "role": "assistant",
                "content": content or "",
                "tool_calls": [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["arguments"])
                        }
                    }
                    for tc in tool_calls
                ]
            }
            
            # Exécution des outils via MCP
            tool_results = []
            for tc in tool_calls:
                result = await session.call_tool(tc["name"], tc["arguments"])
                result_text = getattr(result.content[0], "text", "")
                
                tool_result = self.llm_provider.format_tool_result(
                    tc["id"],
                    tc["name"],
                    result_text
                )
                tool_results.append(tool_result)
            
            # Mise à jour de l'historique et des messages courants
            self.messages.append(assistant_msg)
            self.messages.extend(tool_results)
            
            current_messages.append(assistant_msg)
            current_messages.extend(tool_results)
            
            # Boucle pour obtenir la réponse suivante
    
    async def chat_loop(self, session: ClientSession):
        """Interactive chat loop"""
        print("Chat session started. Type your queries below (Ctrl+C to exit).")
        while True:
            try:
                query = input("\nQuery: ").strip()
                if not query:
                    continue
                await self.process_query(session, query)
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    async def run(self, server_params: StdioServerParameters):
        """Runs the MCP client and connects to the server."""
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                await self.chat_loop(session)

    @staticmethod
    def setup_stdio_server_params(command: str, script: str) -> StdioServerParameters:
        """Configures the MCP stdio server parameters"""
        logger.info(f"Setting up MCP stdio server with command: {command} {script}")
        logger.info(f"cwd : {os.getcwd()}")
        return StdioServerParameters(
            command=command,
            args=[script],
            env=None,
        )
  