# TinyRAG Integrated Project Structure

## Repository Organization Evolution

The project has evolved from a simple two-repository structure to a comprehensive three-repository architecture with shared core library abstraction.

### Current Architecture (v1.1) ✅

#### 1. `rag-memo-api` (Backend)
```
rag-memo-api/
├── main.py                    # FastAPI application entry point
├── dependencies.py            # Dependency injection
├── routes/                    # API route handlers
│   ├── documents.py          # Document upload and management
│   ├── memos.py             # Memo generation endpoints
│   └── auth.py              # Authentication routes
├── models/                   # Pydantic models
│   ├── document.py          # Document models
│   ├── memo.py              # Memo models
│   └── user.py              # User models
├── services/                 # Business logic
│   ├── llm_factory.py       # LLM provider abstraction
│   ├── memo_generator.py    # Memo generation service
│   ├── document_processor.py # Document processing
│   └── auth_service.py      # Authentication service
├── workers/                  # Dramatiq task definitions
│   └── tasks.py             # Async task implementations
├── tests/                    # Test suite
├── docker/                   # Docker configuration
├── requirements.txt          # Python dependencies
└── README.md                # Project documentation
```

#### 2. `rag-memo-ui` (Frontend)
```
rag-memo-ui/
├── src/
│   ├── components/          # React components
│   │   ├── DocumentUpload/  # Document upload component
│   │   ├── MemoViewer/      # Memo display component
│   │   └── ui/              # Reusable UI components
│   ├── services/            # API client services
│   │   └── api.ts           # API client
│   ├── store/               # Zustand state management
│   │   └── useStore.ts      # Application state
│   ├── types/               # TypeScript definitions
│   └── utils/               # Helper functions
├── public/                  # Static assets
├── tests/                   # Frontend tests
├── package.json             # Node.js dependencies
└── README.md               # Frontend documentation
```

#### 3. `rag-memo-core-lib` (Shared Library - Basic)
```
rag-memo-core-lib/
├── src/
│   ├── models/              # Basic shared models
│   │   └── utils/               # Basic utilities
│   └── tests/                   # Library tests
```

---

## Enhanced Architecture (v1.2) 🚀

### Core Library Transformation (`rag-memo-core-lib`)

Following enterprise architecture principles from `ENG_README.md`:

```
rag-memo-core-lib/
├── src/
│   ├── models/                    # Shared data models
│   │   ├── __init__.py
│   │   ├── base.py               # Base model classes
│   │   ├── document.py           # Document models
│   │   ├── generation.py         # Generation models
│   │   ├── project.py            # Project models
│   │   ├── evaluation.py         # Evaluation models
│   │   └── user.py               # User models
│   ├── services/                  # Core business logic
│   │   ├── __init__.py
│   │   ├── rag/                  # RAG engine abstractions
│   │   │   ├── __init__.py
│   │   │   ├── base.py           # Abstract RAG interface
│   │   │   ├── llamaindex_rag.py # LlamaIndex implementation
│   │   │   ├── langchain_rag.py  # LangChain implementation
│   │   │   └── factory.py        # RAG factory
│   │   ├── parsers/              # Document parsing services
│   │   │   ├── __init__.py
│   │   │   ├── base.py           # Abstract parser interface
│   │   │   ├── pdf_parser.py     # PDF parser
│   │   │   ├── docx_parser.py    # DOCX parser
│   │   │   ├── image_parser.py   # Image/OCR parser
│   │   │   └── factory.py        # Parser factory
│   │   ├── embeddings/           # Embedding services
│   │   │   ├── __init__.py
│   │   │   ├── base.py           # Abstract embedding interface
│   │   │   ├── openai_embeddings.py # OpenAI embeddings
│   │   │   └── factory.py        # Embedding factory
│   │   ├── llm/                  # LLM services (from v1.1)
│   │   │   ├── __init__.py
│   │   │   ├── base.py           # Abstract LLM interface
│   │   │   ├── openai_llm.py     # OpenAI implementation
│   │   │   ├── gemini_llm.py     # Gemini implementation
│   │   │   └── factory.py        # LLM factory
│   │   └── evaluation/           # Evaluation services
│   │       ├── __init__.py
│   │       ├── base.py           # Abstract evaluator interface
│   │       ├── llm_judge.py      # LLM-as-a-Judge
│   │       └── human_feedback.py # Human feedback processing
│   ├── utils/                    # Shared utilities
│   │   ├── __init__.py
│   │   ├── text_processing.py    # Text processing utilities
│   │   ├── metadata_extraction.py # Metadata extraction
│   │   ├── citation_utils.py     # Citation processing
│   │   ├── file_utils.py         # File handling utilities
│   │   └── validation.py        # Data validation utilities
│   ├── config/                   # Configuration management
│   │   ├── __init__.py
│   │   ├── settings.py           # Shared settings
│   │   ├── constants.py          # Application constants
│   │   └── database.py           # Database configuration
│   └── exceptions/               # Custom exceptions
│       ├── __init__.py
│       ├── base.py               # Base exception classes
│       ├── parsing.py            # Parsing exceptions
│       ├── rag.py                # RAG exceptions
│       └── llm.py                # LLM exceptions
├── tests/                        # Comprehensive test suite
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── fixtures/                 # Test fixtures
├── docs/                         # Library documentation
│   ├── api.md                    # API documentation
│   └── examples/                 # Usage examples
├── pyproject.toml               # Poetry configuration
├── README.md                    # Library documentation
└── CHANGELOG.md                 # Version history
```

### Enhanced Backend (`rag-memo-api`)

```
rag-memo-api/
├── main.py                      # FastAPI application entry point
├── dependencies.py              # Dependency injection with core lib
├── routes/                      # API route handlers
│   ├── __init__.py
│   ├── documents.py            # ENHANCED: Multi-format upload
│   ├── memos.py               # ENHANCED: Advanced generation
│   ├── evaluation.py          # NEW: Evaluation endpoints
│   ├── projects.py            # Project management
│   └── auth.py                # Authentication routes
├── services/                   # Application-specific services
│   ├── __init__.py
│   ├── rag_orchestrator.py    # NEW: RAG framework orchestration
│   ├── document_processor.py  # ENHANCED: Multi-format processing
│   ├── query_transformer.py   # NEW: Query transformation service
│   ├── evaluation_service.py  # NEW: Quality evaluation service
│   └── notification_service.py # NEW: User notifications
├── workers/                    # Dramatiq task definitions
│   ├── __init__.py
│   ├── document_tasks.py      # Document processing tasks
│   ├── generation_tasks.py    # Memo generation tasks
│   └── evaluation_tasks.py    # Evaluation tasks
├── middleware/                 # Custom middleware
│   ├── __init__.py
│   ├── auth.py                # Authentication middleware
│   ├── logging.py             # Request logging
│   └── error_handling.py      # Error handling middleware
├── tests/                      # Test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── e2e/                   # End-to-end tests
├── docker/                     # Docker configuration
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-compose.prod.yml
├── scripts/                    # Utility scripts
│   ├── migrate.py             # Database migration
│   └── seed.py                # Data seeding
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
└── README.md                  # Project documentation
```

### Enhanced Frontend (`rag-memo-ui`)

```
rag-memo-ui/
├── src/
│   ├── components/             # React components
│   │   ├── DocumentUpload/     # ENHANCED: Multi-format support
│   │   │   ├── DocumentUpload.tsx
│   │   │   ├── FilePreview.tsx
│   │   │   └── UploadProgress.tsx
│   │   ├── MemoViewer/         # ENHANCED: Advanced viewing
│   │   │   ├── MemoViewer.tsx
│   │   │   ├── CitationPanel.tsx
│   │   │   └── QualityMetrics.tsx
│   │   ├── RAGSettings/        # NEW: RAG configuration
│   │   │   ├── FrameworkSelector.tsx
│   │   │   ├── ModelSelector.tsx
│   │   │   └── AdvancedSettings.tsx
│   │   ├── Evaluation/         # NEW: Quality evaluation
│   │   │   ├── FeedbackForm.tsx
│   │   │   ├── QualityDashboard.tsx
│   │   │   └── MetricsChart.tsx
│   │   └── ui/                 # Reusable UI components
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       ├── Modal.tsx
│   │       └── LoadingSpinner.tsx
│   ├── services/               # API client services
│   │   ├── api.ts             # ENHANCED: New endpoints
│   │   ├── documentService.ts  # Document operations
│   │   ├── memoService.ts     # Memo operations
│   │   └── evaluationService.ts # Evaluation operations
│   ├── store/                  # Zustand state management
│   │   ├── useDocumentStore.ts # Document state
│   │   ├── useMemoStore.ts    # Memo state
│   │   ├── useSettingsStore.ts # Settings state
│   │   └── useEvaluationStore.ts # Evaluation state
│   ├── hooks/                  # Custom React hooks
│   │   ├── useFileUpload.ts   # File upload hook
│   │   ├── useMemoGeneration.ts # Memo generation hook
│   │   └── useWebSocket.ts    # Real-time updates
│   ├── types/                  # TypeScript definitions
│   │   ├── api.ts             # API types
│   │   ├── document.ts        # Document types
│   │   ├── memo.ts            # Memo types
│   │   └── evaluation.ts      # Evaluation types
│   ├── utils/                  # Helper functions
│   │   ├── fileUtils.ts       # File handling
│   │   ├── formatUtils.ts     # Data formatting
│   │   └── validationUtils.ts # Form validation
│   └── styles/                 # Styling
│       ├── globals.css        # Global styles
│       └── components.css     # Component styles
├── public/                     # Static assets
├── tests/                      # Frontend tests
│   ├── components/            # Component tests
│   ├── services/              # Service tests
│   └── utils/                 # Utility tests
├── docs/                       # Frontend documentation
├── package.json               # Node.js dependencies
├── tsconfig.json              # TypeScript configuration
├── tailwind.config.js         # Tailwind configuration
├── vite.config.ts             # Vite configuration
└── README.md                  # Frontend documentation
```

## Development Environment

### Local Setup (Enhanced)
```
tiny-RAG/
├── docker-compose.yml          # Local development environment
├── docker-compose.prod.yml     # Production environment
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── Makefile                   # Development commands
├── scripts/                   # Setup and utility scripts
│   ├── setup.sh              # Initial setup script
│   ├── test.sh               # Run all tests
│   └── deploy.sh             # Deployment script
└── README.md                 # Project setup instructions
```

## Configuration Management

### Core Library Settings (`rag-memo-core-lib/src/config/settings.py`)
```python
from pydantic_settings import BaseSettings
from typing import Literal, List

class CoreSettings(BaseSettings):
    # Database settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "tinyrag"
    REDIS_URL: str = "redis://localhost:6379"
    
    # LLM settings
    OPENAI_API_KEY: str
    GEMINI_API_KEY: str
    OPENAI_BASE_URL: str = "https://api.openai-proxy.org/v1"
    GEMINI_BASE_URL: str = "https://api.openai-proxy.org/google"
    
    # RAG framework settings
    RAG_FRAMEWORK: Literal["llamaindex", "langchain"] = "llamaindex"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    VECTOR_STORE: str = "mongodb_atlas"
    
    # Document processing settings
    MAX_CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    SUPPORTED_FORMATS: List[str] = ["pdf", "docx", "png", "jpg", "tiff"]
    
    # OCR settings
    OCR_ENGINE: str = "tesseract"
    
    class Config:
        env_file = ".env"
```

### Backend Configuration (`rag-memo-api/config.py`)
```python
from rag_memo_core_lib.config.settings import CoreSettings

class APISettings(CoreSettings):
    # API specific settings
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TinyRAG"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # JWT settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Worker settings
    DRAMATIQ_BROKER: str = "redis"
    WORKER_CONCURRENCY: int = 4
```

## Testing Strategy

### Core Library Testing
```
rag-memo-core-lib/tests/
├── unit/
│   ├── test_models.py         # Model validation tests
│   ├── test_rag_services.py   # RAG service tests
│   ├── test_parsers.py        # Parser tests
│   └── test_utils.py          # Utility tests
├── integration/
│   ├── test_rag_integration.py # RAG framework integration
│   └── test_database.py       # Database integration
└── fixtures/
    ├── sample_documents/       # Test documents
    └── mock_responses/         # Mock API responses
```

### Backend Testing
```
rag-memo-api/tests/
├── unit/
│   ├── test_routes.py         # API endpoint tests
│   ├── test_services.py       # Service layer tests
│   └── test_workers.py        # Worker task tests
├── integration/
│   ├── test_api_integration.py # Full API integration
│   └── test_worker_integration.py # Worker integration
└── e2e/
    └── test_user_flows.py     # End-to-end user flows
```

### Frontend Testing
```
rag-memo-ui/tests/
├── components/
│   ├── DocumentUpload.test.tsx
│   ├── MemoViewer.test.tsx
│   └── RAGSettings.test.tsx
├── services/
│   └── api.test.ts
└── utils/
    └── fileUtils.test.ts
```

## Deployment Architecture

### Development Environment
- **Local Development**: Docker Compose with hot reload
- **Testing**: Automated testing pipeline with GitHub Actions
- **Code Quality**: Ruff for linting, pytest for testing

### Production Environment
- **Backend**: Containerized FastAPI with Gunicorn/Uvicorn
- **Frontend**: Static build deployed to CDN (Vercel/Netlify)
- **Database**: MongoDB Atlas with Vector Search
- **Cache**: Redis Cloud
- **Monitoring**: Application logs and performance metrics

## Migration Path (v1.1 → v1.2)

### Phase 1: Core Library Setup
1. Initialize `rag-memo-core-lib` with Poetry
2. Migrate shared models from backend
3. Create abstract service interfaces
4. Set up testing framework

### Phase 2: Service Migration
1. Move LLM factory to core library
2. Implement RAG service abstractions
3. Create parser factory system
4. Update backend to use core library

### Phase 3: Feature Enhancement
1. Add LangChain/LlamaIndex integration
2. Implement multi-format document processing
3. Add evaluation services
4. Enhance frontend for new features

### Phase 4: Testing & Deployment
1. Comprehensive testing across all layers
2. Performance optimization
3. Documentation updates
4. Production deployment

## Conclusion

The integrated project structure provides a solid foundation for enterprise-grade RAG capabilities while maintaining modularity and reusability. The core library abstraction ensures consistent data models and business logic across the platform, while the enhanced backend and frontend provide advanced features for document processing and memo generation.

This architecture supports the evolution from a simple PDF-to-memo tool to a comprehensive document analysis platform suitable for enterprise deployment. 