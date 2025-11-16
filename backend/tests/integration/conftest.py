"""
Integration tests configuration.
This conftest overrides the parent conftest to avoid loading the full application.
"""
import pytest
import sys
from pathlib import Path

# Add backend to path for imports
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "live_api: marks tests that make real API calls (deselect with '-m \"not live_api\"')"
    )
