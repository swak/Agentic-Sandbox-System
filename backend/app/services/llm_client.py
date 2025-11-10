"""
LLM client service for interacting with OpenAI and Anthropic APIs.
"""

import logging
from typing import List, Dict, Optional
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from app.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with LLM APIs (OpenAI, Anthropic)."""

    def __init__(self, api_provider: str, api_key: Optional[str] = None):
        """
        Initialize LLM client.

        Args:
            api_provider: 'openai' or 'anthropic'
            api_key: API key (uses env var if not provided)
        """
        self.api_provider = api_provider

        if api_provider == 'openai':
            self.client = AsyncOpenAI(
                api_key=api_key or settings.OPENAI_API_KEY
            )
        elif api_provider == 'anthropic':
            self.client = AsyncAnthropic(
                api_key=api_key or settings.ANTHROPIC_API_KEY
            )
        else:
            raise ValueError(f"Unsupported API provider: {api_provider}")

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict:
        """
        Get chat completion from LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (e.g., 'gpt-4', 'claude-3-sonnet')
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            Dict with 'content', 'tokens_used', 'estimated_cost'
        """
        try:
            if self.api_provider == 'openai':
                return await self._openai_completion(messages, model, temperature, max_tokens)
            elif self.api_provider == 'anthropic':
                return await self._anthropic_completion(messages, model, temperature, max_tokens)
        except Exception as e:
            logger.error(f"LLM API error: {str(e)}", exc_info=True)
            raise

    async def _openai_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int
    ) -> Dict:
        """OpenAI completion."""
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        tokens_used = response.usage.total_tokens

        # Estimate cost (approximate rates as of 2025)
        cost_per_1k_tokens = {
            'gpt-4': 0.06,
            'gpt-4-turbo': 0.03,
            'gpt-3.5-turbo': 0.002
        }
        cost = (tokens_used / 1000) * cost_per_1k_tokens.get(model, 0.03)

        return {
            'content': response.choices[0].message.content,
            'tokens_used': tokens_used,
            'estimated_cost': f"{cost:.6f}"
        }

    async def _anthropic_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int
    ) -> Dict:
        """Anthropic completion."""
        # Extract system message if present
        system_message = None
        user_messages = []

        for msg in messages:
            if msg['role'] == 'system':
                system_message = msg['content']
            else:
                user_messages.append(msg)

        response = await self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_message,
            messages=user_messages
        )

        tokens_used = response.usage.input_tokens + response.usage.output_tokens

        # Estimate cost
        cost_per_1k_tokens = {
            'claude-3-opus': 0.075,
            'claude-3-sonnet': 0.015,
            'claude-3-haiku': 0.0025
        }
        cost = (tokens_used / 1000) * cost_per_1k_tokens.get(model, 0.015)

        return {
            'content': response.content[0].text,
            'tokens_used': tokens_used,
            'estimated_cost': f"{cost:.6f}"
        }
