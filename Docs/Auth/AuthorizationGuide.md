# TinyRAG Authorization System Guide

## Overview

TinyRAG v1.3 includes a comprehensive JWT-based authentication and authorization system with role-based access control (RBAC), API key management, and rate limiting. This guide provides complete instructions for setting up and using the authorization features.

## 🔧 System Setup

### 1. Environment Configuration

First, configure your environment variables in `.env`:

```bash
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-here-make-it-long-and-random
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database Configuration
MONGODB_URL=mongodb://localhost:27017/tinyrag
REDIS_URL=redis://localhost:6379

# LLM Configuration (for metadata extraction)
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Rate Limiting
RATE_LIMIT_ENABLED=true
```

### 2. Initialize Authentication Service

In your FastAPI application (`main.py`):

```python
from fastapi import FastAPI
from auth.service import AuthService
from auth.routes import init_auth_routes
from auth.models import User, APIKey
import os

app = FastAPI(title="TinyRAG API", version="1.3.0")

# Initialize authentication service
auth_service = AuthService(
    secret_key=os.getenv("JWT_SECRET_KEY"),
    algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
    access_token_expire_minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
)

# Initialize authentication routes
auth_router = init_auth_routes(auth_service)
app.include_router(auth_router)

# Initialize database models
@app.on_event("startup")
async def startup_event():
    # Initialize Beanie with authentication models
    await init_beanie(database=motor_client.tinyrag, document_models=[User, APIKey])
```

## 👥 User Management

### User Roles and Permissions

TinyRAG supports three user roles:

- **`ADMIN`**: Full system access, can manage all users and settings
- **`USER`**: Standard access, can use all RAG features, manage own profile
- **`VIEWER`**: Read-only access, can view documents and results

### Creating the First Admin User

#### Method 1: API Registration (Recommended)

```bash
# Register the first user (will be created as USER role)
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "username": "admin",
    "password": "SecurePassword123!",
    "full_name": "System Administrator"
  }'
```

Then manually promote to admin role in MongoDB:

```javascript
// Connect to MongoDB and update user role
db.users.updateOne(
  { "email": "admin@example.com" },
  { "$set": { "role": "admin" } }
)
```

#### Method 2: Direct Database Creation

```python
# Create admin user directly (run once)
from auth.models import User, UserRole, UserStatus
from auth.service import AuthService
import asyncio

async def create_admin_user():
    auth_service = AuthService("your-secret-key")
    
    admin_user = User(
        email="admin@example.com",
        username="admin",
        hashed_password=auth_service.get_password_hash("SecurePassword123!"),
        full_name="System Administrator",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE
    )
    
    await admin_user.save()
    print("Admin user created successfully!")

# Run the function
asyncio.run(create_admin_user())
```

## 🔐 Authentication Workflows

### 1. User Registration

**Endpoint**: `POST /auth/register`

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "newuser",
    "password": "SecurePassword123!",
    "full_name": "John Doe"
  }'
```

**Response**:
```json
{
  "id": "user_id_here",
  "email": "user@example.com",
  "username": "newuser",
  "full_name": "John Doe",
  "role": "user",
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z",
  "last_login": null
}
```

**Password Requirements**:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

### 2. User Login

**Endpoint**: `POST /auth/login`

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "user@example.com",
    "password": "SecurePassword123!",
    "remember_me": false
  }'
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user_id": "user_id_here",
  "role": "user"
}
```

**Login Options**:
- Use email or username as identifier
- `remember_me: true` extends session to 7 days
- Rate limited to 10 attempts per minute per IP

### 3. Using JWT Tokens

Include the JWT token in the Authorization header for protected endpoints:

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 🔑 API Key Management

### Creating API Keys

**Endpoint**: `POST /auth/api-keys`

```bash
curl -X POST "http://localhost:8000/auth/api-keys" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Application Key",
    "permissions": ["read", "write"],
    "usage_limit": 1000,
    "expires_in_days": 90
  }'
```

**Response**:
```json
{
  "key_id": "key_abc123",
  "name": "My Application Key",
  "api_key": "sk-1234567890abcdef...",
  "permissions": ["read", "write"],
  "usage_limit": 1000,
  "expires_at": "2024-04-15T10:30:00Z",
  "created_at": "2024-01-15T10:30:00Z",
  "warning": "Store this API key securely. It will not be shown again."
}
```

### Using API Keys

```bash
# Use API key in X-API-Key header
curl -X GET "http://localhost:8000/documents" \
  -H "X-API-Key: sk-1234567890abcdef..."
```

### Managing API Keys

```bash
# List all your API keys
curl -X GET "http://localhost:8000/auth/api-keys" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Delete an API key
curl -X DELETE "http://localhost:8000/auth/api-keys/key_abc123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🛡️ Protecting Your Endpoints

### Basic Protection

```python
from fastapi import Depends
from auth.routes import get_current_user
from auth.models import User

@app.get("/protected-endpoint")
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}!"}
```

### Role-Based Protection

```python
from auth.service import AuthService
from auth.models import UserRole

# Require admin role
@app.get("/admin-only")
async def admin_only_endpoint(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"message": "Admin access granted"}

# Using decorator (if implemented)
@auth_service.require_role(UserRole.ADMIN)
@app.get("/admin-endpoint")
async def admin_endpoint(current_user: User = Depends(get_current_user)):
    return {"data": "sensitive_admin_data"}
```

### API Key Protection

```python
from auth.service import AuthService

async def verify_api_key(api_key: str = Header(None, alias="X-API-Key")):
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    key_obj = await auth_service.verify_api_key(api_key)
    if not key_obj:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return key_obj

@app.get("/api-protected")
async def api_protected_endpoint(api_key_obj = Depends(verify_api_key)):
    return {"message": "API key access granted"}
```

## 👤 User Profile Management

### Get Current User Profile

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Update Profile

```bash
curl -X PUT "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Smith",
    "email": "john.smith@example.com"
  }'
```

## 👑 Admin Operations

### List All Users

```bash
curl -X GET "http://localhost:8000/auth/users?skip=0&limit=50" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN"
```

### Update Any User (Admin Only)

```bash
curl -X PUT "http://localhost:8000/auth/users/USER_ID" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "admin",
    "status": "active"
  }'
```

## 🚦 Rate Limiting

The system includes built-in rate limiting:

- **Registration**: 5 attempts per minute per IP
- **Login**: 10 attempts per minute per IP
- **API calls**: Configurable per endpoint

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1642694400
```

## 🔒 Security Best Practices

### 1. JWT Token Security

- **Store securely**: Use httpOnly cookies in production, not localStorage
- **Short expiration**: Default 30 minutes, use refresh tokens for longer sessions
- **Secure transmission**: Always use HTTPS in production

### 2. Password Security

- **Strong passwords**: Enforce complexity requirements
- **Hashing**: Uses bcrypt with automatic salt generation
- **No storage**: Never store plain text passwords

### 3. API Key Security

- **Limited scope**: Grant minimal required permissions
- **Expiration**: Set reasonable expiration dates
- **Monitoring**: Track usage and detect anomalies
- **Rotation**: Regularly rotate keys

### 4. Environment Security

```bash
# Production .env example
JWT_SECRET_KEY=extremely-long-random-string-min-256-bits
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/tinyrag
REDIS_URL=rediss://user:pass@redis-host:6380

# Never commit .env files to version control
echo ".env*" >> .gitignore
```

## 🐛 Troubleshooting

### Common Issues

1. **"Authentication service not initialized"**
   ```python
   # Ensure auth service is initialized before routes
   auth_service = AuthService(secret_key="your-secret")
   auth_router = init_auth_routes(auth_service)
   ```

2. **"Invalid authentication credentials"**
   - Check JWT token format and expiration
   - Verify secret key matches between services
   - Ensure token is included in Authorization header

3. **"Rate limit exceeded"**
   - Wait for rate limit window to reset
   - Implement exponential backoff in clients
   - Consider API keys for higher limits

4. **Database connection errors**
   - Verify MongoDB connection string
   - Ensure database and collections exist
   - Check network connectivity

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# In auth service
logger = logging.getLogger("auth")
logger.setLevel(logging.DEBUG)
```

## 📝 Frontend Integration

### React/Next.js Example

```typescript
// auth.ts - Authentication utility
class AuthService {
  private static TOKEN_KEY = 'access_token';
  
  static async login(identifier: string, password: string): Promise<boolean> {
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier, password })
      });
      
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem(this.TOKEN_KEY, data.access_token);
        return true;
      }
    } catch (error) {
      console.error('Login failed:', error);
    }
    return false;
  }
  
  static getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }
  
  static async makeAuthenticatedRequest(url: string, options: RequestInit = {}) {
    const token = this.getToken();
    return fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`
      }
    });
  }
  
  static logout() {
    localStorage.removeItem(this.TOKEN_KEY);
  }
}
```

## 🚀 Production Deployment

### Docker Configuration

```dockerfile
# Dockerfile for auth-enabled API
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production

```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    environment:
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - MONGODB_URL=${MONGODB_URL}
      - REDIS_URL=${REDIS_URL}
    ports:
      - "8000:8000"
    depends_on:
      - mongodb
      - redis
```

This comprehensive guide covers all aspects of the TinyRAG authorization system. For additional support, refer to the API documentation at `/docs` when the server is running. 