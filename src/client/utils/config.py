import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


from src.client.utils.logger import logger

@dataclass
class Config:
    """Centralized application configuration."""

    llm_api_key: str
    llm_model: str
    llm_max_tokens: int = 8000
    mcp_server_command: str = "python"
    mcp_server_script: str = "./mcp_demo_server.py"
    

    def __post_init__(self):
        logger.debug(f"Configuration loaded: {self}")

    @classmethod
    def from_env(cls) -> "Config":
        """Creates the configuration from environment variables."""
        load_dotenv()

        llm_model = os.getenv("LLM_MODEL", "claude-3-5-sonnet-20241022")
        llm_api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("MISTRAL_API_KEY") or ""
        if not llm_api_key:
            raise Exception("LLM API key is required. Set ANTHROPIC_API_KEY, OPENAI_API_KEY, or MISTRAL_API_KEY in environment variables.")
        llm_max_tokens = int(os.getenv("LLM_MAX_TOKENS", "8000"))
        mcp_server_command = os.getenv("MCP_SERVER_COMMAND", "python")
        mcp_server_script = os.getenv("MCP_SERVER_SCRIPT", "./mcp_demo_server.py")
        if not Path(mcp_server_script).is_file():
            raise Exception(f"MCP server script not found: {mcp_server_script}")
        return cls(
            llm_api_key=llm_api_key,
            llm_model=llm_model,
            llm_max_tokens=llm_max_tokens,
            mcp_server_command=mcp_server_command,
            mcp_server_script=mcp_server_script,
        )
