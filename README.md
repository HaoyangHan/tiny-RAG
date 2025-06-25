# TinyRAG v1.4.0 ✅ PRODUCTION READY

**Advanced RAG Platform with Project-Based Architecture & Core Library Foundation**

**Current Status**: v1.4.0 Production Ready ✅ COMPLETED (June 25, 2025)  
**Achievement**: 100% API Success Rate with Comprehensive Feature Set

TinyRAG v1.4.0 delivers a complete, production-ready RAG platform with advanced project-based organization, extensible core library architecture, and comprehensive API coverage for modern AI workflows including RAG, agentic systems, and MCP integration.

## ✅ v1.4.0 Production Achievements (COMPLETED)

### 🏗️ **Advanced Project-Based Architecture**
- **Multi-Tenant Organization**: Personal, Team, Enterprise, Research project types
- **Role-Based Access Control**: Owner, Collaborator, Viewer permissions
- **Project Collaboration**: Real-time sharing and team workspace management
- **Hierarchical Resource Management**: Projects → Elements → Generations → Evaluations

### 🤖 **Versatile AI Workflow Support**
- **Raw LLM Access**: Direct language model interactions with full configuration
- **RAG Pipeline**: Document-based question answering with semantic search
- **Agentic Workflows**: Multi-step autonomous AI task execution
- **MCP Integration**: Model Context Protocol for standardized tool usage

### ⚡ **Advanced Element & Template System**
- **Reusable Prompt Templates**: Variable substitution and version control
- **MCP Configuration Elements**: Standardized AI tool and agent definitions
- **Execution Engine**: Automated element processing with tracking
- **Cross-Project Sharing**: Template library and element marketplace

### 📈 **Comprehensive Evaluation Framework**
- **LLM-as-a-Judge**: Automated quality assessment using language models
- **Multi-Criteria Scoring**: Accuracy, relevance, clarity, completeness metrics
- **Hallucination Detection**: Advanced content verification systems
- **Performance Analytics**: Cost tracking, usage metrics, optimization insights

### 🔧 **Extensible Core Library**
- **Abstract Provider System**: Pluggable LLM and vector store backends
- **Type-Safe Interfaces**: Comprehensive abstractions for all AI components
- **Factory Pattern Implementation**: Dynamic provider registration and configuration
- **Mock Providers**: Zero-dependency testing with configurable behavior

### 📊 **Production-Ready API (100% Success Rate)**
- **49/49 Core Tests Passing**: Complete API coverage with full functionality
- **JWT Authentication**: Secure token-based user management
- **Comprehensive Documentation**: Interactive API docs with examples
- **Error Handling**: Structured exception hierarchy with detailed context

### 🐳 **Enhanced Infrastructure**
- **Complete Docker Stack**: Containerized services with health monitoring
- **Service Integration**: MongoDB, Redis, Qdrant with optimized configurations
- **Auto-scaling Workers**: Background processing with queue management
- **Production Monitoring**: Real-time metrics and performance tracking

## 🏗️ Architecture

```mermaid
graph TB
    UI[React Frontend<br/>v1.4 Project UI<br/>Port 3000] --> API[FastAPI v1.4 API<br/>Project-Based<br/>Port 8000]
    API --> Auth[JWT Authentication<br/>RBAC System]
    API --> CoreLib[Core Library<br/>Abstraction Layer]
    
    CoreLib --> LLMFactory[LLM Factory<br/>Provider System]
    CoreLib --> VectorFactory[Vector Store<br/>Factory]
    CoreLib --> Worker[Element Execution<br/>Engine]
    
    API --> Mongo[(MongoDB<br/>Projects & Elements)]
    API --> Redis[(Redis<br/>Sessions & Cache)]
    API --> Qdrant[(Qdrant<br/>Vector Embeddings)]
    
    LLMFactory --> OpenAI[OpenAI Provider<br/>GPT-4o-mini]
    LLMFactory --> Anthropic[Anthropic Provider<br/>Claude]
    LLMFactory --> Mock[Mock Provider<br/>Testing]
    
    subgraph "v1.4 Project Architecture"
        Project[Project] --> Elements[Elements<br/>Templates & Tools]
        Elements --> Generations[Generations<br/>Executions]
        Generations --> Evaluations[Evaluations<br/>Quality Scores]
    end
    
    subgraph "Extensible Workflows"
        RAG[RAG Pipeline<br/>Doc Q&A]
        Agentic[Agentic Tasks<br/>Multi-step AI]
        MCP[MCP Integration<br/>Tool Protocol]
        Raw[Raw LLM<br/>Direct Access]
    end
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenAI API key (required for LLM features)
- 8GB+ RAM recommended

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/tiny-RAG.git
cd tiny-RAG

# Copy environment template
cp env.example .env

# Edit .env with your configuration
# REQUIRED: Set OPENAI_API_KEY and JWT_SECRET_KEY
nano .env
```

### 2. One-Command Startup

```bash
# Start all services
./scripts/start-tinyrag.sh

# Or with options
./scripts/start-tinyrag.sh --rebuild  # Rebuild images
./scripts/start-tinyrag.sh --logs     # Show logs after start
```

### 3. Access the Application

- **Frontend UI**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

### 4. Default Admin Login

```
Email: admin@tinyrag.local
Username: admin
Password: TinyRAG2024!
```

⚠️ **Change the default password immediately!**

## 📋 Core Features

### 🔐 Authentication System

- **User Registration & Login**: Secure JWT-based authentication
- **Role-Based Access**: Admin, User, and Viewer roles
- **API Key Management**: Generate and manage API keys for programmatic access
- **Rate Limiting**: Configurable rate limits for security
- **Session Management**: Secure session handling with Redis

### 🧠 Intelligent Metadata Extraction

- **LLM-Powered Analysis**: Uses GPT-4o-mini for comprehensive metadata extraction
- **Multi-Type Extraction**: Keywords, entities, dates, topics, sentiment, summaries
- **Quality Assessment**: Content readability and information density scoring
- **Confidence Scoring**: All extractions include confidence levels
- **Caching**: Intelligent caching to reduce LLM API costs

### 🎯 Advanced Retrieval & Reranking

- **Semantic Search**: Vector-based similarity matching
- **Metadata Filtering**: Filter by dates, entities, topics, quality scores
- **Intelligent Reranking**: Multi-factor scoring algorithm
- **Diversity Filtering**: Ensures diverse, non-redundant results
- **Explanation System**: Detailed scoring explanations for transparency

### 📄 Document Processing

- **Multi-Format Support**: PDF, DOCX, TXT, MD files
- **Intelligent Chunking**: Context-aware document segmentation
- **Metadata Preservation**: Maintains document structure and metadata
- **Batch Processing**: Efficient handling of multiple documents
- **Progress Tracking**: Real-time processing status updates

## 🛠️ Development Setup

### Local Development

```bash
# Install dependencies
pip install -r rag-memo-api/requirements.txt
pip install -r rag-memo-core-lib/requirements.txt

# Start infrastructure only
docker-compose up -d tinyrag-mongodb tinyrag-redis tinyrag-qdrant

# Run API locally
cd rag-memo-api
uvicorn main:app --reload --port 8000

# Run UI locally
cd rag-memo-ui
npm install
npm run dev
```

### Testing

```bash
# Run API tests
cd rag-memo-api
pytest tests/ -v

# Run UI tests
cd rag-memo-ui
npm test

# Run integration tests
./scripts/run-tests.sh
```

## 📚 API Usage Examples

### v1.4 API Authentication

```bash
# Register a new user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "newuser",
    "password": "SecurePass123!",
    "full_name": "John Doe"
  }'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "user@example.com",
    "password": "SecurePass123!"
  }'
```

### Project-Based Workflow

```bash
# Create a project
curl -X POST "http://localhost:8000/api/v1/projects" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Customer Analysis",
    "description": "RAG system for customer data analysis",
    "tenant_type": "TEAM"
  }'

# Upload document to project
curl -X POST "http://localhost:8000/api/v1/documents/upload?project_id=PROJECT_ID" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@document.pdf"
```

### Element & Generation System

```bash
# Create prompt template element
curl -X POST "http://localhost:8000/api/v1/elements" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Document Analyzer",
    "project_id": "PROJECT_ID",
    "element_type": "PROMPT_TEMPLATE",
    "template_content": "Analyze this document: {content}",
    "variables": ["content"]
  }'

# Execute element
curl -X POST "http://localhost:8000/api/v1/elements/ELEMENT_ID/execute" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "variables": {
      "content": "Document content to analyze..."
    }
  }'
```

### Evaluation System

```bash
# Create evaluation for generation
curl -X POST "http://localhost:8000/api/v1/evaluations" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "generation_id": "GENERATION_ID",
    "evaluator_model": "gpt-4o",
    "custom_criteria": {
      "accuracy": 0.4,
      "relevance": 0.3,
      "clarity": 0.3
    }
  }'
```

## ⚙️ Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Authentication
JWT_SECRET_KEY=your-super-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM Configuration
OPENAI_API_KEY=sk-your-openai-key
LLM_MODEL=gpt-4o-mini

# Features
ENABLE_METADATA_EXTRACTION=true
ENABLE_ENHANCED_RERANKING=true

# Performance
WORKER_CONCURRENCY=4
RATE_LIMIT_ENABLED=true
```

### Advanced Configuration

See `Docs/TinyRAG-v1.4-API-Documentation.md` for complete API reference and `Docs/DevLog/2025-06-25_v1.4-core-lib-implementation-progress.md` for detailed architecture information.

## 🔧 Troubleshooting

### Common Issues

1. **Services won't start**
   ```bash
   # Check Docker status
   docker info
   
   # Check service logs
   docker-compose logs tinyrag-api
   ```

2. **Authentication errors**
   ```bash
   # Verify JWT secret is set
   echo $JWT_SECRET_KEY
   
   # Check API health
   curl http://localhost:8000/health
   ```

3. **LLM extraction fails**
   ```bash
   # Verify OpenAI API key
   echo $OPENAI_API_KEY
   
   # Check worker logs
   docker-compose logs tinyrag-worker
   ```

### Reset Everything

```bash
# Stop all services and remove data
docker-compose down -v

# Rebuild and restart
./scripts/start-tinyrag.sh --rebuild
```

## 📊 Monitoring & Logging

### Service Monitoring

```bash
# Check all service status
docker-compose ps

# View real-time logs
docker-compose logs -f

# Monitor specific service
docker-compose logs -f tinyrag-api
```

### Health Checks

- **API Health**: `GET /health`
- **Database Status**: Included in health endpoint
- **LLM Service Status**: Monitored automatically
- **Authentication Status**: JWT validation checks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the coding standards in `.cursorrules`
4. Add comprehensive tests
5. Commit with semantic messages (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Standards

- **Type Annotations**: All Python code must be fully typed
- **Documentation**: Google-style docstrings required
- **Testing**: 90%+ test coverage target
- **Security**: Follow OWASP guidelines
- **Performance**: Profile and optimize critical paths

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4o-mini API
- Anthropic for Claude API
- FastAPI for the excellent web framework
- Qdrant for vector database capabilities
- The open-source community for inspiration and tools

## 📞 Support

- **Documentation**: `/docs` when running locally
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Security**: security@tinyrag.local

---

**TinyRAG v1.4.0** - Complete RAG Platform for Modern AI Workflows! 🚀

📖 **Full API Documentation**: [TinyRAG v1.4 API Guide](Docs/TinyRAG-v1.4-API-Documentation.md)