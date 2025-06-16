# TinyRAG Service Startup Guide

**Rules for AI loaded successfully!** This guide follows the development standards defined in `.cursorrules` and provides step-by-step instructions for starting all TinyRAG services.

## Prerequisites

### System Requirements
- **Operating System**: macOS, Linux, or Windows with WSL2
- **Node.js**: Version 18.0 or higher
- **Python**: Version 3.11 or higher
- **Docker**: Version 20.10 or higher (recommended)
- **Docker Compose**: Version 2.0 or higher

### Required Tools
```bash
# Install Node.js (using nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# Install Python (using pyenv)
curl https://pyenv.run | bash
pyenv install 3.11.0
pyenv global 3.11.0

# Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop/
```

## Quick Start (Recommended)

### Option 1: Docker Compose (Easiest)

1. **Clone and Setup**
   ```bash
   cd /Users/haoyanghan/Documents/GitHub/tiny-RAG
   
   # Copy environment files
   cp env.example .env
   cp rag-memo-api/env.example rag-memo-api/.env
   cp rag-memo-ui/env.example rag-memo-ui/.env
   ```

2. **Start All Services**
   ```bash
   # Start all services with Docker Compose
   docker-compose up -d
   
   # Check service status
   docker-compose ps
   
   # View logs
   docker-compose logs -f
   ```

3. **Access Applications**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **MongoDB**: localhost:27017
   - **Redis**: localhost:6379

### Option 2: Manual Setup (Development)

## Database Services

### 1. MongoDB Setup

#### Option A: Docker (Recommended)
```bash
# Start MongoDB with Docker
docker run -d \
  --name tinyrag-mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  -e MONGO_INITDB_DATABASE=tinyrag \
  -v tinyrag_mongodb_data:/data/db \
  mongo:7.0

# Verify MongoDB is running
docker logs tinyrag-mongodb
```

#### Option B: Local Installation (macOS)
```bash
# Install MongoDB using Homebrew
brew tap mongodb/brew
brew install mongodb-community@7.0

# Start MongoDB service
brew services start mongodb/brew/mongodb-community@7.0

# Create database and user
mongosh
> use tinyrag
> db.createUser({
    user: "tinyrag_user",
    pwd: "tinyrag_password",
    roles: ["readWrite"]
  })
```

#### Option C: MongoDB Atlas (Cloud)
1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a free cluster
3. Create a database user
4. Get connection string
5. Update `MONGODB_URL` in `.env` files

### 2. Redis Setup

#### Option A: Docker (Recommended)
```bash
# Start Redis with Docker
docker run -d \
  --name tinyrag-redis \
  -p 6379:6379 \
  redis:7.2-alpine

# Verify Redis is running
docker exec -it tinyrag-redis redis-cli ping
```

#### Option B: Local Installation (macOS)
```bash
# Install Redis using Homebrew
brew install redis

# Start Redis service
brew services start redis

# Test Redis connection
redis-cli ping
```

### 3. Vector Database (MongoDB Atlas Vector Search)

#### Setup Vector Search Index
```javascript
// Connect to MongoDB and create vector search index
// This can be done via MongoDB Compass or Atlas UI

// Example index configuration for document embeddings
{
  "name": "document_embeddings_index",
  "type": "vectorSearch",
  "definition": {
    "fields": [
      {
        "type": "vector",
        "path": "embedding",
        "numDimensions": 1536,
        "similarity": "cosine"
      },
      {
        "type": "filter",
        "path": "document_id"
      }
    ]
  }
}
```

## Application Services

### 1. Backend API (rag-memo-api)

```bash
# Navigate to backend directory
cd rag-memo-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your actual values

# Run database migrations (if any)
python -m alembic upgrade head

# Start the API server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# In a separate terminal, start the worker
cd rag-memo-api
source venv/bin/activate
dramatiq workers.tasks
```

### 2. Frontend UI (rag-memo-ui)

```bash
# Navigate to frontend directory
cd rag-memo-ui

# Install dependencies
npm install

# Set up environment variables
cp env.example .env.local
# Edit .env.local with your actual values

# Start the development server
npm run dev

# Build for production (optional)
npm run build
npm run preview
```

### 3. Core Library (rag-memo-core-lib)

```bash
# Navigate to core library directory
cd rag-memo-core-lib

# Install dependencies with Poetry
poetry install

# Run tests
poetry run pytest

# Build the package
poetry build
```

## Environment Configuration

### Backend API (.env)
```env
# Database Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=tinyrag
REDIS_URL=redis://localhost:6379

# LLM API Keys
OPENAI_API_KEY=sk-28B9sTozC3sX2aQWfZ7F4teA9xerCGusWMJTuZrmRtU7ku2a
GEMINI_API_KEY=sk-28B9sTozC3sX2aQWfZ7F4teA9xerCGusWMJTuZrmRtU7ku2a

# Application Settings
DEBUG=true
API_V1_STR=/api/v1
PROJECT_NAME=TinyRAG
```

### Frontend UI (.env.local)
```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_API_VERSION=v1

# Application Settings
VITE_APP_NAME=TinyRAG
VITE_APP_VERSION=1.2.0
VITE_ENABLE_DEBUG=true
```

## Service Health Checks

### 1. Database Health Check
```bash
# MongoDB
mongosh --eval "db.adminCommand('ping')"

# Redis
redis-cli ping
```

### 2. API Health Check
```bash
# Backend API
curl http://localhost:8000/health

# Check API documentation
open http://localhost:8000/docs
```

### 3. Frontend Health Check
```bash
# Frontend
curl http://localhost:3000

# Open in browser
open http://localhost:3000
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port
lsof -i :8000  # For backend
lsof -i :3000  # For frontend
lsof -i :27017 # For MongoDB
lsof -i :6379  # For Redis

# Kill process
kill -9 <PID>
```

#### 2. Database Connection Issues
```bash
# Check MongoDB status
docker ps | grep mongo
docker logs tinyrag-mongodb

# Check Redis status
docker ps | grep redis
docker logs tinyrag-redis

# Test connections
mongosh mongodb://localhost:27017/tinyrag
redis-cli -h localhost -p 6379 ping
```

#### 3. API Key Issues
```bash
# Verify API keys are set
echo $OPENAI_API_KEY
echo $GEMINI_API_KEY

# Test API key validity
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai-proxy.org/v1/models
```

#### 4. Frontend Build Issues
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf .vite
npm run dev
```

### Log Locations

#### Docker Logs
```bash
# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api
docker-compose logs -f ui
docker-compose logs -f mongodb
docker-compose logs -f redis
```

#### Local Development Logs
```bash
# Backend logs
tail -f rag-memo-api/logs/app.log

# Frontend logs (in browser console)
# Open Developer Tools > Console

# Worker logs
tail -f rag-memo-api/logs/worker.log
```

## Performance Optimization

### 1. Database Optimization
```javascript
// Create indexes for better performance
db.documents.createIndex({ "filename": 1 })
db.documents.createIndex({ "created_at": -1 })
db.documents.createIndex({ "status": 1 })
db.generations.createIndex({ "document_id": 1 })
db.generations.createIndex({ "created_at": -1 })
```

### 2. Redis Configuration
```bash
# Optimize Redis for development
redis-cli CONFIG SET maxmemory 256mb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### 3. API Performance
```bash
# Use production ASGI server
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Production Deployment

### 1. Environment Setup
```bash
# Set production environment variables
export DEBUG=false
export MONGODB_URL="mongodb+srv://user:pass@cluster.mongodb.net/tinyrag"
export REDIS_URL="redis://production-redis:6379"
```

### 2. Docker Production Build
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Health Monitoring
```bash
# Set up health check endpoints
curl http://localhost:8000/health
curl http://localhost:8000/metrics
```

## Next Steps

1. **Verify All Services**: Ensure all services are running and healthy
2. **Test Upload**: Try uploading a PDF document
3. **Generate Memo**: Test the memo generation functionality
4. **Check Logs**: Monitor logs for any errors or warnings
5. **Performance Testing**: Run load tests if needed

## Support

For issues or questions:
1. Check the logs for error messages
2. Review the troubleshooting section
3. Consult the API documentation at http://localhost:8000/docs
4. Check the project documentation in the `Docs/` directory

---

**Service Status Dashboard**: Once all services are running, you can monitor them at:
- **API Health**: http://localhost:8000/health
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **MongoDB**: Use MongoDB Compass to connect to localhost:27017
- **Redis**: Use Redis CLI or Redis Desktop Manager 