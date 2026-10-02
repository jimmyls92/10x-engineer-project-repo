"""Test fixtures for PromptLab"""

import itertools
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from app.api import app
from app import models
from app.storage import storage


@pytest.fixture
def client():
    """Create a test client for the API."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage():
    """Clear storage before each test."""
    storage.clear()
    yield
    storage.clear()


@pytest.fixture
def sample_prompt_data():
    """Sample prompt data for testing."""
    return {
        "title": "Code Review Prompt",
        "content": "Review the following code and provide feedback:\n\n{{code}}",
        "description": "A prompt for AI code review"
    }


@pytest.fixture
def sample_collection_data():
    """Sample collection data for testing."""
    return {
        "name": "Development",
        "description": "Prompts for development tasks"
    }


@pytest.fixture
def ticking_clock(monkeypatch):
    """Make the clock behind ``get_current_time()`` advance 1 µs on every call.

    The real clock is coarse on some platforms (Python 3.12 on Windows steps
    about every millisecond), so two timestamps from back-to-back requests can
    be equal and a strict comparison can fail for no reason. This replaces the
    ``datetime`` that ``app.models`` reads with a subclass whose ``utcnow()``
    returns a new value each call, so every timestamp is distinct and in call
    order. The application code still runs unchanged.

    Args:
        monkeypatch: pytest's monkeypatch fixture; the patch is undone after
            the test.
    """
    start = datetime(2026, 1, 1)
    ticks = itertools.count()

    class TickingDatetime(datetime):
        @classmethod
        def utcnow(cls):
            return start + timedelta(microseconds=next(ticks))

    monkeypatch.setattr(models, "datetime", TickingDatetime)
