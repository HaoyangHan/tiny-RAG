"""Tests for evaluation service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from rag_memo_core_lib.services.evaluation.evaluator import MemoEvaluator
from rag_memo_core_lib.services.evaluation.metrics import (
    CitationAccuracy,
    ContentRelevance,
    TextQuality
)
from rag_memo_core_lib.models.evaluation import (
    EvaluationResult,
    EvaluationMetrics,
    CitationValidation
)

@pytest.fixture
def sample_memo_content():
    """Sample memo content for testing."""
    return """
    According to the document[1], this is a test memo.
    The document also states[2] that we should test thoroughly.
    
    Citations:
    [1] Page 1: "This is a test document content."
    [2] Page 2: "Testing should be thorough and comprehensive."
    """

@pytest.fixture
def sample_evaluation_metrics():
    """Sample evaluation metrics for testing."""
    return EvaluationMetrics(
        citation_accuracy=0.95,
        content_relevance=0.85,
        text_quality=0.90,
        overall_score=0.90
    )

@pytest.mark.asyncio
async def test_citation_accuracy(
    core_settings,
    mock_openai,
    sample_document,
    sample_memo_content
):
    """Test citation accuracy evaluation."""
    evaluator = CitationAccuracy(settings=core_settings)
    
    with patch("rag_memo_core_lib.services.evaluation.metrics.OpenAI") as mock_openai_cls:
        mock_openai_cls.return_value = mock_openai
        mock_openai.chat.completions.create.return_value.choices[0].message.content = "0.95"
        
        result = await evaluator.evaluate(
            memo_content=sample_memo_content,
            source_documents=[sample_document]
        )
        
        assert isinstance(result, float)
        assert 0 <= result <= 1
        assert result == 0.95

@pytest.mark.asyncio
async def test_content_relevance(
    core_settings,
    mock_openai,
    sample_document,
    sample_memo_content
):
    """Test content relevance evaluation."""
    evaluator = ContentRelevance(settings=core_settings)
    
    with patch("rag_memo_core_lib.services.evaluation.metrics.OpenAI") as mock_openai_cls:
        mock_openai_cls.return_value = mock_openai
        mock_openai.chat.completions.create.return_value.choices[0].message.content = "0.85"
        
        result = await evaluator.evaluate(
            memo_content=sample_memo_content,
            source_documents=[sample_document]
        )
        
        assert isinstance(result, float)
        assert 0 <= result <= 1
        assert result == 0.85

@pytest.mark.asyncio
async def test_text_quality(
    core_settings,
    mock_openai,
    sample_memo_content
):
    """Test text quality evaluation."""
    evaluator = TextQuality(settings=core_settings)
    
    with patch("rag_memo_core_lib.services.evaluation.metrics.OpenAI") as mock_openai_cls:
        mock_openai_cls.return_value = mock_openai
        mock_openai.chat.completions.create.return_value.choices[0].message.content = "0.90"
        
        result = await evaluator.evaluate(
            memo_content=sample_memo_content
        )
        
        assert isinstance(result, float)
        assert 0 <= result <= 1
        assert result == 0.90

@pytest.mark.asyncio
async def test_memo_evaluator(
    core_settings,
    mock_openai,
    sample_document,
    sample_memo_content,
    sample_evaluation_metrics
):
    """Test complete memo evaluation."""
    evaluator = MemoEvaluator(settings=core_settings)
    
    with patch("rag_memo_core_lib.services.evaluation.evaluator.OpenAI") as mock_openai_cls:
        mock_openai_cls.return_value = mock_openai
        
        # Mock individual metric evaluations
        with patch.object(CitationAccuracy, "evaluate", return_value=0.95), \
             patch.object(ContentRelevance, "evaluate", return_value=0.85), \
             patch.object(TextQuality, "evaluate", return_value=0.90):
            
            result = await evaluator.evaluate(
                memo_content=sample_memo_content,
                source_documents=[sample_document]
            )
            
            assert isinstance(result, EvaluationResult)
            assert result.metrics == sample_evaluation_metrics
            assert len(result.citation_validations) > 0

@pytest.mark.asyncio
async def test_evaluation_error_handling(
    core_settings,
    mock_openai,
    sample_document,
    sample_memo_content
):
    """Test evaluation error handling."""
    evaluator = MemoEvaluator(settings=core_settings)
    
    with patch("rag_memo_core_lib.services.evaluation.evaluator.OpenAI") as mock_openai_cls:
        mock_openai_cls.return_value = mock_openai
        mock_openai.chat.completions.create.side_effect = Exception("API Error")
        
        with pytest.raises(Exception) as exc_info:
            await evaluator.evaluate(
                memo_content=sample_memo_content,
                source_documents=[sample_document]
            )
        
        assert "API Error" in str(exc_info.value) 