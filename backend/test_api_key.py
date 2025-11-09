#!/usr/bin/env python3
"""Quick test script to verify API key configuration."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from core.config import settings

    print("✅ Configuration loaded successfully!")
    print(f"\nApp Name: {settings.app_name}")
    print(f"Debug Mode: {settings.debug}")
    print(f"LLM Model: {settings.llm_model}")

    # Check if API key is set (don't print the actual key!)
    if settings.anthropic_api_key and len(settings.anthropic_api_key) > 10:
        print(
            f"✅ Anthropic API Key: Configured (length: {len(settings.anthropic_api_key)})")
    else:
        print("❌ Anthropic API Key: NOT SET or invalid")

    if settings.secret_key and len(settings.secret_key) > 10:
        print(f"✅ Secret Key: Configured (length: {len(settings.secret_key)})")
    else:
        print("❌ Secret Key: NOT SET or invalid")

    print(f"\nDatabase URL: {settings.database_url}")

except Exception as e:
    print(f"❌ Error loading configuration: {e}")
    sys.exit(1)
