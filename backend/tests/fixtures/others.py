"""Test data fixtures for various models."""

import pytest
from sqlalchemy.orm import Session

from app import models
from tests.utils.create_data.core import create_ai_prompts


@pytest.fixture
def test_ai_prompts(session: Session) -> tuple[models.AiSystemPrompt, models.AiJobPromptTemplate]:
    """Create test AI prompts for job rating"""
    return create_ai_prompts(session)
