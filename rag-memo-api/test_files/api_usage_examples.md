# TinyRAG v1.4 API Usage Examples

## 📖 Complete API Documentation

This document provides comprehensive examples for all TinyRAG v1.4 API endpoints. All examples use curl for demonstration, but can be adapted to any HTTP client.

## 🔐 Authentication

### 1. Register a New User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer@example.com",
    "username": "developer",
    "password": "SecurePassword123!",
    "full_name": "API Developer"
  }'
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user_id": "6859036f0cfc8f1bb0f21c76"
}
```

### 2. Login to Get JWT Token

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "developer@example.com",
    "password": "SecurePassword123!"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "6859036f0cfc8f1bb0f21c76",
    "email": "developer@example.com",
    "username": "developer",
    "full_name": "API Developer"
  }
}
```

### 3. Verify Token

```bash
curl -X GET "http://localhost:8000/auth/verify-token" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 🏗️ v1.4 Project-Based API

### Projects API

#### Create a Project

```bash
curl -X POST "http://localhost:8000/api/v1/projects/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {your_token}" \
  -d '{
    "name": "HR Document Analysis",
    "description": "Project for analyzing HR documents and policies",
    "tenant_type": "HR",
    "visibility": "private",
    "configuration": {
      "default_temperature": 0.7,
      "max_tokens": 2000,
      "enable_analytics": true
    }
  }'
```

**Response:**
```json
{
  "id": "60f4d2e5e8b4a12345678901",
  "name": "HR Document Analysis",
  "description": "Project for analyzing HR documents and policies",
  "tenant_type": "HR",
  "task_type": "RAG",
  "status": "ACTIVE",
  "visibility": "private",
  "owner_id": "6859036f0cfc8f1bb0f21c76",
  "collaborators": [],
  "document_count": 0,
  "element_count": 0,
  "generation_count": 0,
  "created_at": "2025-06-24T10:30:00Z",
  "updated_at": "2025-06-24T10:30:00Z"
}
```

#### List Projects

```bash
curl -X GET "http://localhost:8000/api/v1/projects/?page=1&page_size=10&tenant_type=HR" \
  -H "Authorization: Bearer {your_token}"
```

#### Get Project Details

```bash
curl -X GET "http://localhost:8000/api/v1/projects/60f4d2e5e8b4a12345678901" \
  -H "Authorization: Bearer {your_token}"
```

#### Update Project

```bash
curl -X PUT "http://localhost:8000/api/v1/projects/60f4d2e5e8b4a12345678901" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {your_token}" \
  -d '{
    "description": "Updated: Advanced HR document analysis with ML insights",
    "status": "ACTIVE"
  }'
```

### Elements API (Templates & Tools)

#### Create a Prompt Template

```bash
curl -X POST "http://localhost:8000/api/v1/elements/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {your_token}" \
  -d '{
    "name": "HR Policy Analyzer",
    "description": "Template for analyzing HR policies and procedures",
    "project_id": "60f4d2e5e8b4a12345678901",
    "element_type": "PROMPT_TEMPLATE",
    "template_content": "Analyze the following HR policy document and provide:\n1. Key policy points\n2. Compliance requirements\n3. Potential issues\n\nDocument: {document_content}\nSpecific focus: {focus_area}",
    "variables": ["document_content", "focus_area"],
    "execution_config": {
      "temperature": 0.3,
      "max_tokens": 1500,
      "model": "gpt-4o-mini"
    },
    "tags": ["hr", "policy", "analysis"]
  }'
```

**Response:**
```json
{
  "id": "60f4d2e5e8b4a12345678902",
  "name": "HR Policy Analyzer",
  "description": "Template for analyzing HR policies and procedures",
  "project_id": "60f4d2e5e8b4a12345678901",
  "element_type": "PROMPT_TEMPLATE",
  "status": "DRAFT",
  "template_version": "1.0.0",
  "tags": ["hr", "policy", "analysis"],
  "execution_count": 0,
  "created_at": "2025-06-24T10:35:00Z",
  "updated_at": "2025-06-24T10:35:00Z"
}
```

#### Execute an Element

```bash
curl -X POST "http://localhost:8000/api/v1/elements/60f4d2e5e8b4a12345678902/execute" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {your_token}" \
  -d '{
    "document_content": "Employee Handbook Section 3: Time Off Policies...",
    "focus_area": "vacation day allocation and approval process"
  }'
```

**Response:**
```json
{
  "execution_id": "60f4d2e5e8b4a12345678903",
  "status": "completed",
  "output_content": "Based on the HR policy analysis:\n\n1. Key Policy Points:\n- 15 vacation days annually for full-time employees...",
  "execution_time_ms": 2345,
  "error_message": null
}
```

#### List Elements

```bash
curl -X GET "http://localhost:8000/api/v1/elements/?project_id=60f4d2e5e8b4a12345678901&element_type=PROMPT_TEMPLATE" \
  -H "Authorization: Bearer {your_token}"
```

### Generations API

#### List Generations

```bash
curl -X GET "http://localhost:8000/api/v1/generations/?project_id=60f4d2e5e8b4a12345678901&page=1&page_size=20" \
  -H "Authorization: Bearer {your_token}"
```

**Response:**
```json
[
  {
    "id": "60f4d2e5e8b4a12345678904",
    "element_id": "60f4d2e5e8b4a12345678902",
    "project_id": "60f4d2e5e8b4a12345678901",
    "status": "COMPLETED",
    "model_used": "gpt-4o-mini",
    "chunk_count": 3,
    "token_usage": 1247,
    "created_at": "2025-06-24T10:40:00Z",
    "updated_at": "2025-06-24T10:40:15Z"
  }
]
```

#### Get Generation Details

```bash
curl -X GET "http://localhost:8000/api/v1/generations/60f4d2e5e8b4a12345678904" \
  -H "Authorization: Bearer {your_token}"
```

**Response:**
```json
{
  "id": "60f4d2e5e8b4a12345678904",
  "element_id": "60f4d2e5e8b4a12345678902",
  "project_id": "60f4d2e5e8b4a12345678901",
  "status": "COMPLETED",
  "model_used": "gpt-4o-mini",
  "chunk_count": 3,
  "token_usage": 1247,
  "prompt": "Analyze the following HR policy document...",
  "content": "Based on the HR policy analysis:\n\n1. Key Policy Points:\n- 15 vacation days annually...",
  "cost_usd": 0.024,
  "generation_time_ms": 2345,
  "error_message": null,
  "created_at": "2025-06-24T10:40:00Z",
  "updated_at": "2025-06-24T10:40:15Z"
}
```

### Evaluations API

#### Create an Evaluation

```bash
curl -X POST "http://localhost:8000/api/v1/evaluations/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {your_token}" \
  -d '{
    "generation_id": "60f4d2e5e8b4a12345678904",
    "criteria": [
      {
        "name": "accuracy",
        "description": "How accurate is the policy analysis?",
        "weight": 0.4,
        "scale": "1-10"
      },
      {
        "name": "completeness",
        "description": "How complete is the coverage of policy points?",
        "weight": 0.3,
        "scale": "1-10"
      },
      {
        "name": "clarity",
        "description": "How clear and understandable is the analysis?",
        "weight": 0.3,
        "scale": "1-10"
      }
    ],
    "evaluation_config": {
      "llm_judge": true,
      "model": "gpt-4o",
      "temperature": 0.1
    }
  }'
```

#### List Evaluations

```bash
curl -X GET "http://localhost:8000/api/v1/evaluations/?project_id=60f4d2e5e8b4a12345678901&min_score=7.0" \
  -H "Authorization: Bearer {your_token}"
```

### Documents API

#### List Documents

```bash
curl -X GET "http://localhost:8000/api/v1/documents/?project_id=60f4d2e5e8b4a12345678901&status=PROCESSED" \
  -H "Authorization: Bearer {your_token}"
```

## 📊 Legacy v1.3 API (Backward Compatibility)

### Generate Response (Legacy)

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {your_token}" \
  -d '{
    "query": "What are the key points in the uploaded HR documents?",
    "document_ids": ["60f4d2e5e8b4a12345678905"],
    "max_tokens": 1000,
    "temperature": 0.7
  }'
```

### Get Generation (Legacy)

```bash
curl -X GET "http://localhost:8000/generations/60f4d2e5e8b4a12345678906" \
  -H "Authorization: Bearer {your_token}"
```

## 🔧 Health & Admin Endpoints

### Health Check

```bash
curl -X GET "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.4.0",
  "api_versions": {
    "v1.3": "legacy endpoints (/documents, /memos, /generate)",
    "v1.4": "project-based endpoints (/api/v1/*)"
  },
  "services": {
    "auth": true,
    "llm_extractor": false,
    "enhanced_reranker": false,
    "document_service": true,
    "generation_service": true,
    "v1.4_api": true,
    "project_service": true,
    "element_service": true
  },
  "database": {
    "models_registered": [
      "User", "APIKey", "Document", "Generation",
      "Project", "Element", "ElementGeneration", "Evaluation"
    ]
  }
}
```

### Admin System Stats

```bash
curl -X GET "http://localhost:8000/admin/system-stats" \
  -H "Authorization: Bearer {admin_token}"
```

**Response:**
```json
{
  "v1.3_models": {
    "users": 15,
    "documents": 145,
    "generations": 89
  },
  "v1.4_models": {
    "projects": 8,
    "elements": 23,
    "element_generations": 67,
    "evaluations": 34
  },
  "services": {
    "auth_service": true,
    "v1.4_api": true
  }
}
```

## 📝 Common Usage Patterns

### 1. Complete Project Workflow

```bash
# 1. Create project
PROJECT_ID=$(curl -s -X POST "http://localhost:8000/api/v1/projects/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Customer Support Analysis",
    "tenant_type": "QA_GENERATION"
  }' | jq -r '.id')

# 2. Create element template
ELEMENT_ID=$(curl -s -X POST "http://localhost:8000/api/v1/elements/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"name\": \"Support Ticket Analyzer\",
    \"project_id\": \"$PROJECT_ID\",
    \"element_type\": \"PROMPT_TEMPLATE\",
    \"template_content\": \"Analyze this support ticket: {ticket_content}\"
  }" | jq -r '.id')

# 3. Execute element
curl -X POST "http://localhost:8000/api/v1/elements/$ELEMENT_ID/execute" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "ticket_content": "Customer complaining about slow loading times..."
  }'
```

### 2. Batch Operations

```bash
# List all projects and their statistics
curl -X GET "http://localhost:8000/api/v1/projects/?include_stats=true" \
  -H "Authorization: Bearer $TOKEN"

# Get all elements for a specific tenant type
curl -X GET "http://localhost:8000/api/v1/elements/?tenant_type=HR&status=ACTIVE" \
  -H "Authorization: Bearer $TOKEN"
```

## 🔄 Error Handling Examples

### Authentication Errors

```bash
# Missing token
curl -X GET "http://localhost:8000/api/v1/projects/"
# Response: 401 Unauthorized

# Invalid token
curl -X GET "http://localhost:8000/api/v1/projects/" \
  -H "Authorization: Bearer invalid_token"
# Response: 401 Unauthorized
```

### Validation Errors

```bash
# Invalid project data
curl -X POST "http://localhost:8000/api/v1/projects/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "",
    "tenant_type": "INVALID_TYPE"
  }'
# Response: 422 Validation Error
```

## 🚀 Testing Your Implementation

1. **Start the API server:**
   ```bash
   cd rag-memo-api
   python main.py
   ```

2. **Run comprehensive tests:**
   ```bash
   python test_api_comprehensive.py
   ```

3. **Access interactive documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 📚 Additional Resources

- **OpenAPI Specification**: Available at `/openapi.json`
- **Health Check**: `/health` - Always test this first
- **Admin Interface**: `/admin/*` - Requires admin privileges
- **Legacy Compatibility**: All v1.3 endpoints still work

---

*This documentation covers TinyRAG v1.4 API. For the latest updates, always refer to the interactive documentation at `/docs`.* 