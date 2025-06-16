"""Tests for RAG service implementations."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from rag_memo_core_lib.services.rag.factory import RAGFactory
from rag_memo_core_lib.services.rag.llamaindex_rag import LlamaIndexRAG
from rag_memo_core_lib.services.rag.langchain_rag import LangChainRAG
from rag_memo_core_lib.models.generation import GenerationRequest, GenerationResponse

@pytest.mark.asyncio
async def test_llamaindex_rag_initialization(
    core_settings,
    mock_openai,
    sample_document
):
    """Test LlamaIndex RAG service initialization."""
    with patch("rag_memo_core_lib.services.rag.llamaindex_rag.OpenAI") as mock_openai_cls:
        mock_openai_cls.return_value = mock_openai
        
        rag_service = LlamaIndexRAG(settings=core_settings)
        await rag_service.initialize(documents=[sample_document])
        
        # Verify document was processed
        assert len(rag_service.index.documents) == 1
        assert rag_service.index.documents[0].text == sample_document.content

@pytest.mark.asyncio
async def test_llamaindex_rag_generation(
    core_settings,
    mock_openai,
    sample_document
):
    """Test memo generation with LlamaIndex RAG."""
    with patch("rag_memo_core_lib.services.rag.llamaindex_rag.OpenAI") as mock_openai_cls:
        mock_openai_cls.return_value = mock_openai
        
        # Mock LLM response
        mock_openai.chat.completions.create.return_value.choices[0].message.content = "Test memo"
        
        rag_service = LlamaIndexRAG(settings=core_settings)
        await rag_service.initialize(documents=[sample_document])
        
        request = GenerationRequest(
            query="Summarize the document",
            document_ids=[sample_document.id],
            model="gpt-4"
        )
        
        response = await rag_service.generate(request)
        
        assert isinstance(response, GenerationResponse)
        assert response.content == "Test memo"
        assert len(response.citations) > 0

@pytest.mark.asyncio
async def test_langchain_rag_initialization(
    core_settings,
    mock_openai,
    sample_document
):
    """Test LangChain RAG service initialization."""
    with patch("rag_memo_core_lib.services.rag.langchain_rag.OpenAI") as mock_openai_cls:
        mock_openai_cls.return_value = mock_openai
        
        rag_service = LangChainRAG(settings=core_settings)
        await rag_service.initialize(documents=[sample_document])
        
        # Verify document was processed
        assert len(rag_service.document_store) == 1

@pytest.mark.asyncio
async def test_rag_factory_creation(core_settings):
    """Test RAG factory creates correct service."""
    # Test LlamaIndex creation
    core_settings.RAG_FRAMEWORK = "llamaindex"
    rag_service = RAGFactory.create_rag_service(core_settings)
    assert isinstance(rag_service, LlamaIndexRAG)
    
    # Test LangChain creation
    core_settings.RAG_FRAMEWORK = "langchain"
    rag_service = RAGFactory.create_rag_service(core_settings)
    assert isinstance(rag_service, LangChainRAG)
    
    # Test invalid framework
    core_settings.RAG_FRAMEWORK = "invalid"
    with pytest.raises(ValueError):
        RAGFactory.create_rag_service(core_settings)

@pytest.mark.asyncio
async def test_rag_error_handling(
    core_settings,
    mock_openai,
    sample_document
):
    """Test RAG service error handling."""
    with patch("rag_memo_core_lib.services.rag.llamaindex_rag.OpenAI") as mock_openai_cls:
        mock_openai_cls.return_value = mock_openai
        
        # Mock LLM error
        mock_openai.chat.completions.create.side_effect = Exception("API Error")
        
        rag_service = LlamaIndexRAG(settings=core_settings)
        await rag_service.initialize(documents=[sample_document])
        
        request = GenerationRequest(
            query="Summarize the document",
            document_ids=[sample_document.id],
            model="gpt-4"
        )
        
        with pytest.raises(Exception) as exc_info:
            await rag_service.generate(request)
        
        assert "API Error" in str(exc_info.value) 