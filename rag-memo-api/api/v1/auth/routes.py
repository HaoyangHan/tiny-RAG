"""
Authentication routes for TinyRAG v1.4.

This module contains authentication endpoints adapted for the v1.4 API structure,
maintaining compatibility with the existing auth system.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from auth.models import (
    User, UserCreate, UserResponse, LoginRequest, Token,
    PasswordReset, PasswordResetConfirm
)
from auth.service import AuthService

# Global auth service reference (will be set by main app)
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

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency to get current active user."""
    if current_user.status.value != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )
    return current_user

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account"
)
async def register(user_data: UserCreate) -> UserResponse:
    """Register a new user."""
    try:
        service = get_auth_service()
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
        # Re-raise HTTPExceptions (like duplicate user errors) as-is
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account"
        )


@router.post(
    "/login",
    response_model=Token,
    summary="Login user",
    description="Authenticate user and return access token"
)
async def login(login_data: LoginRequest) -> Token:
    """Authenticate user and return access token."""
    try:
        service = get_auth_service()
        user = await service.authenticate_user(
            identifier=login_data.identifier,
            password=login_data.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email/username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = service.create_access_token(
            user=user,
            remember_me=login_data.remember_me
        )
        
        return token
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get current authenticated user information"
)
async def get_me(current_user: User = Depends(get_current_active_user)) -> UserResponse:
    """Get current user information."""
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


@router.post(
    "/password-reset",
    summary="Request password reset",
    description="Request a password reset token"
)
async def request_password_reset(request: PasswordReset):
    """Request password reset."""
    # TODO: Implement password reset functionality
    # This would typically send an email with a reset token
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Password reset functionality not implemented yet"
    )


@router.post(
    "/password-reset/confirm",
    summary="Confirm password reset",
    description="Reset password with token"
)
async def confirm_password_reset(request: PasswordResetConfirm):
    """Confirm password reset with token."""
    # TODO: Implement password reset confirmation
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Password reset confirmation not implemented yet"
    )


@router.post(
    "/logout",
    summary="Logout user",
    description="Logout current user (invalidate token)"
)
async def logout(current_user: User = Depends(get_current_user)):
    """Logout current user."""
    # TODO: Implement token blacklisting for logout
    # For now, just return success (client should discard token)
    return {"message": "Successfully logged out"}


@router.get(
    "/verify-token",
    response_model=UserResponse,
    summary="Verify token",
    description="Verify if the current token is valid and return user info"
)
async def verify_token(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Verify token validity and return user information."""
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


def set_auth_service(service: AuthService) -> None:
    """Set the authentication service instance."""
    global auth_service
    auth_service = service