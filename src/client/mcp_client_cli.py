import asyncio
import os
import sys

from src.client.services.sqlite_assistant import SQLiteAssistant
from src.client.utils.config import Config, ConfigurationError
from src.client.utils.logger import logger


class MCPClientCLI:
    def __init__(self):
        self.assistant = None
        self.config = None

    def main(self):
        try:
            self.config = Config.from_env()
            self.assistant = SQLiteAssistant(self.config)
        except ConfigurationError as e:
            logger.error(f"Configuration error: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            sys.exit(1)

    def run(self):
        """Initialize and run the MCP client application."""
        logger.info("Initializing MCP client...")
        self.main()
        asyncio.run(self.assistant.run())
        logger.info("MCP client has shut down.")


if __name__ == "__main__":
    app = MCPClientCLI()
    app.run()
