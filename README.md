# TinyRAG - Document Processing & Memo Generation Platform

[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/your-username/tiny-RAG)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![Node.js](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org)

**TinyRAG** is a modern, enterprise-grade document processing and memo generation platform that leverages advanced RAG (Retrieval-Augmented Generation) techniques to transform documents into intelligent, actionable memos.

## 🚀 Features

### Version 1.2 Highlights
- **Multi-Format Support**: PDF, DOCX, and image processing with OCR
- **Advanced RAG Frameworks**: LlamaIndex (default) and LangChain integration
- **Multi-LLM Support**: OpenAI GPT-4, Google Gemini with unified interface
- **Enhanced UI**: Modern React interface with drag-and-drop upload
- **Real-time Processing**: Live progress tracking and status updates
- **Vector Search**: MongoDB Atlas Vector Search integration
- **Enterprise Architecture**: Modular design with core library abstraction

### Core Capabilities
- 📄 **Document Processing**: Intelligent parsing of PDFs, DOCX, and images
- 🤖 **AI-Powered Generation**: Context-aware memo creation with citations
- 🔍 **Vector Search**: Semantic document retrieval and similarity matching
- 📊 **Progress Tracking**: Real-time upload and processing status
- 🎨 **Modern UI**: Responsive design with dark mode support
- 🔒 **Enterprise Security**: JWT authentication and role-based access
- 📈 **Performance Monitoring**: Built-in metrics and health checks

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │   Backend API   │    │  Core Library   │
│   (React/Vite)  │◄──►│   (FastAPI)     │◄──►│   (Python)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │    │   Task Queue    │    │   Vector DB     │
│                 │    │   (Redis)       │    │   (MongoDB)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Docker & Docker Compose** (recommended)
- **Node.js 18+** and **Python 3.11+** (for local development)
- **MongoDB** and **Redis** (if not using Docker)

### Option 1: Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/tiny-RAG.git
   cd tiny-RAG
   ```

2. **Start all services**
   ```bash
   # Copy environment files (API keys already included)
   cp env.example .env
   cp rag-memo-api/env.example rag-memo-api/.env
   cp rag-memo-ui/env.example rag-memo-ui/.env
   
   # Start all services
   docker-compose up -d
   
   # Check status
   docker-compose ps
   ```

3. **Access the application**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **MongoDB Admin**: http://localhost:8081 (admin/admin)
   - **Redis Admin**: http://localhost:8082

### Option 2: Manual Setup

See the comprehensive [Service Startup Guide](Docs/Service-Startup-Guide.md) for detailed manual installation instructions.

## 📖 Documentation

- **[Service Startup Guide](Docs/Service-Startup-Guide.md)** - Complete setup instructions
- **[Version Plan](Docs/Todo/VersionPlanIntegrated.md)** - Development roadmap and features
- **[Project Structure](Docs/Todo/ProjectStructureIntegrated.md)** - Architecture overview
- **[Implementation Plan](Docs/Version1.2-Implementation-Plan.md)** - v1.2 development plan
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when running)

## 🛠️ Development

### Project Structure
```
tiny-RAG/
├── rag-memo-ui/              # Frontend React application
├── rag-memo-api/             # Backend FastAPI application
├── rag-memo-core-lib/        # Core Python library
├── Docs/                     # Documentation
├── scripts/                  # Setup and utility scripts
├── docker-compose.yml        # Docker orchestration
└── README.md                 # This file
```

### Environment Configuration

The project uses environment files for configuration:

- **Root `.env`**: Global configuration
- **`rag-memo-api/.env`**: Backend-specific settings
- **`rag-memo-ui/.env`**: Frontend-specific settings

**API Keys**: The provided API key `sk-28B9sTozC3sX2aQWfZ7F4teA9xerCGusWMJTuZrmRtU7ku2a` is pre-configured for both OpenAI and Gemini services.

### Local Development

1. **Backend Development**
   ```bash
   cd rag-memo-api
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **Frontend Development**
   ```bash
   cd rag-memo-ui
   npm install
   npm run dev
   ```

3. **Core Library Development**
   ```bash
   cd rag-memo-core-lib
   poetry install
   poetry run pytest
   ```

## 🔧 Configuration

### Supported File Formats
- **Documents**: PDF, DOCX, DOC
- **Images**: PNG, JPG, JPEG, TIFF (with OCR)
- **Maximum Size**: 50MB per file
- **Batch Upload**: Up to 10 files simultaneously

### RAG Framework Configuration
```env
# Choose your RAG framework
RAG_FRAMEWORK=llamaindex  # or 'langchain'

# Embedding model
EMBEDDING_MODEL=text-embedding-3-small

# Vector store
VECTOR_STORE=mongodb_atlas
```

### LLM Provider Configuration
```env
# OpenAI Configuration
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai-proxy.org/v1

# Google Gemini Configuration
GEMINI_API_KEY=your-api-key
GEMINI_BASE_URL=https://api.openai-proxy.org/google
```

## 📊 Monitoring & Health Checks

### Service Health Endpoints
- **API Health**: `GET /health`
- **Database Status**: `GET /health/db`
- **Redis Status**: `GET /health/redis`
- **System Metrics**: `GET /metrics`

### Admin Interfaces
- **MongoDB Express**: http://localhost:8081 (admin/admin)
- **Redis Commander**: http://localhost:8082
- **API Documentation**: http://localhost:8000/docs

## 🧪 Testing

### Run Tests
```bash
# Backend tests
cd rag-memo-api
pytest

# Frontend tests
cd rag-memo-ui
npm test

# Core library tests
cd rag-memo-core-lib
poetry run pytest
```

### Load Testing
```bash
# API load testing
cd rag-memo-api
locust -f tests/load_test.py --host=http://localhost:8000
```

## 🚀 Deployment

### Production Deployment
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables for Production
```env
DEBUG=false
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/tinyrag
REDIS_URL=redis://production-redis:6379
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Standards
- Follow the guidelines in [`.cursorrules`](.cursorrules)
- Use Python 3.11+ with type hints
- Follow Google docstring format
- Use Ruff for code formatting
- Write comprehensive tests

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Troubleshooting
1. Check the [Service Startup Guide](Docs/Service-Startup-Guide.md) troubleshooting section
2. Review service logs: `docker-compose logs -f`
3. Verify environment configuration
4. Check API documentation at http://localhost:8000/docs

### Common Issues
- **Port conflicts**: Use `lsof -i :PORT` to find conflicting processes
- **Database connection**: Verify MongoDB and Redis are running
- **API key issues**: Ensure keys are properly set in environment files
- **File upload errors**: Check file size limits and supported formats

### Getting Help
- 📖 Check the documentation in the `Docs/` directory
- 🐛 Report issues on GitHub
- 💬 Join our community discussions

## 🐳 Docker Setup & Deployment

### Prerequisites
- Docker Desktop 24.0.0 or later
- Docker Compose v2.24.0 or later
- At least 4GB of available RAM
- Available ports: 3000, 8000, 8081, 8082

### Quick Start with Docker
1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/tiny-RAG.git
   cd tiny-RAG
   ```

2. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Start the services:**
   ```bash
   # Start all services in development mode
   docker-compose up -d

   # Or start with production configuration
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Access the services:**
   - Frontend UI: http://localhost:3000
   - API Documentation: http://localhost:8000/docs
   - MongoDB Express: http://localhost:8081 (admin/admin)
   - Redis Commander: http://localhost:8082

### Service Health Checks
```bash
# Check all containers are running
docker-compose ps

# Check API health
curl http://localhost:8000/health

# Check MongoDB connection
curl http://localhost:8000/health/db

# Check Redis connection
curl http://localhost:8000/health/redis
```

### Container Management
```bash
# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f api

# Rebuild specific service
docker-compose build api

# Restart specific service
docker-compose restart api
```

### Development with Docker
- **Live reload** is enabled for both frontend and backend in development mode
- Frontend code changes will automatically trigger rebuilds
- Backend code changes will reload the API server
- Core library changes require rebuilding the API container

### Troubleshooting
1. **Container fails to start:**
   ```bash
   # Check container logs
   docker-compose logs [service_name]
   ```

2. **Port conflicts:**
   ```bash
   # Check if ports are in use
   lsof -i :3000,8000,8081,8082
   ```

3. **Memory issues:**
   ```bash
   # Check container resource usage
   docker stats
   ```

---

**Built with ❤️ using FastAPI, React, MongoDB, and modern AI technologies.**