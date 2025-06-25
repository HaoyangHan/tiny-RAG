# TinyRAG v1.4 API Documentation

**Version**: 1.4.0  
**Release Date**: June 2025  
**API Base URL**: `http://localhost:8000/api/v1`  
**Documentation**: `http://localhost:8000/docs`

---

## 📋 Project Overview

**TinyRAG v1.4** is a comprehensive **Retrieval-Augmented Generation (RAG) platform** designed for versatile AI-powered workflows across multiple use cases:

### 🎯 **Core Capabilities**

1. **📊 Project-Based Organization**
   - Multi-tenant project management with role-based access control
   - Collaborative workspaces for teams and organizations
   - Flexible project types: Personal, Team, Enterprise, Research

2. **🤖 Flexible AI Workflows**
   - **Raw LLM Access**: Direct interaction with language models
   - **RAG Pipeline**: Document-based question answering with citations
   - **Agentic Workflows**: Multi-step autonomous AI task execution
   - **MCP (Model Context Protocol)**: Standardized AI tool integration

3. **📁 Advanced Document Management**
   - Multi-format support (PDF, DOCX, TXT, MD)
   - Intelligent chunking and vector embeddings
   - Metadata extraction and semantic search
   - Real-time processing status tracking

4. **⚡ Template & Element System**
   - Reusable prompt templates with variable substitution
   - Configurable AI tools and agents
   - Version control and template management
   - Cross-project element sharing

5. **📈 Evaluation & Analytics**
   - LLM-as-a-judge evaluation framework
   - Quality scoring and hallucination detection
   - Usage analytics and cost tracking
   - Performance metrics and optimization insights

### 🏗️ **Architecture Highlights**

- **Microservices Design**: Modular, scalable architecture
- **JWT Authentication**: Secure token-based authentication
- **Vector Database**: Qdrant for semantic search and embeddings
- **Real-time Processing**: Async document processing pipeline
- **Multi-LLM Support**: OpenAI, Anthropic, and extensible provider system
- **Docker Containerization**: Complete containerized deployment

---

## 🛠️ High-Level API Categories

### 🔐 **Authentication** (`/auth/*`)
User registration, login, token management, and session control.

### 👥 **Users** (`/users/*`)
User profile management, analytics, and account settings.

### 📊 **Projects** (`/projects/*`)
Project creation, management, collaboration, and organization.

### 📄 **Documents** (`/documents/*`)
Document upload, processing, content management, and metadata extraction.

### ⚡ **Elements** (`/elements/*`)
Template management, prompt creation, tool configuration, and reusable components.

### 🤖 **Generations** (`/generations/*`)
LLM content generation, execution tracking, and result management.

### 📈 **Evaluations** (`/evaluations/*`)
Quality assessment, scoring, hallucination detection, and performance analysis.

---

## 📚 Detailed API Endpoints

### 🔐 Authentication Endpoints

#### **POST** `/auth/register`
**Create new user account**

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "newuser",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Response (201):**
```json
{
  "id": "60f4d2e5e8b4a12345678901",
  "email": "user@example.com",
  "username": "newuser",
  "full_name": "John Doe",
  "role": "USER",
  "status": "ACTIVE",
  "created_at": "2025-06-25T10:30:00Z",
  "last_login": null
}
```

#### **POST** `/auth/login`
**Authenticate user and get access token**

**Request Body:**
```json
{
  "identifier": "user@example.com",
  "password": "SecurePass123!",
  "remember_me": false
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user_id": "60f4d2e5e8b4a12345678901"
}
```

#### **GET** `/auth/me`
**Get current authenticated user information**

**Headers:** `Authorization: Bearer {token}`

**Response (200):**
```json
{
  "id": "60f4d2e5e8b4a12345678901",
  "email": "user@example.com",
  "username": "newuser",
  "full_name": "John Doe",
  "role": "USER",
  "status": "ACTIVE",
  "created_at": "2025-06-25T10:30:00Z",
  "last_login": "2025-06-25T14:15:00Z"
}
```

#### **GET** `/auth/verify-token`
**Verify token validity**

**Headers:** `Authorization: Bearer {token}`

**Response (200):** Same as `/auth/me`

#### **POST** `/auth/logout`
**Logout current user**

**Headers:** `Authorization: Bearer {token}`

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

---

### 👥 User Management Endpoints

#### **GET** `/users/profile`
**Get extended user profile with statistics**

**Headers:** `Authorization: Bearer {token}`

**Response (200):**
```json
{
  "id": "60f4d2e5e8b4a12345678901",
  "email": "user@example.com",
  "username": "newuser",
  "full_name": "John Doe",
  "role": "USER",
  "status": "ACTIVE",
  "created_at": "2025-06-25T10:30:00Z",
  "last_login": "2025-06-25T14:15:00Z",
  "project_count": 5,
  "collaboration_count": 3
}
```

#### **GET** `/users/analytics`
**Get user analytics and dashboard statistics**

**Headers:** `Authorization: Bearer {token}`

**Response (200):**
```json
{
  "projects": {
    "total": 5,
    "owned": 3,
    "collaborated": 2,
    "recent": 1
  },
  "elements": {
    "total": 12,
    "recent": 3,
    "by_type": {
      "PROMPT_TEMPLATE": 8,
      "MCP_CONFIG": 2,
      "AGENTIC_TOOL": 2
    }
  },
  "generations": {
    "total": 45,
    "recent": 8,
    "total_tokens": 125430,
    "total_cost_usd": 12.54
  },
  "evaluations": {
    "total": 23,
    "recent": 5,
    "completed": 20,
    "average_score": 8.7
  }
}
```

---

### 📊 Project Management Endpoints

#### **POST** `/projects`
**Create new project**

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "name": "Customer Support Analysis",
  "description": "RAG system for analyzing customer support tickets",
  "tenant_type": "TEAM",
  "keywords": ["support", "analysis", "customer"],
  "visibility": "PRIVATE"
}
```

**Response (201):**
```json
{
  "id": "60f4d2e5e8b4a12345678902",
  "name": "Customer Support Analysis",
  "description": "RAG system for analyzing customer support tickets",
  "tenant_type": "TEAM",
  "keywords": ["support", "analysis", "customer"],
  "visibility": "PRIVATE",
  "status": "ACTIVE",
  "owner_id": "60f4d2e5e8b4a12345678901",
  "collaborators": [],
  "document_count": 0,
  "element_count": 0,
  "generation_count": 0,
  "created_at": "2025-06-25T10:35:00Z",
  "updated_at": "2025-06-25T10:35:00Z"
}
```

#### **GET** `/projects`
**List accessible projects with filtering and pagination**

**Headers:** `Authorization: Bearer {token}`

**Query Parameters:**
- `tenant_type`: Filter by tenant type (PERSONAL, TEAM, ENTERPRISE, RESEARCH)
- `visibility`: Filter by visibility (PRIVATE, TEAM, PUBLIC)
- `status`: Filter by status (ACTIVE, ARCHIVED, SUSPENDED)
- `keyword`: Search in names and descriptions
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Response (200):**
```json
{
  "projects": [
    {
      "id": "60f4d2e5e8b4a12345678902",
      "name": "Customer Support Analysis",
      "description": "RAG system for analyzing customer support tickets",
      "tenant_type": "TEAM",
      "visibility": "PRIVATE",
      "status": "ACTIVE",
      "document_count": 5,
      "element_count": 3,
      "generation_count": 12,
      "created_at": "2025-06-25T10:35:00Z"
    }
  ],
  "total_count": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

#### **GET** `/projects/{project_id}`
**Get detailed project information**

**Headers:** `Authorization: Bearer {token}`

**Response (200):**
```json
{
  "id": "60f4d2e5e8b4a12345678902",
  "name": "Customer Support Analysis",
  "description": "RAG system for analyzing customer support tickets",
  "tenant_type": "TEAM",
  "keywords": ["support", "analysis", "customer"],
  "visibility": "PRIVATE",
  "status": "ACTIVE",
  "owner_id": "60f4d2e5e8b4a12345678901",
  "collaborators": ["60f4d2e5e8b4a12345678903"],
  "document_count": 5,
  "element_count": 3,
  "generation_count": 12,
  "created_at": "2025-06-25T10:35:00Z",
  "updated_at": "2025-06-25T14:20:00Z"
}
```

#### **GET** `/projects/{project_id}/documents`
**List documents in a project**

**Headers:** `Authorization: Bearer {token}`

**Response (200):** Array of document objects (see Documents section)

#### **GET** `/projects/{project_id}/elements`
**List elements in a project**

**Headers:** `Authorization: Bearer {token}`

**Response (200):** Array of element objects (see Elements section)

#### **PUT** `/projects/{project_id}`
**Update project information**

**Headers:** `Authorization: Bearer {token}`

**Request Body:** Partial project object with fields to update

#### **DELETE** `/projects/{project_id}`
**Delete project (soft delete)**

**Headers:** `Authorization: Bearer {token}`

**Response (204):** No content

---

### 📄 Document Management Endpoints

#### **POST** `/documents/upload`
**Upload and process document**

**Headers:** `Authorization: Bearer {token}`

**Request:** Multipart form data
- `file`: Document file (PDF, DOCX, TXT, MD)
- `project_id`: Associated project ID (query parameter)

**Response (201):**
```json
{
  "id": "60f4d2e5e8b4a12345678903",
  "filename": "support_policies.pdf",
  "project_id": "60f4d2e5e8b4a12345678902",
  "content_type": "application/pdf",
  "file_size": 245760,
  "status": "PROCESSED",
  "chunks": [
    {
      "text": "Customer support policies and procedures...",
      "page_number": 1,
      "chunk_index": 0,
      "embedding": [0.123, -0.456, 0.789]
    }
  ],
  "chunk_count": 15,
  "created_at": "2025-06-25T10:40:00Z",
  "updated_at": "2025-06-25T10:41:30Z"
}
```

#### **GET** `/documents`
**List accessible documents**

**Headers:** `Authorization: Bearer {token}`

**Query Parameters:**
- `project_id`: Filter by project ID
- `status`: Filter by processing status (PROCESSING, PROCESSED, FAILED)

**Response (200):** Array of document objects

#### **GET** `/documents/{document_id}`
**Get document details**

**Headers:** `Authorization: Bearer {token}`

**Response (200):** Full document object with chunks and embeddings

#### **GET** `/documents/{document_id}/content`
**Get document content with metadata**

**Headers:** `Authorization: Bearer {token}`

**Response (200):**
```json
{
  "document_id": "60f4d2e5e8b4a12345678903",
  "full_text": "Complete document text content...",
  "chunks": [
    {
      "text": "Chunk text...",
      "page_number": 1,
      "chunk_index": 0,
      "metadata": {
        "section": "Introduction",
        "keywords": ["policy", "customer", "support"]
      }
    }
  ],
  "total_tokens": 2456,
  "language": "en"
}
```

#### **DELETE** `/documents/{document_id}`
**Delete document**

**Headers:** `Authorization: Bearer {token}`

**Response (204):** No content

---

### ⚡ Element Management Endpoints

#### **POST** `/elements`
**Create new element (template/tool)**

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "name": "Support Ticket Analyzer",
  "description": "Analyzes customer support tickets for sentiment and priority",
  "project_id": "60f4d2e5e8b4a12345678902",
  "element_type": "PROMPT_TEMPLATE",
  "template_content": "Analyze this support ticket:\n\n{ticket_content}\n\nProvide:\n1. Sentiment: {sentiment_options}\n2. Priority: {priority_levels}\n3. Summary: Brief description",
  "variables": ["ticket_content", "sentiment_options", "priority_levels"],
  "execution_config": {
    "model": "gpt-4o-mini",
    "temperature": 0.3,
    "max_tokens": 500
  },
  "tags": ["support", "analysis", "classification"]
}
```

**Response (201):**
```json
{
  "id": "60f4d2e5e8b4a12345678904",
  "name": "Support Ticket Analyzer",
  "description": "Analyzes customer support tickets for sentiment and priority",
  "project_id": "60f4d2e5e8b4a12345678902",
  "element_type": "PROMPT_TEMPLATE",
  "status": "ACTIVE",
  "template_version": "1.0.0",
  "tags": ["support", "analysis", "classification"],
  "execution_count": 0,
  "created_at": "2025-06-25T10:45:00Z",
  "updated_at": "2025-06-25T10:45:00Z"
}
```

#### **GET** `/elements`
**List accessible elements**

**Headers:** `Authorization: Bearer {token}`

**Query Parameters:**
- `project_id`: Filter by project ID
- `element_type`: Filter by type (PROMPT_TEMPLATE, MCP_CONFIG, AGENTIC_TOOL)
- `status`: Filter by status (ACTIVE, DRAFT, ARCHIVED)
- `page`: Page number
- `page_size`: Items per page

**Response (200):** Array of element objects

#### **GET** `/elements/{element_id}`
**Get detailed element information**

**Headers:** `Authorization: Bearer {token}`

**Response (200):**
```json
{
  "id": "60f4d2e5e8b4a12345678904",
  "name": "Support Ticket Analyzer",
  "description": "Analyzes customer support tickets for sentiment and priority",
  "project_id": "60f4d2e5e8b4a12345678902",
  "element_type": "PROMPT_TEMPLATE",
  "status": "ACTIVE",
  "template_content": "Analyze this support ticket:\n\n{ticket_content}\n\nProvide:\n1. Sentiment: {sentiment_options}\n2. Priority: {priority_levels}\n3. Summary: Brief description",
  "template_variables": ["ticket_content", "sentiment_options", "priority_levels"],
  "template_version": "1.0.0",
  "execution_config": {
    "model": "gpt-4o-mini",
    "temperature": 0.3,
    "max_tokens": 500
  },
  "tags": ["support", "analysis", "classification"],
  "execution_count": 25,
  "usage_statistics": {
    "total_executions": 25,
    "success_rate": 0.96,
    "average_tokens": 387,
    "total_cost_usd": 2.45
  },
  "created_at": "2025-06-25T10:45:00Z",
  "updated_at": "2025-06-25T15:20:00Z"
}
```

#### **POST** `/elements/{element_id}/execute`
**Execute element with variables**

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "variables": {
    "ticket_content": "Customer is angry about delayed delivery...",
    "sentiment_options": "Positive, Neutral, Negative",
    "priority_levels": "Low, Medium, High, Critical"
  },
  "execution_config": {
    "temperature": 0.2
  }
}
```

**Response (200):**
```json
{
  "execution_id": "60f4d2e5e8b4a12345678905",
  "element_id": "60f4d2e5e8b4a12345678904",
  "status": "COMPLETED",
  "result": {
    "content": "1. Sentiment: Negative\n2. Priority: High\n3. Summary: Customer expressing frustration about delivery delay, requires immediate attention",
    "metadata": {
      "model_used": "gpt-4o-mini",
      "tokens_used": 142,
      "cost_usd": 0.008,
      "execution_time_ms": 1250
    }
  },
  "created_at": "2025-06-25T15:30:00Z"
}
```

#### **PUT** `/elements/{element_id}`
**Update element**

**Headers:** `Authorization: Bearer {token}`

**Request Body:** Partial element object with fields to update

#### **DELETE** `/elements/{element_id}`
**Delete element**

**Headers:** `Authorization: Bearer {token}`

**Response (204):** No content

---

### 🤖 Generation Management Endpoints

#### **GET** `/generations`
**List generations with filtering**

**Headers:** `Authorization: Bearer {token}`

**Query Parameters:**
- `project_id`: Filter by project ID
- `element_id`: Filter by element ID
- `status`: Filter by status (PENDING, PROCESSING, COMPLETED, FAILED)
- `page`: Page number
- `page_size`: Items per page

**Response (200):**
```json
[
  {
    "id": "60f4d2e5e8b4a12345678905",
    "element_id": "60f4d2e5e8b4a12345678904",
    "project_id": "60f4d2e5e8b4a12345678902",
    "status": "COMPLETED",
    "model_used": "gpt-4o-mini",
    "chunk_count": 1,
    "token_usage": 142,
    "created_at": "2025-06-25T15:30:00Z",
    "updated_at": "2025-06-25T15:30:15Z"
  }
]
```

#### **GET** `/generations/{generation_id}`
**Get detailed generation result**

**Headers:** `Authorization: Bearer {token}`

**Response (200):**
```json
{
  "id": "60f4d2e5e8b4a12345678905",
  "element_id": "60f4d2e5e8b4a12345678904",
  "project_id": "60f4d2e5e8b4a12345678902",
  "status": "COMPLETED",
  "model_used": "gpt-4o-mini",
  "chunk_count": 1,
  "token_usage": 142,
  "prompt": "Analyze this support ticket:\n\nCustomer is angry about delayed delivery...",
  "content": "1. Sentiment: Negative\n2. Priority: High\n3. Summary: Customer expressing frustration about delivery delay, requires immediate attention",
  "cost_usd": 0.008,
  "generation_time_ms": 1250,
  "error_message": null,
  "created_at": "2025-06-25T15:30:00Z",
  "updated_at": "2025-06-25T15:30:15Z"
}
```

---

### 📈 Evaluation Endpoints

#### **POST** `/evaluations`
**Create evaluation for a generation**

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "generation_id": "60f4d2e5e8b4a12345678905",
  "evaluator_model": "gpt-4o",
  "custom_criteria": {
    "accuracy": 0.4,
    "relevance": 0.3,
    "clarity": 0.3
  }
}
```

**Response (201):**
```json
{
  "id": "60f4d2e5e8b4a12345678906",
  "generation_id": "60f4d2e5e8b4a12345678905",
  "project_id": "60f4d2e5e8b4a12345678902",
  "status": "PENDING",
  "overall_score": null,
  "evaluator_model": "gpt-4o",
  "hallucination_detected": false,
  "created_at": "2025-06-25T15:35:00Z",
  "updated_at": "2025-06-25T15:35:00Z"
}
```

#### **GET** `/evaluations`
**List evaluations with filtering**

**Headers:** `Authorization: Bearer {token}`

**Query Parameters:**
- `project_id`: Filter by project ID
- `generation_id`: Filter by generation ID
- `status`: Filter by status

**Response (200):** Array of evaluation objects

#### **GET** `/evaluations/{evaluation_id}`
**Get detailed evaluation results**

**Headers:** `Authorization: Bearer {token}`

**Response (200):** Detailed evaluation object with scores and analysis

---

## 🔒 Authentication & Authorization

### **JWT Token Format**
All authenticated endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### **Token Expiration**
- Default expiration: 30 minutes
- Remember me: 7 days
- Refresh tokens: Not yet implemented

### **Role-Based Access Control**
- **USER**: Standard user permissions
- **ADMIN**: Full system access
- **VIEWER**: Read-only access

### **Project-Level Permissions**
- **OWNER**: Full project control
- **COLLABORATOR**: Edit access
- **VIEWER**: Read-only access

---

## 📊 Response Formats

### **Success Responses**
- **200 OK**: Successful request
- **201 Created**: Resource created successfully
- **204 No Content**: Successful deletion

### **Error Responses**
```json
{
  "detail": "Error description",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-06-25T15:40:00Z"
}
```

### **Common Error Codes**
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error

---

## 🚀 Getting Started

### **1. Authentication**
```bash
# Register
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"user","password":"SecurePass123!","full_name":"John Doe"}'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"identifier":"user@example.com","password":"SecurePass123!"}'
```

### **2. Create Project**
```bash
curl -X POST "http://localhost:8000/api/v1/projects" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"My RAG Project","description":"AI-powered document analysis","tenant_type":"PERSONAL"}'
```

### **3. Upload Document**
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload?project_id=PROJECT_ID" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf"
```

### **4. Create Element**
```bash
curl -X POST "http://localhost:8000/api/v1/elements" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Document Analyzer","project_id":"PROJECT_ID","element_type":"PROMPT_TEMPLATE","template_content":"Analyze: {content}","variables":["content"]}'
```

### **5. Execute Element**
```bash
curl -X POST "http://localhost:8000/api/v1/elements/ELEMENT_ID/execute" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"variables":{"content":"Document content to analyze..."}}'
```

---

## 📖 Additional Resources

- **Interactive API Docs**: `http://localhost:8000/docs`
- **OpenAPI Spec**: `http://localhost:8000/openapi.json`
- **Health Check**: `http://localhost:8000/health`
- **System Statistics**: `http://localhost:8000/admin/system-stats` (admin only)

---

**TinyRAG v1.4** - Comprehensive RAG Platform for Modern AI Workflows 🚀 