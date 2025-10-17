import asyncio
import sys

from src.client.utils.config import Config
from src.client.utils.logger import logger
from src.client.business.mcp_chat import MCPChatClient
from src.client.business.llm_provider import LiteLLMProvider

class MCPClientCLI:
    def __init__(self):
        self.chat = None
        self.server_params = None
        
    def main(self):
        try:
            config = Config.from_env()
        
            server_params =  MCPChatClient.setup_stdio_server_params(
                command="python",
                script=config.mcp_server_script
            )

            llm_provider = LiteLLMProvider(
                model=config.llm_model,
                api_key=config.llm_api_key,
                max_tokens=config.llm_max_tokens,
                temperature=0.7
            )

            
            chat = MCPChatClient(llm_provider=llm_provider)

            self.chat = chat
            self.server_params = server_params
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            sys.exit(2)

    def run(self):
        """Initialize and run the MCP client application."""
        logger.info("Initializing MCP client...")
        self.main()
        asyncio.run(self.chat.run(self.server_params))
        logger.info("MCP client has shut down.")


if __name__ == "__main__":
    logger.info("Starting MCP client...")
    try:
        app = MCPClientCLI()
        app.run()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    logger.info("MCP client has shut down.")
