"""
Authentication routes for TinyRAG API.
"""

from typing import Dict, List, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .models import (
    User, UserCreate, UserUpdate, UserResponse, LoginRequest, Token,
    APIKeyCreate, APIKeyResponse
)
from .service import AuthService

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create router
router = APIRouter(prefix="/auth", tags=["authentication"])

# Initialize auth service (will be configured in main app)
auth_service: AuthService = None


def get_auth_service() -> AuthService:
    """Get the authentication service instance."""
    if auth_service is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service not initialized"
        )
    return auth_service


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> User:
    """Dependency to get current authenticated user."""
    service = get_auth_service()
    return await service.get_current_user(credentials)


@router.post("/register", response_model=UserResponse)
@limiter.limit("5/minute")
async def register_user(
    user_data: UserCreate,
    request: Request
) -> UserResponse:
    """
    Register a new user account.
    
    Creates a new user with the provided information.
    Rate limited to 5 registrations per minute per IP.
    """
    service = get_auth_service()
    
    try:
        user = await service.create_user(user_data)
        
        return UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            status=user.status,
            created_at=user.created_at,
            last_login=user.last_login
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(
    login_data: LoginRequest,
    request: Request
) -> Token:
    """
    Authenticate user and return access token.
    
    Supports login with either email or username.
    Rate limited to 10 attempts per minute per IP.
    """
    service = get_auth_service()
    
    # Authenticate user
    user = await service.authenticate_user(
        login_data.identifier, 
        login_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    token = service.create_access_token(user, login_data.remember_me)
    
    return token


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get current user information.
    
    Returns the profile information of the authenticated user.
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
        status=current_user.status,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Update current user profile.
    
    Allows users to update their own profile information.
    """
    service = get_auth_service()
    
    updated_user = await service.update_user(
        str(current_user.id), 
        user_update, 
        current_user
    )
    
    return UserResponse(
        id=str(updated_user.id),
        email=updated_user.email,
        username=updated_user.username,
        full_name=updated_user.full_name,
        role=updated_user.role,
        status=updated_user.status,
        created_at=updated_user.created_at,
        last_login=updated_user.last_login
    )


@router.post("/api-keys", response_model=Dict[str, Any])
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Create a new API key for the current user.
    
    Returns the API key information including the plain key (only shown once).
    """
    service = get_auth_service()
    
    api_key_doc, plain_key = await service.create_api_key(current_user, key_data)
    
    return {
        "key_id": api_key_doc.key_id,
        "name": api_key_doc.name,
        "api_key": plain_key,  # Only shown once
        "permissions": api_key_doc.permissions,
        "usage_limit": api_key_doc.usage_limit,
        "expires_at": api_key_doc.expires_at,
        "created_at": api_key_doc.created_at,
        "warning": "Store this API key securely. It will not be shown again."
    }


@router.get("/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user)
) -> List[APIKeyResponse]:
    """
    List all API keys for the current user.
    
    Returns API key information without the actual key values.
    """
    from .models import APIKey
    
    api_keys = await APIKey.find({"user_id": str(current_user.id)}).to_list()
    
    return [
        APIKeyResponse(
            key_id=key.key_id,
            name=key.name,
            permissions=key.permissions,
            usage_count=key.usage_count,
            usage_limit=key.usage_limit,
            created_at=key.created_at,
            expires_at=key.expires_at,
            last_used=key.last_used,
            is_active=key.is_active
        )
        for key in api_keys
    ]


@router.delete("/api-keys/{key_id}")
async def delete_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Delete an API key.
    
    Only the owner of the API key can delete it.
    """
    from .models import APIKey
    
    api_key = await APIKey.find_one({
        "key_id": key_id,
        "user_id": str(current_user.id)
    })
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    await api_key.delete()
    
    return {"message": "API key deleted successfully"}


# Admin-only routes
@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
) -> List[UserResponse]:
    """
    List all users (admin only).
    
    Returns paginated list of all users in the system.
    """
    from .models import UserRole
    
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    users = await User.find().skip(skip).limit(limit).to_list()
    
    return [
        UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            status=user.status,
            created_at=user.created_at,
            last_login=user.last_login
        )
        for user in users
    ]


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_admin(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Update any user (admin only).
    
    Allows administrators to update any user's information.
    """
    from .models import UserRole
    
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    service = get_auth_service()
    updated_user = await service.update_user(user_id, user_update, current_user)
    
    return UserResponse(
        id=str(updated_user.id),
        email=updated_user.email,
        username=updated_user.username,
        full_name=updated_user.full_name,
        role=updated_user.role,
        status=updated_user.status,
        created_at=updated_user.created_at,
        last_login=updated_user.last_login
    )


# Rate limit error handler - will be registered in main app


def init_auth_routes(service: AuthService) -> APIRouter:
    """
    Initialize authentication routes with service instance.
    
    Args:
        service: Configured authentication service
        
    Returns:
        Configured router
    """
    global auth_service
    auth_service = service
    return router 