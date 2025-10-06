import os
import json
from abc import ABC
from typing import Any, Dict, List, Optional
import litellm

class LiteLLMProvider(ABC):
    """Provider utilisant LiteLLM pour supporter tous les modèles"""
    
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        **default_params
    ):
        self.model = model
        self.default_params = default_params
        
        # Configuration de l'API key si fournie
        if api_key:
            if model.startswith("claude"):
                os.environ["ANTHROPIC_API_KEY"] = api_key
            elif model.startswith("mistral"):
                os.environ["MISTRAL_API_KEY"] = api_key
            elif model.startswith("gpt"):
                os.environ["OPENAI_API_KEY"] = api_key
    
    async def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        **kwargs
    ) -> Any:
        """Appel à LiteLLM avec support des outils"""
        params = {**self.default_params, **kwargs}
        
        # LiteLLM gère automatiquement la conversion des formats
        response = await litellm.acompletion(
            model=self.model,
            messages=messages,
            tools=tools if tools else None,
            **params
        )
        return response
    
    def extract_content(self, response: Any) -> Optional[str]:
        """Extrait le contenu textuel"""
        try:
            return response.choices[0].message.content
        except (AttributeError, IndexError):
            return None
    
    def extract_tool_calls(self, response: Any) -> List[Dict[str, Any]]:
        """Extrait les appels d'outils (format OpenAI standard)"""
        try:
            tool_calls = response.choices[0].message.tool_calls
            if not tool_calls:
                return []
            
            result = []
            for tc in tool_calls:
                result.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": json.loads(tc.function.arguments or "{}")
                })
            return result
        except (AttributeError, TypeError):
            return []
    
    def format_tool_result(
        self,
        tool_call_id: str,
        tool_name: str,
        result: str
    ) -> Dict[str, Any]:
        """Format OpenAI standard pour les résultats d'outils"""
        return {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": tool_name,
            "content": result
        }

