# TinyRAG v1.1 Project Structure

## Repository Organization

The project maintains the three main repositories with enhanced LLM capabilities:

### 1. `rag-memo-api` (Backend) - Enhanced v1.1
```
rag-memo-api/
├── main.py                  # ENHANCED: FastAPI application with LLM support
├── database.py              # Database connection management
├── dependencies.py          # UPDATED: Removed deprecated dependencies
├── requirements.txt         # UPDATED: Added LLM provider dependencies
├── Dockerfile              # Container configuration
├── README.md               # Backend documentation
├── 
├── models/                 # Data models (Beanie ODM)
│   ├── document.py         # Document and chunk models
│   └── memo.py            # Memo and section models
├── 
├── services/              # Business logic services
│   ├── llm_factory.py     # NEW: Unified LLM provider interface
│   ├── memo_generator.py  # ENHANCED: Multi-model memo generation
│   └── document_processor.py # Document parsing and embedding
├── 
├── routes/                # API route handlers
│   ├── documents.py       # Document upload and management
│   └── memos.py          # ENHANCED: Memo generation with model selection
├── 
├── workers/               # Background task processing
│   ├── actors.py         # Dramatiq task definitions
│   └── tasks.py          # Task implementations
├── 
├── tests/                # Test suite
│   ├── test_llm_factory.py    # NEW: LLM factory tests
│   ├── test_memo_generator.py # UPDATED: Multi-model tests
│   └── test_api.py            # API endpoint tests
└── 
└── docker/               # Docker configuration
    └── docker-compose.yml
```

### 2. `rag-memo-ui` (Frontend) - Maintained v1.0 Structure
```
rag-memo-ui/
├── src/
│   ├── components/       # React components
│   │   ├── ui/          # Reusable UI components
│   │   │   └── Button.tsx
│   │   ├── documents/   # Document management components
│   │   │   ├── DocumentUpload.tsx
│   │   │   └── DocumentList.tsx
│   │   └── memos/       # FUTURE: Memo management components
│   ├── 
│   ├── lib/             # Utility libraries
│   │   └── api/         # API client services
│   │       └── documentApi.ts
│   ├── 
│   ├── store/           # State management (Zustand)
│   │   ├── index.ts     # Main store configuration
│   │   └── documentStore.ts # Document state management
│   ├── 
│   ├── types/           # TypeScript definitions
│   │   └── index.ts     # Shared type definitions
│   ├── 
│   ├── config/          # Configuration
│   │   └── index.ts     # API endpoints and settings
│   └── 
│   └── pages/           # Page components
│       └── documents/
│           └── index.tsx
├── 
├── public/              # Static assets
├── tests/              # Frontend tests
├── package.json        # Node.js dependencies
├── tailwind.config.js  # Tailwind CSS configuration
├── tsconfig.json       # TypeScript configuration
└── README.md          # Frontend documentation
```

### 3. `rag-memo-core-lib` (Shared Library) - Future Enhancement
```
rag-memo-core-lib/
├── src/
│   ├── models/          # Shared data models
│   │   ├── document.py  # Document model definitions
│   │   ├── memo.py     # Memo model definitions
│   │   └── llm.py      # NEW: LLM model definitions
│   ├── 
│   ├── utils/          # Shared utilities
│   │   ├── text_processing.py
│   │   └── validation.py
│   └── 
│   └── constants/      # NEW: Shared constants
│       ├── models.py   # LLM model constants
│       └── prompts.py  # Standard prompt templates
├── 
├── tests/             # Library tests
├── setup.py          # Package configuration
└── README.md         # Library documentation
```

## Enhanced Backend Architecture (v1.1)

### LLM Factory System

#### Core Components
```python
# services/llm_factory.py
class LLMFactory:
    """Unified interface for all LLM providers"""
    - create_llm(model: str) -> BaseLLM
    - generate_response(messages, model, temperature, max_tokens) -> LLMResponse
    - get_available_models() -> Dict[str, List[str]]
    - get_default_model(provider) -> str

class BaseLLM(ABC):
    """Abstract base class for LLM implementations"""
    - generate(messages, temperature, max_tokens) -> LLMResponse

class OpenAILLM(BaseLLM):
    """OpenAI provider implementation"""
    - Endpoint: https://api.openai-proxy.org/v1
    - Models: gpt-4-mini-2025-04-16, gpt-4.1-nano-2025-04-14

class GeminiLLM(BaseLLM):
    """Google Gemini provider implementation"""
    - Endpoint: https://api.openai-proxy.org/google
    - Models: gemini-2.0-flash-lite, gemini-2.5-pro-preview-06-05, gemini-2.5-flash-preview-05-20
```

#### Data Models
```python
# Enhanced message and response models
class LLMMessage(BaseModel):
    role: str  # "system", "user", "assistant"
    content: str

class LLMResponse(BaseModel):
    content: str
    model: str
    provider: str
    usage: Optional[Dict[str, Any]] = None
```

### Enhanced Services

#### Memo Generator v1.1
```python
# services/memo_generator.py
class MemoGenerator:
    def __init__(self, model: Optional[str] = None):
        self.model = model  # Default model selection
        
    async def generate_memo(
        self, title, documents, user_id, 
        sections=None, model=None
    ) -> Memo:
        # Enhanced with model selection
        
    async def _generate_section(
        self, section_title, documents, model=None
    ) -> MemoSection:
        # Uses LLM factory for generation
```

### API Enhancements

#### New Endpoints
```python
# routes/memos.py
@router.get("/models")
async def get_available_models():
    """Get list of available LLM models with descriptions"""

@router.post("/", response_model=Memo)
async def create_memo(memo_data: MemoCreate):
    """Enhanced memo creation with model selection"""
    # memo_data.model: Optional[str] = None
```

## Configuration Management

### Environment Variables (v1.1)
```env
# Database Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=tinyrag
REDIS_URL=redis://localhost:6379

# LLM API Configuration
OPENAI_API_KEY=sk-xxxxxxxx
GEMINI_API_KEY=sk-xxxxxxxx

# Security Configuration
JWT_SECRET_KEY=your-jwt-secret-key

# Application Configuration
DEBUG=False
API_V1_STR=/api/v1
PROJECT_NAME=TinyRAG
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

### Dependencies (v1.1)
```txt
# Core Framework
fastapi==0.109.2
uvicorn==0.27.1
pydantic==2.6.1
pydantic-settings==2.1.0

# LLM Providers (NEW)
openai==1.12.0
google-generativeai==0.3.2

# Database & Caching
motor==3.3.2
beanie==1.25.0
redis==5.0.1

# Background Processing
dramatiq==1.16.0

# Document Processing
pypdf==4.0.1
python-magic==0.4.27
pillow==10.2.0

# Vector Operations
pymongo==4.6.1
faiss-cpu==1.7.4

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9

# Development & Testing
pytest==8.0.1
pytest-asyncio==0.23.5
httpx==0.26.0
pytest-cov==4.1.0
ruff==0.2.1
black==24.1.1
mypy==1.8.0
```

## Development Workflow (v1.1)

### Local Development Setup
```bash
# 1. Clone repositories
git clone <repo-url> tiny-RAG
cd tiny-RAG

# 2. Backend setup
cd rag-memo-api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Environment configuration
cp .env.example .env
# Edit .env with your API keys

# 4. Frontend setup
cd ../rag-memo-ui
npm install

# 5. Start services
docker-compose up -d  # MongoDB, Redis
cd rag-memo-api && uvicorn main:app --reload
cd rag-memo-ui && npm run dev
```

### Testing Strategy (v1.1)

#### Backend Testing
```bash
# Unit tests
pytest tests/test_llm_factory.py -v
pytest tests/test_memo_generator.py -v

# Integration tests
pytest tests/test_api.py -v

# Coverage report
pytest --cov=services --cov-report=html
```

#### LLM Testing
```python
# Test LLM factory functionality
async def test_llm_factory():
    factory = LLMFactory()
    
    # Test model creation
    llm = factory.create_llm("gemini-2.0-flash-lite")
    assert isinstance(llm, GeminiLLM)
    
    # Test response generation
    messages = [LLMMessage(role="user", content="Hello")]
    response = await factory.generate_response(messages)
    assert response.content
    assert response.model == "gemini-2.0-flash-lite"
```

## Deployment Architecture

### Docker Configuration (v1.1)
```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: ./rag-memo-api
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - MONGODB_URL=mongodb://mongodb:27017
      - REDIS_URL=redis://redis:6379
    depends_on:
      - mongodb
      - redis

  mongodb:
    image: mongo:6.0
    volumes:
      - mongodb_data:/data/db

  redis:
    image: redis:7.0
    volumes:
      - redis_data:/data
```

### Production Deployment
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# Health checks
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/memos/models
```

## Monitoring and Observability

### Logging Configuration
```python
# Enhanced logging for LLM operations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# LLM-specific logging
llm_logger = logging.getLogger("llm_factory")
llm_logger.info(f"Using model: {model}, Provider: {provider}")
```

### Performance Metrics
- **LLM Response Time**: Track generation latency by model
- **Token Usage**: Monitor costs across providers
- **Error Rates**: Track failures by provider and model
- **Model Selection**: Analyze usage patterns

## Security Considerations

### API Key Management
- Environment variable storage
- Rotation procedures
- Access logging
- Rate limiting per provider

### Data Protection
- Document encryption at rest
- Secure memo storage
- User data isolation
- Audit logging

## Future Enhancements (v1.2+)

### Planned Architecture Updates
```
# Additional services
├── services/
│   ├── model_router.py      # Intelligent model routing
│   ├── cost_optimizer.py    # Cost optimization engine
│   ├── quality_assessor.py  # Output quality evaluation
│   └── cache_manager.py     # Response caching system

# Enhanced monitoring
├── monitoring/
│   ├── metrics.py          # Custom metrics collection
│   ├── alerts.py           # Alert management
│   └── dashboards.py       # Performance dashboards
```

### Scalability Improvements
- **Horizontal Scaling**: Multi-instance deployment
- **Load Balancing**: Request distribution across models
- **Caching Layer**: Redis-based response caching
- **Queue Management**: Priority-based task processing

## Documentation Structure

```
docs/
├── api/                    # API documentation
│   ├── endpoints.md        # UPDATED: New LLM endpoints
│   └── models.md          # UPDATED: LLM model specifications
├── 
├── architecture/          # System design documentation
│   ├── llm-factory.md     # NEW: LLM factory architecture
│   └── data-flow.md       # UPDATED: Enhanced data flow
├── 
├── deployment/            # Deployment guides
│   ├── production.md      # UPDATED: LLM environment setup
│   └── monitoring.md      # NEW: LLM monitoring guide
├── 
├── user/                  # User guides
│   ├── LLM-Setup-Guide.md # NEW: LLM setup and usage
│   └── api-usage.md       # UPDATED: Model selection examples
└── 
└── development/           # Development guides
    ├── contributing.md    # Contribution guidelines
    └── testing.md         # UPDATED: LLM testing procedures
```

This enhanced project structure for v1.1 provides a robust foundation for multi-LLM support while maintaining clean separation of concerns and scalability for future enhancements. 