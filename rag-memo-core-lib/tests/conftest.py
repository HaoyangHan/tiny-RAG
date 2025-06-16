"""Common test fixtures and configurations."""
import os
import pytest
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import motor.motor_asyncio
from beanie import init_beanie
from mongomock_motor import AsyncMongoMockClient

from rag_memo_core_lib.config.settings import CoreSettings
from rag_memo_core_lib.models.document import Document
from rag_memo_core_lib.models.project import Project

@pytest.fixture
def core_settings() -> CoreSettings:
    """Fixture for test settings."""
    return CoreSettings(
        MONGODB_URL="mongodb://test:test@localhost:27017/test",
        OPENAI_API_KEY="test-key",
        GEMINI_API_KEY="test-key",
        RAG_FRAMEWORK="llamaindex",
        DEBUG=True
    )

@pytest.fixture
async def mock_mongodb() -> AsyncGenerator[AsyncMongoMockClient, None]:
    """Fixture for mock MongoDB client."""
    client = AsyncMongoMockClient()
    await init_beanie(
        database=client.get_database("test"),
        document_models=[Document, Project]
    )
    yield client
    await client.close()

@pytest.fixture
def mock_openai() -> Generator[MagicMock, None, None]:
    """Fixture for mock OpenAI client."""
    mock = MagicMock()
    mock.embeddings.create = AsyncMock()
    mock.chat.completions.create = AsyncMock()
    yield mock

@pytest.fixture
def mock_gemini() -> Generator[MagicMock, None, None]:
    """Fixture for mock Gemini client."""
    mock = MagicMock()
    mock.generate_content = AsyncMock()
    yield mock

@pytest.fixture
def sample_document() -> Document:
    """Fixture for a sample document."""
    return Document(
        id="test-doc-1",
        title="Test Document",
        content="This is a test document content.",
        metadata={
            "author": "Test Author",
            "created_at": "2024-03-01"
        },
        embedding=None
    )

@pytest.fixture
def sample_project() -> Project:
    """Fixture for a sample project."""
    return Project(
        id="test-proj-1",
        name="Test Project",
        description="Test project description",
        document_ids=["test-doc-1"]
    ) 