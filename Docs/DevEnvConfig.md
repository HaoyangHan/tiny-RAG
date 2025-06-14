# Development Environment Configuration

## System Requirements

### Minimum Requirements
- CPU: 4 cores
- RAM: 8GB
- Storage: 20GB free space
- OS: Ubuntu 20.04+, macOS 10.15+, or Windows 10+

### Recommended Requirements
- CPU: 8 cores
- RAM: 16GB
- Storage: 50GB free space
- OS: Ubuntu 22.04+, macOS 12+, or Windows 11+

## Required Software

### 1. Python Environment
```bash
# Install Python 3.11+
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# macOS
brew install python@3.11

# Windows
# Download from python.org
```

### 2. Node.js Environment
```bash
# Install Node.js 18+
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs

# macOS
brew install node@18

# Windows
# Download from nodejs.org
```

### 3. Docker and Docker Compose
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose

# macOS
brew install docker docker-compose

# Windows
# Download Docker Desktop from docker.com
```

### 4. Git
```bash
# Ubuntu/Debian
sudo apt install git

# macOS
brew install git

# Windows
# Download from git-scm.com
```

## Project Setup

### 1. Clone Repositories
```bash
# Create project directory
mkdir tiny-RAG
cd tiny-RAG

# Clone repositories
git clone https://github.com/your-org/rag-memo-api.git
git clone https://github.com/your-org/rag-memo-ui.git
git clone https://github.com/your-org/rag-memo-core-lib.git
```

### 2. Backend Setup
```bash
cd rag-memo-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install
```

### 3. Frontend Setup
```bash
cd rag-memo-ui

# Install dependencies
npm install

# Install development dependencies
npm install --save-dev @types/node @types/react @types/react-dom
```

### 4. Environment Configuration

#### Backend (.env)
```bash
# Copy example env file
cp .env.example .env

# Required environment variables
MONGODB_URI=mongodb://localhost:27017/tinyrag
REDIS_URI=redis://localhost:6379/0
LLM_API_KEY=your_openai_api_key
VECTOR_DB_URI=mongodb://localhost:27017/tinyrag_vectors
```

#### Frontend (.env.local)
```bash
# Copy example env file
cp .env.local.example .env.local

# Required environment variables
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
```

### 5. Database Setup

#### MongoDB
```bash
# Start MongoDB (if using local instance)
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  mongo:latest
```

#### Redis
```bash
# Start Redis
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:latest
```

### 6. Development Tools Setup

#### VS Code Extensions
- Python
- Pylance
- Python Test Explorer
- ESLint
- Prettier
- Docker
- GitLens

#### VS Code Settings
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

## Running the Development Environment

### 1. Start Services
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### 2. Run Backend
```bash
cd rag-memo-api
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Start API server
uvicorn api.main:app --reload

# Start workers
dramatiq workers.actors
```

### 3. Run Frontend
```bash
cd rag-memo-ui

# Start development server
npm run dev
```

## Development Workflow

### 1. Code Quality Tools
```bash
# Backend
cd rag-memo-api
ruff check .  # Lint
ruff format .  # Format
pytest  # Run tests

# Frontend
cd rag-memo-ui
npm run lint  # Lint
npm run format  # Format
npm test  # Run tests
```

### 2. Database Management
```bash
# Connect to MongoDB
mongosh mongodb://localhost:27017/tinyrag

# Connect to Redis
redis-cli
```

### 3. Logging
```bash
# View API logs
docker-compose logs -f api

# View worker logs
docker-compose logs -f workers
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check port usage
   sudo lsof -i :8000  # API port
   sudo lsof -i :3000  # Frontend port
   ```

2. **Database Connection**
   ```bash
   # Test MongoDB connection
   mongosh mongodb://localhost:27017/tinyrag --eval "db.runCommand({ping: 1})"
   
   # Test Redis connection
   redis-cli ping
   ```

3. **Docker Issues**
   ```bash
   # Reset Docker
   docker-compose down -v
   docker system prune -f
   docker-compose up -d
   ```

### Getting Help

- Check the [FAQ](docs/FAQ.md)
- Review the [Troubleshooting Guide](docs/troubleshooting.md)
- Create an issue on GitHub
- Join our community chat 