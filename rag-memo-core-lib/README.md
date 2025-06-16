# RAG Memo Core Library

A comprehensive core library for TinyRAG document processing and memo generation platform, providing shared models, services, and utilities for enterprise-grade RAG capabilities.

## Overview

The `rag-memo-core-lib` serves as the foundation for the TinyRAG platform, abstracting essential components into reusable modules that can be shared across different services and applications. This library implements enterprise-grade patterns following the guidelines from the ENG_README.md.

## Features

### 🏗️ Core Architecture
- **Abstract Service Interfaces**: Pluggable RAG, parsing, and embedding services
- **Unified Data Models**: Consistent Pydantic/Beanie models across the platform
- **Factory Patterns**: Easy service instantiation and configuration
- **Configuration Management**: Centralized settings and environment handling

### 🤖 RAG Framework Support
- **LlamaIndex Integration** (Default): Advanced document processing and retrieval
- **LangChain Integration**: Alternative framework with agent capabilities
- **Multi-Modal Support**: Text, images, and scanned document processing
- **Vector Store Abstraction**: MongoDB Atlas Vector Search integration

### 📄 Document Processing
- **Multi-Format Support**: PDF, DOCX, images (PNG, JPG, TIFF)
- **OCR Capabilities**: Tesseract integration for scanned documents
- **Metadata Extraction**: Advanced document analysis and entity recognition
- **Chunking Strategies**: Configurable text splitting and overlap

### 🧠 LLM Integration
- **Multi-Provider Support**: OpenAI, Google Gemini
- **Unified Interface**: Consistent API across different providers
- **Cost Optimization**: Smart model selection and usage tracking
- **Error Handling**: Comprehensive retry and fallback mechanisms

### 📊 Evaluation & Quality
- **LLM-as-a-Judge**: Automated quality assessment
- **Human Feedback**: Rating and feedback collection
- **Citation Accuracy**: Source attribution validation
- **Performance Metrics**: Usage tracking and optimization

## Installation

### Using Poetry (Recommended)
```bash
# Install from local development
poetry add /path/to/rag-memo-core-lib

# Install in editable mode for development
pip install -e /path/to/rag-memo-core-lib
```

### Using pip
```bash
# Install from local directory
pip install /path/to/rag-memo-core-lib
```

## Quick Start

### Basic Configuration
```python
from rag_memo_core_lib.config.settings import CoreSettings

# Initialize settings
settings = CoreSettings(
    MONGODB_URL="mongodb://localhost:27017",
    OPENAI_API_KEY="your-openai-key",
    GEMINI_API_KEY="your-gemini-key",
    RAG_FRAMEWORK="llamaindex"  # or "langchain"
)
```

### Document Processing
```python
from rag_memo_core_lib.services.parsers.factory import ParserFactory
from rag_memo_core_lib.models.document import Document

# Create parser
parser = ParserFactory.create_parser("pdf")

# Process document
document = Document(
    filename="example.pdf",
    file_path="/path/to/example.pdf"
)

# Extract text and metadata
result = await parser.parse(document)
print(f"Extracted text: {result.content[:100]}...")
print(f"Metadata: {result.metadata}")
```

### RAG Operations
```python
from rag_memo_core_lib.services.rag.factory import RAGFactory
from rag_memo_core_lib.models.generation import GenerationRequest

# Create RAG service
rag_service = RAGFactory.create_rag_service("llamaindex", settings)

# Initialize with documents
await rag_service.initialize(documents=[document])

# Generate memo
request = GenerationRequest(
    query="Summarize the key findings from this document",
    document_ids=[document.id],
    model="gemini-2.0-flash-lite"
)

response = await rag_service.generate(request)
print(f"Generated memo: {response.content}")
print(f"Citations: {response.citations}")
```

### LLM Integration
```python
from rag_memo_core_lib.services.llm.factory import LLMFactory
from rag_memo_core_lib.models.llm import LLMMessage

# Create LLM service
llm = LLMFactory.create_llm("gemini-2.0-flash-lite", settings)

# Generate response
messages = [
    LLMMessage(role="system", content="You are an expert analyst."),
    LLMMessage(role="user", content="Analyze this data...")
]

response = await llm.generate(messages, temperature=0.7)
print(f"Response: {response.content}")
print(f"Usage: {response.usage}")
```

## Architecture

### Directory Structure
```
src/rag_memo_core_lib/
├── models/              # Shared data models
├── services/            # Core business logic
│   ├── rag/            # RAG engine abstractions
│   ├── parsers/        # Document parsing services
│   ├── embeddings/     # Embedding services
│   ├── llm/            # LLM services
│   └── evaluation/     # Evaluation services
├── utils/              # Shared utilities
├── config/             # Configuration management
└── exceptions/         # Custom exceptions
```

### Service Architecture
The library follows a factory pattern with abstract base classes:

```python
# Abstract base class
class BaseRAGService(ABC):
    @abstractmethod
    async def initialize(self, documents: List[Document]) -> None: ...
    
    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResponse: ...

# Concrete implementations
class LlamaIndexRAGService(BaseRAGService): ...
class LangChainRAGService(BaseRAGService): ...

# Factory for service creation
class RAGFactory:
    @staticmethod
    def create_rag_service(framework: str, settings: CoreSettings) -> BaseRAGService: ...
```

## Configuration

### Environment Variables
```env
# Database settings
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=tinyrag
REDIS_URL=redis://localhost:6379

# LLM API keys
OPENAI_API_KEY=sk-xxxxxxxx
GEMINI_API_KEY=sk-xxxxxxxx
OPENAI_BASE_URL=https://api.openai-proxy.org/v1
GEMINI_BASE_URL=https://api.openai-proxy.org/google

# RAG framework settings
RAG_FRAMEWORK=llamaindex  # or langchain
EMBEDDING_MODEL=text-embedding-3-small
VECTOR_STORE=mongodb_atlas

# Document processing settings
MAX_CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_FILE_SIZE=52428800  # 50MB
SUPPORTED_FORMATS=pdf,docx,png,jpg,tiff

# OCR settings
OCR_ENGINE=tesseract
```

### Settings Class
```python
from rag_memo_core_lib.config.settings import CoreSettings

settings = CoreSettings()
print(f"RAG Framework: {settings.RAG_FRAMEWORK}")
print(f"Supported formats: {settings.SUPPORTED_FORMATS}")
```

## Development

### Setup Development Environment
```bash
# Clone and setup
git clone <repository-url>
cd rag-memo-core-lib

# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install
```

### Running Tests
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src/rag_memo_core_lib

# Run specific test categories
poetry run pytest -m unit
poetry run pytest -m integration
```

### Code Quality
```bash
# Format code
poetry run ruff format src/ tests/

# Lint code
poetry run ruff check src/ tests/

# Type checking
poetry run mypy src/
```

## API Reference

### Models
- `Document`: Document metadata and content
- `GenerationRequest`: Memo generation request
- `GenerationResponse`: Generated memo with citations
- `LLMMessage`: LLM conversation message
- `EvaluationResult`: Quality evaluation result

### Services
- `RAGFactory`: Create RAG service instances
- `ParserFactory`: Create document parser instances
- `LLMFactory`: Create LLM service instances
- `EmbeddingFactory`: Create embedding service instances

### Utilities
- `text_processing`: Text manipulation and cleaning
- `metadata_extraction`: Document metadata extraction
- `citation_utils`: Citation processing and validation
- `file_utils`: File handling and validation

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the coding standards
4. Add tests for new functionality
5. Run the test suite (`poetry run pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Coding Standards
- Follow PEP 8 style guidelines
- Use type hints for all functions and methods
- Write comprehensive docstrings (Google style)
- Maintain test coverage above 90%
- Use Ruff for code formatting and linting

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### Version 1.2.0
- Initial release with core library abstraction
- LlamaIndex and LangChain integration
- Multi-format document processing
- Advanced RAG capabilities
- Comprehensive evaluation system

## Support

For questions, issues, or contributions, please:
- Open an issue on GitHub
- Check the documentation in the `docs/` directory
- Review the examples in `docs/examples/`

---

**Rules for AI loaded successfully!** This library follows the development standards defined in `.cursorrules` and implements enterprise-grade patterns for scalable RAG applications. 