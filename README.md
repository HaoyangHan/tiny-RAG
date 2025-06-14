# TinyRAG - Intelligent Memo Generation Platform

## Overview
TinyRAG is an intelligent AI-powered platform that automates the creation of first-draft memos from dense, complex documents. Using cutting-edge Retrieval-Augmented Generation (RAG), it ensures every statement is grounded in source documents with verifiable citations.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- MongoDB Atlas Account
- OpenAI API Key

### Local Development Setup
1. Clone the repositories:
```bash
git clone https://github.com/your-org/rag-memo-api.git
git clone https://github.com/your-org/rag-memo-ui.git
git clone https://github.com/your-org/rag-memo-core-lib.git
```

2. Set up the backend:
```bash
cd rag-memo-api
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

3. Set up the frontend:
```bash
cd rag-memo-ui
npm install
```

4. Configure environment variables:
```bash
# Copy example env files
cp .env.example .env  # in each repository
```

5. Start the development environment:
```bash
docker-compose up -d
```

## 🛠️ Features

### Core Features
- 📄 PDF Document Processing
- 🤖 AI-Powered Memo Generation
- 📝 Citation System
- 🔍 Source Verification
- 🎯 Customizable Prompts

### Technical Features
- ⚡ FastAPI Backend
- 🔄 Asynchronous Processing
- 🎨 Modern React/Vue.js Frontend
- 📊 MongoDB + Vector Search
- 🔒 Secure Authentication

## 📚 Documentation

- [API Documentation](docs/api/README.md)
- [Architecture Overview](docs/architecture/README.md)
- [Development Guide](docs/Contributing.md)
- [User Guide](docs/user/README.md)

## 🧪 Testing

```bash
# Backend Tests
cd rag-memo-api
pytest

# Frontend Tests
cd rag-memo-ui
npm test
```

## 📈 Performance Metrics

- Document Processing: < 30 seconds
- Memo Generation: < 60 seconds
- API Response: < 200ms
- System Uptime: > 99%

## 🔄 Development Workflow

1. Create feature branch
2. Implement changes
3. Run tests
4. Submit PR
5. Code review
6. Merge to main

## 🤝 Contributing

Please read our [Contributing Guide](docs/Contributing.md) for details on our code of conduct and the process for submitting pull requests.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Project Structure](docs/ProjectStructure.md)
- [Version Plan](docs/Todo/VersionPlanDoc.md)
- [Change Log](docs/ChangeLog.md)
- [FAQ](docs/FAQ.md)
- [Technical Debt](docs/TechDebt.md)