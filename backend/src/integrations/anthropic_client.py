"""
Anthropic API client for Claude Sonnet 4.5 integration.

This module provides a wrapper for the Anthropic API with rate limiting,
error handling, retry logic, and comprehensive monitoring.
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
import time
from datetime import datetime
from src.core.config import settings
from src.core.rate_limiter import rate_limiter_manager

logger = logging.getLogger(__name__)

# Pricing for Claude Sonnet 4.5 (as of Nov 2024)
# https://docs.anthropic.com/en/docs/about-claude/models
INPUT_COST_PER_MILLION = 3.0  # $3 per million input tokens
OUTPUT_COST_PER_MILLION = 15.0  # $15 per million output tokens

# Global metrics (in production, use Prometheus or similar)
api_metrics = {
    "total_calls": 0,
    "successful_calls": 0,
    "failed_calls": 0,
    "total_input_tokens": 0,
    "total_output_tokens": 0,
    "total_cost_usd": 0.0,
    "total_response_time_ms": 0,
    "last_call_timestamp": None,
}


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

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate API call cost in USD.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in USD
        """
        input_cost = (input_tokens / 1_000_000) * INPUT_COST_PER_MILLION
        output_cost = (output_tokens / 1_000_000) * OUTPUT_COST_PER_MILLION
        return input_cost + output_cost

    def _update_metrics(
        self,
        success: bool,
        input_tokens: int = 0,
        output_tokens: int = 0,
        response_time_ms: float = 0,
    ) -> None:
        """
        Update global API metrics.

        Args:
            success: Whether the API call succeeded
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            response_time_ms: Response time in milliseconds
        """
        api_metrics["total_calls"] += 1
        api_metrics["last_call_timestamp"] = datetime.utcnow().isoformat()

        if success:
            api_metrics["successful_calls"] += 1
            api_metrics["total_input_tokens"] += input_tokens
            api_metrics["total_output_tokens"] += output_tokens
            api_metrics["total_response_time_ms"] += response_time_ms

            cost = self._calculate_cost(input_tokens, output_tokens)
            api_metrics["total_cost_usd"] += cost
        else:
            api_metrics["failed_calls"] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current API usage metrics.

        Returns:
            Dict with API usage statistics and cost estimation
        """
        total_calls = api_metrics["total_calls"]
        avg_response_time = (
            api_metrics["total_response_time_ms"] / api_metrics["successful_calls"]
            if api_metrics["successful_calls"] > 0
            else 0
        )

        return {
            "total_calls": total_calls,
            "successful_calls": api_metrics["successful_calls"],
            "failed_calls": api_metrics["failed_calls"],
            "success_rate": (
                api_metrics["successful_calls"] / total_calls
                if total_calls > 0
                else 0.0
            ),
            "total_input_tokens": api_metrics["total_input_tokens"],
            "total_output_tokens": api_metrics["total_output_tokens"],
            "total_cost_usd": round(api_metrics["total_cost_usd"], 4),
            "avg_response_time_ms": round(avg_response_time, 2),
            "last_call_timestamp": api_metrics["last_call_timestamp"],
        }

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
            raise RateLimitError(
                "Rate limit exceeded, timeout waiting for token")

        max_tokens = max_tokens or settings.llm_max_tokens
        temperature = temperature if temperature is not None else settings.llm_temperature

        start_time = time.time()
        input_tokens = 0
        output_tokens = 0

        try:
            logger.info(
                f"Calling Claude API with prompt length: {len(prompt)}")

            messages = [{"role": "user", "content": prompt}]

            response = self.client.messages.create(
                model=settings.llm_model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message if system_message else None,
                messages=messages,
            )

            # Calculate response time
            response_time_ms = (time.time() - start_time) * 1000

            # Extract response content
            content = response.content[0].text if response.content else ""

            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            # Calculate cost
            cost = self._calculate_cost(input_tokens, output_tokens)

            result = {
                "content": content,
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                },
                "model": response.model,
                "stop_reason": response.stop_reason,
                "cost_usd": round(cost, 6),
                "response_time_ms": round(response_time_ms, 2),
            }

            # Update metrics
            self._update_metrics(
                success=True,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                response_time_ms=response_time_ms,
            )

            logger.info(
                f"Claude API response: {input_tokens} input tokens, "
                f"{output_tokens} output tokens, "
                f"cost: ${cost:.6f}, "
                f"time: {response_time_ms:.2f}ms"
            )

            return result

        except RateLimitError as e:
            self._update_metrics(success=False)
            logger.error(f"Rate limit exceeded: {e}")
            raise
        except APIError as e:
            self._update_metrics(success=False)
            logger.error(f"Anthropic API error: {e}")
            raise
        except Exception as e:
            self._update_metrics(success=False)
            logger.error(f"Unexpected error calling Claude API: {e}")
            raise


# Global client instance
anthropic_client = AnthropicClient()
