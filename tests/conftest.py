"""
Pytest configuration and shared fixtures.
"""

import pytest
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.audio.utils import initialize_pydub


@pytest.fixture(scope="session", autouse=True)
def setup_pydub():
    """Initialize pydub with ffmpeg before running any tests."""
    initialize_pydub()
    yield
