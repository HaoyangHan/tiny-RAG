"""
Main API router for TinyRAG v1.4.

This module assembles all domain-specific routers into the main API router
following the restructured architecture with proper sub-routes.
"""

from fastapi import APIRouter
from .auth.routes import router as auth_router
from .users.routes import router as users_router
from .projects.routes import router as projects_router
from .documents.routes import router as documents_router
from .elements.routes import router as elements_router
from .generations.routes import router as generations_router
from .evaluations.routes import router as evaluations_router

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include domain-specific routers
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"],
)

api_router.include_router(
    users_router,
    prefix="/users",
    tags=["Users"],
)

api_router.include_router(
    projects_router,
    prefix="/projects",
    tags=["Projects"],
)

api_router.include_router(
    documents_router,
    prefix="/documents",
    tags=["Documents"],
)

api_router.include_router(
    elements_router,
    prefix="/elements",
    tags=["Elements"],
)

api_router.include_router(
    generations_router,
    prefix="/generations",
    tags=["Generations"],
)

api_router.include_router(
    evaluations_router,
    prefix="/evaluations",
    tags=["Evaluations"],
) 