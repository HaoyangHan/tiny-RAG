# TinyRAG Project Structure

## Repository Organization

The project is organized into three main repositories:

### 1. `rag-memo-api` (Backend)
```
rag-memo-api/
├── api/
│   ├── main.py              # FastAPI application entry point
│   ├── routes/              # API route handlers
│   │   ├── documents.py     # Document upload and management
│   │   ├── generation.py    # Memo generation endpoints
│   │   └── projects.py      # Project management
│   ├── models/              # Pydantic models
│   │   ├── document.py
│   │   ├── generation.py
│   │   └── project.py
│   └── services/           # Business logic
│       ├── parser.py       # Document parsing service
│       ├── rag.py         # RAG engine
│       └── evaluation.py   # Quality evaluation
├── workers/
│   ├── actors.py          # Dramatiq task definitions
│   └── tasks.py           # Task implementations
├── tests/                 # Test suite
├── docker/               # Docker configuration
├── requirements.txt      # Python dependencies
└── README.md            # Project documentation
```

### 2. `rag-memo-ui` (Frontend)
```
rag-memo-ui/
├── src/
│   ├── components/       # React/Vue components
│   │   ├── DocumentUpload/
│   │   ├── MemoViewer/
│   │   └── PromptEditor/
│   ├── services/        # API client services
│   ├── store/          # State management
│   ├── types/          # TypeScript definitions
│   └── utils/          # Helper functions
├── public/             # Static assets
├── tests/             # Frontend tests
├── package.json       # Node.js dependencies
└── README.md         # Frontend documentation
```

### 3. `rag-memo-core-lib` (Shared Library)
```
rag-memo-core-lib/
├── src/
│   ├── models/        # Shared data models
│   │   ├── document.py
│   │   ├── generation.py
│   │   └── project.py
│   └── utils/         # Shared utilities
├── tests/            # Library tests
├── setup.py         # Package configuration
└── README.md       # Library documentation
```

## Development Environment

### Local Setup
```
tiny-RAG/
├── docker-compose.yml    # Local development environment
├── .env.example         # Environment variables template
└── README.md           # Project setup instructions
```

## Key Configuration Files

### Backend Configuration
```python
# api/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URI: str
    REDIS_URI: str
    LLM_API_KEY: str
    VECTOR_DB_URI: str
```

### Frontend Configuration
```typescript
// src/config.ts
export const config = {
  API_BASE_URL: process.env.VITE_API_BASE_URL,
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  SUPPORTED_FORMATS: ['application/pdf']
};
```

## Development Workflow

1. **Local Development:**
   ```bash
   # Start all services
   docker-compose up -d
   
   # Run backend tests
   cd rag-memo-api
   pytest
   
   # Run frontend tests
   cd rag-memo-ui
   npm test
   ```

2. **Deployment:**
   - Backend: Deploy to cloud provider (e.g., AWS, GCP)
   - Frontend: Deploy to static hosting (e.g., Vercel, Netlify)
   - Database: MongoDB Atlas
   - Vector DB: MongoDB Atlas Vector Search

## Documentation Structure

```
docs/
├── api/              # API documentation
├── architecture/     # System design docs
├── deployment/       # Deployment guides
└── user/            # User guides
```

## Testing Strategy (v1.3.1 Focus)

### 1. Comprehensive API Testing
```python
# Test Coverage Priorities (Week 1)
- Authentication endpoints: 100% coverage
- Document management: All CRUD operations
- RAG generation: Query processing
- Admin functions: User management
- Error scenarios: Edge cases and failures
```

### 2. UI Component Testing
```typescript
// Testing Framework (Week 2)
- Jest: Unit testing framework
- React Testing Library: Component testing
- Cypress: End-to-end testing
- MSW: API mocking for isolated tests
- Storybook: Component documentation and testing
```

### 3. Integration Testing
```yaml
# End-to-End Workflows (Week 3)
- User Registration → Login → Dashboard
- Document Upload → Processing → List View
- Query Generation → Response → Citation
- Authentication Flow → Protected Routes
- Error Handling → Recovery → User Feedback
```

### 4. Performance Testing
```yaml
# Performance Benchmarks (Week 4)
Response Time Targets:
  - Authentication: < 200ms
  - Document Upload: < 5s per MB
  - Query Generation: < 10s
  - UI Loading: < 2s initial load
  
Load Testing:
  - 10 concurrent users: Basic functionality
  - 50 concurrent users: Normal load
  - 100+ concurrent users: Stress testing
```

## Monitoring and Logging

1. **Application Logs:**
   - Backend: Structured logging with Python logging
   - Frontend: Error tracking with Sentry

2. **Performance Monitoring:**
   - API response times
   - Document processing times
   - Generation latency

3. **Error Tracking:**
   - Exception monitoring
   - User error reporting
   - System health checks 