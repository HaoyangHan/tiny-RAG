# TinyRAG Integrated Version Plan

## Project Evolution Overview

TinyRAG has evolved from a simple PDF-to-memo generation tool to a comprehensive document processing and memo generation platform with advanced LLM capabilities.

## Version History & Integration

### Version 1.0 - MVP Foundation ✅
**Status: Completed**

#### Core Components Delivered
- **Frontend (`rag-memo-ui`)**: Next.js with TypeScript, Tailwind CSS
- **Backend (`rag-memo-api`)**: FastAPI with MongoDB and Redis
- **Document Processing**: PDF text extraction and basic metadata
- **RAG Engine**: Basic text chunking, embeddings, and retrieval
- **Memo Generation**: Simple LLM-based memo creation with citations
- **Infrastructure**: Docker containerization with docker-compose

#### Key Features
- Single PDF upload interface
- Basic memo generation with text citations
- Asynchronous processing with Dramatiq
- JWT authentication system
- RESTful API endpoints

### Version 1.1 - Enhanced LLM Capabilities ✅
**Status: Completed**

#### Major Enhancements
- **Multi-LLM Provider Support**:
  - Google Gemini (gemini-2.0-flash-lite as default)
  - OpenAI (gpt-4-mini-2025-04-16)
  - Unified LLM Factory architecture
- **Enhanced Services**:
  - Improved citation extraction
  - Model selection capabilities
  - Cost optimization through model selection
- **API Improvements**:
  - New `/api/v1/memos/models` endpoint
  - Enhanced memo creation with model parameter
  - Comprehensive error handling

#### Technical Achievements
- Removed LangChain dependencies in favor of direct API integration
- Implemented proxy endpoint support
- Added comprehensive logging and monitoring
- Maintained backward compatibility with v1.0

---

## Version 1.2 - Advanced RAG Framework Integration 🚀
**Status: Planned**

### Overview
Version 1.2 introduces enterprise-grade RAG capabilities through LangChain and LlamaIndex integration, with LlamaIndex as the default framework. This version also abstracts essential modules into the `rag-memo-core-lib` for better modularity and reusability.

### Core Objectives
1. **Advanced RAG Capabilities**: Implement sophisticated document processing and retrieval
2. **Framework Integration**: LangChain + LlamaIndex with LlamaIndex as default
3. **Core Library Abstraction**: Move essential modules to `rag-memo-core-lib`
4. **Enterprise Features**: Multi-format support, advanced metadata extraction, query transformation

### Key Features

#### 1. Advanced RAG Framework Integration
- **LlamaIndex (Default)**:
  - `IngestionPipeline` for document processing
  - `VectorStoreIndex` for advanced retrieval
  - `ResponseSynthesizer` for context-aware generation
  - Multi-modal support for images and scanned PDFs
- **LangChain (Alternative)**:
  - Document loaders for various formats
  - Text splitters and embeddings
  - Retrieval chains and memory management
  - Agent-based workflows

#### 2. Enhanced Document Processing
- **Multi-format Support**:
  - PDF (text and scanned)
  - DOCX, DOC
  - Images (PNG, JPG, TIFF) with OCR
  - HTML and Markdown
- **Advanced Metadata Extraction**:
  - Document structure analysis
  - Entity recognition
  - Keyword extraction
  - Temporal information extraction

#### 3. Core Library Abstraction (`rag-memo-core-lib`)
Following the enterprise architecture guidelines from `ENG_README.md`:

```
rag-memo-core-lib/
├── src/
│   ├── models/              # Shared data models
│   │   ├── document.py      # Document models
│   │   ├── generation.py    # Generation models
│   │   ├── project.py       # Project models
│   │   └── evaluation.py    # Evaluation models
│   ├── services/            # Core business logic
│   │   ├── rag/            # RAG engine abstractions
│   │   │   ├── base.py     # Abstract RAG interface
│   │   │   ├── llamaindex.py # LlamaIndex implementation
│   │   │   └── langchain.py  # LangChain implementation
│   │   ├── parsers/        # Document parsing services
│   │   │   ├── base.py     # Abstract parser interface
│   │   │   ├── pdf.py      # PDF parser
│   │   │   ├── docx.py     # DOCX parser
│   │   │   └── image.py    # Image/OCR parser
│   │   └── embeddings/     # Embedding services
│   │       ├── base.py     # Abstract embedding interface
│   │       └── openai.py   # OpenAI embeddings
│   ├── utils/              # Shared utilities
│   │   ├── text_processing.py
│   │   ├── metadata_extraction.py
│   │   └── citation_utils.py
│   └── config/             # Configuration management
│       ├── settings.py     # Shared settings
│       └── constants.py    # Application constants
├── tests/                  # Comprehensive test suite
└── pyproject.toml         # Poetry configuration
```

#### 4. Advanced RAG Capabilities
- **Query Transformation**:
  - Query expansion and refinement
  - Multi-query generation
  - Context-aware query optimization
- **Retrieval Enhancement**:
  - Hybrid search (vector + keyword)
  - Metadata filtering
  - Re-ranking algorithms
  - Multi-document retrieval
- **Generation Improvements**:
  - Context-aware synthesis
  - Citation accuracy enhancement
  - Multi-step reasoning
  - Quality evaluation integration

#### 5. Evaluation & Quality Assurance
- **LLM-as-a-Judge Integration**:
  - Automated quality scoring
  - Faithfulness evaluation
  - Relevance assessment
  - Citation accuracy validation
- **Human Feedback Loop**:
  - Rating system integration
  - Feedback collection and analysis
  - Continuous improvement metrics

### Technical Architecture

#### Backend Enhancements (`rag-memo-api`)
```
rag-memo-api/
├── services/
│   ├── rag_orchestrator.py     # NEW: RAG framework orchestration
│   ├── document_processor.py   # ENHANCED: Multi-format processing
│   ├── query_transformer.py    # NEW: Query transformation service
│   └── evaluation_service.py   # NEW: Quality evaluation service
├── routes/
│   ├── documents.py           # ENHANCED: Multi-format upload
│   ├── memos.py              # ENHANCED: Advanced generation
│   └── evaluation.py         # NEW: Evaluation endpoints
└── dependencies.py           # UPDATED: Core library integration
```

#### Core Library Integration
- **Shared Models**: All Pydantic/Beanie models moved to core library
- **Service Abstractions**: Abstract interfaces for RAG, parsing, and embeddings
- **Configuration Management**: Centralized settings and constants
- **Utility Functions**: Shared text processing and citation utilities

### Development Phases

#### Phase 1: Core Library Foundation (Week 1-2)
- Set up `rag-memo-core-lib` with Poetry/Rye
- Migrate shared models from API to core library
- Create abstract interfaces for RAG, parsing, and embeddings
- Implement LlamaIndex-based RAG service
- Set up comprehensive testing framework

#### Phase 2: LangChain Integration (Week 3)
- Implement LangChain-based RAG service
- Create framework selection mechanism
- Add multi-format document parsing
- Implement query transformation service

#### Phase 3: Advanced Features (Week 4-5)
- Multi-modal document processing (images, scanned PDFs)
- Advanced metadata extraction
- Hybrid search implementation
- Citation accuracy improvements

#### Phase 4: Evaluation & Quality (Week 6)
- LLM-as-a-Judge integration
- Human feedback system
- Quality metrics dashboard
- Performance optimization

#### Phase 5: Integration & Testing (Week 7-8)
- Backend integration with core library
- Frontend enhancements for new features
- Comprehensive testing and validation
- Documentation and deployment

### Success Metrics

#### Functionality
- Multi-format document processing (PDF, DOCX, images)
- Advanced RAG capabilities with both frameworks
- Improved citation accuracy (>95%)
- Quality evaluation system operational

#### Performance
- Document processing time < 20 seconds (multi-format)
- Memo generation time < 45 seconds (complex documents)
- Framework switching overhead < 2 seconds
- API response time < 150ms

#### Quality
- Citation accuracy > 95%
- Content relevance score > 4.5/5
- User satisfaction > 90%
- System reliability > 99.5%

### Migration Strategy

#### From v1.1 to v1.2
1. **Core Library Setup**:
   - Install `rag-memo-core-lib` as dependency
   - Migrate shared models and utilities
   - Update import statements

2. **Service Enhancement**:
   - Replace direct LLM calls with RAG framework integration
   - Add multi-format document processing
   - Implement query transformation

3. **API Updates**:
   - New endpoints for advanced features
   - Enhanced document upload with format detection
   - Evaluation and feedback endpoints

### Dependencies Updates

#### Core Library (`rag-memo-core-lib`)
```toml
[tool.poetry.dependencies]
python = "^3.11"
pydantic = "^2.6.1"
beanie = "^1.24.0"
llama-index = "^0.10.0"
langchain = "^0.1.0"
langchain-community = "^0.0.20"
```

#### Backend API (`rag-memo-api`)
```txt
# Add to existing requirements.txt
llama-index==0.10.0
langchain==0.1.0
langchain-community==0.0.20
pytesseract==0.3.10
pillow==10.2.0
python-docx==1.1.0
```

### Configuration Enhancements

#### Environment Variables
```env
# Existing variables maintained
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=sk-xxxxxxxx
GEMINI_API_KEY=sk-xxxxxxxx

# New RAG framework settings
RAG_FRAMEWORK=llamaindex  # or langchain
EMBEDDING_MODEL=text-embedding-3-small
VECTOR_STORE=mongodb_atlas
OCR_ENGINE=tesseract

# Document processing settings
MAX_CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_FILE_SIZE=50MB
SUPPORTED_FORMATS=pdf,docx,png,jpg,tiff
```

### Future Roadmap (v1.3+)

#### Planned Enhancements
- **Agent-based Workflows**: Multi-step reasoning and planning
- **Real-time Collaboration**: Multi-user document editing
- **Advanced Analytics**: Usage patterns and optimization insights
- **Custom Model Training**: Domain-specific model fine-tuning
- **API Ecosystem**: Third-party integrations and webhooks

#### Enterprise Features
- **SSO Integration**: Enterprise authentication systems
- **Audit Logging**: Comprehensive activity tracking
- **Data Governance**: Privacy and compliance features
- **Scalability**: Kubernetes deployment and auto-scaling

## Conclusion

Version 1.2 represents a significant architectural evolution, introducing enterprise-grade RAG capabilities while maintaining the simplicity and effectiveness established in previous versions. The core library abstraction provides a solid foundation for future enhancements and ensures code reusability across the platform.

The integration of LangChain and LlamaIndex, with LlamaIndex as the default, provides flexibility and advanced capabilities while maintaining performance and reliability. This version positions TinyRAG as a comprehensive document analysis and memo generation platform suitable for enterprise deployment. 