import os
from dataclasses import dataclass

from dotenv import load_dotenv

from src.client.models.errors_model import ConfigurationError


@dataclass
class Config:
    """Centralized application configuration."""

    anthropic_api_key: str
    model: str = "claude-3-5-sonnet-20240620"
    max_tokens: int = 8000
    server_command: str = "python"
    server_script: str = "./mcp_demo_server.py"

    @classmethod
    def from_env(cls) -> "Config":
        """Creates the configuration from environment variables."""
        load_dotenv()

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ConfigurationError("ANTHROPIC_API_KEY environment variable not set.")

        return cls(
            anthropic_api_key=api_key,
            model=os.getenv("ANTHROPIC_MODEL", cls.model),
            max_tokens=int(os.getenv("MAX_TOKENS", str(cls.max_tokens))),
            server_command=os.getenv("SERVER_COMMAND", cls.server_command),
            server_script=os.getenv("SERVER_SCRIPT", cls.server_script),
        )
