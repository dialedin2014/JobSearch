"""
LLM service dependency injection.

This module provides FastAPI dependencies for accessing LLM services.
"""

from fastapi import Depends
from src.integrations.anthropic_client import anthropic_client, AnthropicClient


async def get_llm_service() -> AnthropicClient:
    """
    Dependency for getting LLM service (Anthropic Claude).
    
    Returns:
        AnthropicClient: Anthropic API client instance
    """
    return anthropic_client
