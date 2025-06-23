"""
Authentication models for TinyRAG API.

This module contains Pydantic models for user authentication, authorization,
and session management following security best practices.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
from beanie import Document


class UserRole(str, Enum):
    """User role enumeration for role-based access control."""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class UserStatus(str, Enum):
    """User account status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class User(Document):
    """
    User document model for MongoDB storage.
    
    Attributes:
        email: Unique user email address
        username: Unique username for display
        hashed_password: Bcrypt hashed password
        full_name: User's full name
        role: User role for RBAC
        status: Account status
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        last_login: Last login timestamp
        metadata: Additional user metadata
    """
    
    email: EmailStr = Field(..., description="User email address", unique=True)
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    hashed_password: str = Field(..., description="Bcrypt hashed password")
    full_name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    role: UserRole = Field(default=UserRole.USER, description="User role for RBAC")
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="Account status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Account creation time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional user metadata")

    @validator('username')
    def validate_username(cls, v: str) -> str:
        """Validate username format and characters."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must contain only alphanumeric characters, hyphens, and underscores')
        return v.lower()

    @validator('updated_at', pre=True, always=True)
    def set_updated_at(cls, v: datetime) -> datetime:
        """Auto-update the updated_at timestamp."""
        return datetime.utcnow()

    class Settings:
        name = "users"
        # Indexes are created by mongo-init.js to avoid conflicts
        # indexes = [
        #     [("email", 1), {"unique": True, "name": "users_email_unique"}],
        #     [("username", 1), {"unique": True, "name": "users_username_unique"}],
        #     "role",
        #     "status",
        #     "created_at"
        # ]


class UserCreate(BaseModel):
    """
    User creation request model.
    
    Used for user registration endpoints.
    """
    
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Desired username")
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    full_name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    
    @validator('password')
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v


class UserUpdate(BaseModel):
    """
    User update request model.
    
    Used for profile updates and admin user management.
    """
    
    email: Optional[EmailStr] = Field(None, description="New email address")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="New username")
    full_name: Optional[str] = Field(None, min_length=1, max_length=100, description="New full name")
    role: Optional[UserRole] = Field(None, description="New user role (admin only)")
    status: Optional[UserStatus] = Field(None, description="New account status (admin only)")


class UserResponse(BaseModel):
    """
    User response model for API endpoints.
    
    Excludes sensitive information like passwords.
    """
    
    id: str = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., description="Username")
    full_name: str = Field(..., description="User's full name")
    role: UserRole = Field(..., description="User role")
    status: UserStatus = Field(..., description="Account status")
    created_at: datetime = Field(..., description="Account creation time")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")


class Token(BaseModel):
    """
    JWT token response model.
    
    Contains access token and metadata.
    """
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user_id: str = Field(..., description="User ID associated with token")
    role: UserRole = Field(..., description="User role for authorization")


class TokenData(BaseModel):
    """
    Token payload data model.
    
    Contains claims stored in JWT token.
    """
    
    user_id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="User email")
    role: UserRole = Field(..., description="User role")
    exp: datetime = Field(..., description="Token expiration time")
    iat: datetime = Field(..., description="Token issued at time")


class LoginRequest(BaseModel):
    """
    User login request model.
    
    Supports login with either email or username.
    """
    
    identifier: str = Field(..., description="Email or username")
    password: str = Field(..., description="User password")
    remember_me: bool = Field(default=False, description="Extended session flag")


class PasswordReset(BaseModel):
    """
    Password reset request model.
    
    Used for password reset functionality.
    """
    
    email: EmailStr = Field(..., description="User email address")


class PasswordResetConfirm(BaseModel):
    """
    Password reset confirmation model.
    
    Used to confirm password reset with token.
    """
    
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")
    
    @validator('new_password')
    def validate_password(cls, v: str) -> str:
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v


class APIKey(Document):
    """
    API key document model for API access.
    
    Supports different access levels and usage tracking.
    """
    
    key_id: str = Field(..., description="Unique key identifier")
    user_id: str = Field(..., description="Owner user ID")
    name: str = Field(..., description="Human-readable key name")
    hashed_key: str = Field(..., description="Hashed API key")
    permissions: List[str] = Field(default_factory=list, description="API permissions")
    usage_count: int = Field(default=0, description="Usage counter")
    usage_limit: Optional[int] = Field(None, description="Usage limit per month")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Key expiration time")
    last_used: Optional[datetime] = Field(None, description="Last usage timestamp")
    is_active: bool = Field(default=True, description="Key status")
    
    class Settings:
        name = "api_keys"
        indexes = [
            "key_id",
            "user_id",
            "created_at",
            "expires_at",
            "is_active"
        ]


class APIKeyCreate(BaseModel):
    """API key creation request model."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Key name")
    permissions: List[str] = Field(default_factory=list, description="API permissions")
    usage_limit: Optional[int] = Field(None, gt=0, description="Monthly usage limit")
    expires_in_days: Optional[int] = Field(None, gt=0, le=365, description="Expiration in days")


class APIKeyResponse(BaseModel):
    """API key response model."""
    
    key_id: str = Field(..., description="Key identifier")
    name: str = Field(..., description="Key name")
    permissions: List[str] = Field(..., description="API permissions")
    usage_count: int = Field(..., description="Current usage count")
    usage_limit: Optional[int] = Field(..., description="Usage limit")
    created_at: datetime = Field(..., description="Creation time")
    expires_at: Optional[datetime] = Field(..., description="Expiration time")
    last_used: Optional[datetime] = Field(..., description="Last usage")
    is_active: bool = Field(..., description="Key status") 