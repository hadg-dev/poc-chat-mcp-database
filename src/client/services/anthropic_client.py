from typing import List

import anthropic
from anthropic.types import MessageParam, ToolUnionParam

from src.client.utils.config import Config
from src.client.utils.logger import logger


class AnthropicClient:
    """Wrapper client for the Anthropic API."""

    def __init__(self, config: Config):
        self.config = config
        self.client = anthropic.AsyncAnthropic(api_key=config.anthropic_api_key)

    async def create_message(
        self, messages: List[MessageParam], tools: List[ToolUnionParam], system_prompt: str
    ) -> anthropic.types.Message:
        """Creates a message via the Anthropic API."""
        try:
            return await self.client.messages.create(
                model=self.config.model,
                system=system_prompt,
                max_tokens=self.config.max_tokens,
                messages=messages,
                tools=tools,
            )
        except Exception as e:
            logger.error(f"Anthropic API Error: {e}")
            raise
