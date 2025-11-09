"""
Anthropic API client for Claude 3 Sonnet integration.

This module provides a wrapper for the Anthropic API with rate limiting,
error handling, and retry logic.
"""

from anthropic import Anthropic, APIError, RateLimitError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from typing import Dict, Any, List
import logging
from src.core.config import settings
from src.core.rate_limiter import rate_limiter_manager

logger = logging.getLogger(__name__)


class AnthropicClient:
    """
    Wrapper for Anthropic API with rate limiting and error handling.
    
    Attributes:
        client: Anthropic API client
        rate_limiter: Token bucket rate limiter for API calls
    """

    def __init__(self):
        """Initialize Anthropic client with API key from settings."""
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        # Create rate limiter: assume tier 2 (50 requests/min = 0.83 req/sec)
        self.rate_limiter = rate_limiter_manager.get_or_create(
            "anthropic", capacity=50, refill_rate=0.83
        )

    @retry(
        retry=retry_if_exception_type((APIError, RateLimitError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def create_message(
        self,
        prompt: str,
        system_message: str = "",
        max_tokens: int = None,
        temperature: float = None,
    ) -> Dict[str, Any]:
        """
        Create a message using Claude 3 Sonnet.
        
        Args:
            prompt: User prompt/message
            system_message: Optional system message for context
            max_tokens: Maximum tokens in response (default from settings)
            temperature: Temperature for response generation (default from settings)
            
        Returns:
            Dict containing response with 'content' and 'usage' keys
            
        Raises:
            APIError: If API call fails after retries
        """
        # Wait for rate limiter
        if not self.rate_limiter.wait_and_acquire(tokens=1, timeout=60.0):
            raise RateLimitError("Rate limit exceeded, timeout waiting for token")

        max_tokens = max_tokens or settings.llm_max_tokens
        temperature = temperature if temperature is not None else settings.llm_temperature

        try:
            logger.info(f"Calling Claude API with prompt length: {len(prompt)}")
            
            messages = [{"role": "user", "content": prompt}]
            
            response = self.client.messages.create(
                model=settings.llm_model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message if system_message else None,
                messages=messages,
            )

            # Extract response content
            content = response.content[0].text if response.content else ""
            
            result = {
                "content": content,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                "model": response.model,
                "stop_reason": response.stop_reason,
            }

            logger.info(
                f"Claude API response: {response.usage.input_tokens} input tokens, "
                f"{response.usage.output_tokens} output tokens"
            )

            return result

        except RateLimitError as e:
            logger.error(f"Rate limit exceeded: {e}")
            raise
        except APIError as e:
            logger.error(f"Anthropic API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling Claude API: {e}")
            raise


# Global client instance
anthropic_client = AnthropicClient()
