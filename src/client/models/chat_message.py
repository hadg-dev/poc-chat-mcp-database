from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from anthropic.types import MessageParam


@dataclass
class ChatMessage:
    """Represents a chat message with metadata."""

    role: str
    content: Union[str, List[Dict[str, Any]]]
    timestamp: Optional[float] = None

    def to_message_param(self) -> MessageParam:
        """Converts to MessageParam for the Anthropic API."""
        return MessageParam(role=self.role, content=self.content)
