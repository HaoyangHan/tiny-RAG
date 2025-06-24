"""
Authentication service for TinyRAG API.

This module provides comprehensive authentication and authorization services
including JWT token management, password hashing, and user management.
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import ValidationError

from .models import (
    User, UserCreate, UserUpdate, UserResponse, UserRole, UserStatus,
    Token, TokenData, LoginRequest, APIKey, APIKeyCreate
)

# Global auth service instance - initialized in main.py
_auth_service: Optional['AuthService'] = None

def set_auth_service(auth_service: 'AuthService'):
    """Set the global auth service instance."""
    global _auth_service
    _auth_service = auth_service

def get_auth_service() -> 'AuthService':
    """Get the global auth service instance."""
    if _auth_service is None:
        raise RuntimeError("Auth service not initialized")
    return _auth_service

class AuthService:
    """
    Authentication service providing JWT and password management.
    
    This service handles user authentication, password hashing, JWT token
    generation and validation, and API key management.
    """
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = 30
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.security = HTTPBearer()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        return self.pwd_context.hash(password)
    
    async def authenticate_user(self, identifier: str, password: str) -> Optional[User]:
        """Authenticate user with email/username and password."""
        user = await User.find_one({
            "$or": [
                {"email": identifier.lower()},
                {"username": identifier.lower()}
            ],
            "status": UserStatus.ACTIVE
        })
        
        if not user or not self.verify_password(password, user.hashed_password):
            return None
            
        user.last_login = datetime.utcnow()
        await user.save()
        return user
    
    def create_access_token(self, user: User, remember_me: bool = False) -> Token:
        """Create JWT access token for user."""
        expires_delta = timedelta(
            hours=168 if remember_me else 0,
            minutes=0 if remember_me else self.access_token_expire_minutes
        )
        
        expire = datetime.utcnow() + expires_delta
        
        to_encode = {
            "user_id": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        return Token(
            access_token=encoded_jwt,
            token_type="bearer",
            expires_in=int(expires_delta.total_seconds()),
            user_id=str(user.id),
            role=user.role
        )
    
    async def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            user_id = payload.get("user_id")
            username = payload.get("username")
            email = payload.get("email")
            role = payload.get("role")
            exp = payload.get("exp")
            iat = payload.get("iat")
            
            if not all([user_id, username, email, role]):
                return None
            
            if datetime.utcnow() > datetime.fromtimestamp(exp):
                return None
            
            return TokenData(
                user_id=user_id,
                username=username,
                email=email,
                role=UserRole(role),
                exp=datetime.fromtimestamp(exp),
                iat=datetime.fromtimestamp(iat)
            )
            
        except (JWTError, ValueError):
            return None
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials) -> User:
        """Get current user from JWT token."""
        token_data = await self.verify_token(credentials.credentials)
        
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = await User.get(token_data.user_id)
        
        if not user or user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create new user account."""
        existing_user = await User.find_one({
            "$or": [
                {"email": user_data.email.lower()},
                {"username": user_data.username.lower()}
            ]
        })
        
        if existing_user:
            if existing_user.email == user_data.email.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email address already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        user = User(
            email=user_data.email.lower(),
            username=user_data.username.lower(),
            hashed_password=self.get_password_hash(user_data.password),
            full_name=user_data.full_name,
            role=UserRole.USER,
            status=UserStatus.ACTIVE
        )
        
        await user.save()
        return user
    
    async def update_user(
        self, 
        user_id: str, 
        user_data: UserUpdate, 
        current_user: User
    ) -> User:
        """
        Update user account.
        
        Args:
            user_id: Target user ID
            user_data: Update data
            current_user: Current authenticated user
            
        Returns:
            Updated user object
            
        Raises:
            HTTPException: If unauthorized or user not found
        """
        user = await User.get(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check permissions
        if current_user.role != UserRole.ADMIN and str(current_user.id) != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this user"
            )
        
        # Update fields
        update_data = user_data.dict(exclude_unset=True)
        
        # Only admins can change role and status
        if current_user.role != UserRole.ADMIN:
            update_data.pop("role", None)
            update_data.pop("status", None)
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        await user.save()
        
        return user
    
    def generate_api_key(self) -> str:
        """
        Generate a secure API key.
        
        Returns:
            Secure random API key string
        """
        return secrets.token_urlsafe(32)
    
    def hash_api_key(self, api_key: str) -> str:
        """
        Hash API key for secure storage.
        
        Args:
            api_key: Plain API key
            
        Returns:
            Hashed API key
        """
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    async def create_api_key(
        self, 
        user: User, 
        key_data: APIKeyCreate
    ) -> tuple[APIKey, str]:
        """
        Create new API key for user.
        
        Args:
            user: User object
            key_data: API key creation data
            
        Returns:
            Tuple of (APIKey object, plain key string)
        """
        # Generate key
        api_key = self.generate_api_key()
        key_id = secrets.token_urlsafe(16)
        
        # Calculate expiration
        expires_at = None
        if key_data.expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=key_data.expires_in_days)
        
        # Create API key document
        api_key_doc = APIKey(
            key_id=key_id,
            user_id=str(user.id),
            name=key_data.name,
            hashed_key=self.hash_api_key(api_key),
            permissions=key_data.permissions,
            usage_limit=key_data.usage_limit,
            expires_at=expires_at
        )
        
        await api_key_doc.save()
        
        return api_key_doc, api_key
    
    async def verify_api_key(self, api_key: str) -> Optional[APIKey]:
        """
        Verify API key and return associated key object.
        
        Args:
            api_key: Plain API key string
            
        Returns:
            APIKey object if valid, None otherwise
        """
        hashed_key = self.hash_api_key(api_key)
        
        key_doc = await APIKey.find_one({
            "hashed_key": hashed_key,
            "is_active": True
        })
        
        if not key_doc:
            return None
        
        # Check expiration
        if key_doc.expires_at and datetime.utcnow() > key_doc.expires_at:
            return None
        
        # Check usage limit
        if key_doc.usage_limit and key_doc.usage_count >= key_doc.usage_limit:
            return None
        
        # Update usage
        key_doc.usage_count += 1
        key_doc.last_used = datetime.utcnow()
        await key_doc.save()
        
        return key_doc
    
    def require_role(self, required_role: UserRole):
        """
        Decorator factory for role-based access control.
        
        Args:
            required_role: Minimum required role
            
        Returns:
            Decorator function
        """
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # Get current user from kwargs
                current_user = kwargs.get('current_user')
                
                if not current_user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
                
                # Check role hierarchy
                role_hierarchy = {
                    UserRole.VIEWER: 0,
                    UserRole.USER: 1,
                    UserRole.ADMIN: 2
                }
                
                user_level = role_hierarchy.get(current_user.role, 0)
                required_level = role_hierarchy.get(required_role, 0)
                
                if user_level < required_level:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Insufficient permissions"
                    )
                
                return await func(*args, **kwargs)
            
            return wrapper
        return decorator 

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> User:
    """FastAPI dependency to get current authenticated user."""
    auth_service = get_auth_service()
    return await auth_service.get_current_user(credentials)

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """FastAPI dependency to get current active user."""
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def create_user(user_data: UserCreate) -> User:
    """Create new user account."""
    auth_service = get_auth_service()
    return await auth_service.create_user(user_data)

async def authenticate_user(identifier: str, password: str) -> Optional[User]:
    """Authenticate user with email/username and password."""
    auth_service = get_auth_service()
    return await auth_service.authenticate_user(identifier, password)

async def create_access_token(user: User, remember_me: bool = False) -> Token:
    """Create JWT access token for user."""
    auth_service = get_auth_service()
    return auth_service.create_access_token(user, remember_me) 