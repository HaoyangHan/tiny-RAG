"""Tests for document processing service."""
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

from rag_memo_core_lib.services.parsers.factory import ParserFactory
from rag_memo_core_lib.services.parsers.pdf_parser import PDFParser
from rag_memo_core_lib.services.parsers.docx_parser import DOCXParser
from rag_memo_core_lib.services.parsers.image_parser import ImageParser
from rag_memo_core_lib.models.document import Document, DocumentMetadata

@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing."""
    return b"%PDF-1.4\nTest PDF content"

@pytest.fixture
def sample_docx_content():
    """Sample DOCX content for testing."""
    return b"PK\x03\x04Test DOCX content"

@pytest.fixture
def sample_image_content():
    """Sample image content for testing."""
    return b"Test image content"

@pytest.mark.asyncio
async def test_pdf_parser(core_settings, sample_pdf_content):
    """Test PDF document parsing."""
    with patch("builtins.open", mock_open(read_data=sample_pdf_content)):
        parser = PDFParser()
        document = Document(
            id="test-pdf",
            title="test.pdf",
            file_path="/path/to/test.pdf"
        )
        
        result = await parser.parse(document)
        
        assert result.content is not None
        assert isinstance(result.metadata, DocumentMetadata)
        assert result.metadata.mime_type == "application/pdf"

@pytest.mark.asyncio
async def test_docx_parser(core_settings, sample_docx_content):
    """Test DOCX document parsing."""
    with patch("builtins.open", mock_open(read_data=sample_docx_content)):
        parser = DOCXParser()
        document = Document(
            id="test-docx",
            title="test.docx",
            file_path="/path/to/test.docx"
        )
        
        result = await parser.parse(document)
        
        assert result.content is not None
        assert isinstance(result.metadata, DocumentMetadata)
        assert result.metadata.mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

@pytest.mark.asyncio
async def test_image_parser(core_settings, sample_image_content, mock_gemini):
    """Test image document parsing with OCR."""
    with patch("builtins.open", mock_open(read_data=sample_image_content)):
        with patch("rag_memo_core_lib.services.parsers.image_parser.Image") as mock_image:
            with patch("google.generativeai.GenerativeModel") as mock_model:
                mock_model.return_value.generate_content = AsyncMock(
                    return_value=MagicMock(text="Extracted text from image")
                )
                
                parser = ImageParser(settings=core_settings)
                document = Document(
                    id="test-image",
                    title="test.png",
                    file_path="/path/to/test.png"
                )
                
                result = await parser.parse(document)
                
                assert result.content == "Extracted text from image"
                assert isinstance(result.metadata, DocumentMetadata)
                assert result.metadata.mime_type in ["image/png", "image/jpeg", "image/tiff"]

def test_parser_factory():
    """Test parser factory creates correct parsers."""
    # Test PDF parser creation
    parser = ParserFactory.create_parser("application/pdf")
    assert isinstance(parser, PDFParser)
    
    # Test DOCX parser creation
    parser = ParserFactory.create_parser("application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    assert isinstance(parser, DOCXParser)
    
    # Test image parser creation
    parser = ParserFactory.create_parser("image/png")
    assert isinstance(parser, ImageParser)
    
    # Test invalid mime type
    with pytest.raises(ValueError):
        ParserFactory.create_parser("invalid/mime-type")

@pytest.mark.asyncio
async def test_parser_error_handling():
    """Test parser error handling."""
    with patch("builtins.open", mock_open()) as mock_file:
        mock_file.side_effect = IOError("File not found")
        
        parser = PDFParser()
        document = Document(
            id="test-error",
            title="test.pdf",
            file_path="/path/to/nonexistent.pdf"
        )
        
        with pytest.raises(IOError) as exc_info:
            await parser.parse(document)
        
        assert "File not found" in str(exc_info.value) 