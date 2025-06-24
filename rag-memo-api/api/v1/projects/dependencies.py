"""
Dependencies for project API endpoints.

This module contains dependency injection functions for project-related
operations following FastAPI dependency injection patterns.
"""

from typing import Annotated
from fastapi import Depends

from .service import ProjectService


def get_project_service() -> ProjectService:
    """
    Dependency to get ProjectService instance.
    
    Returns:
        ProjectService: Instance of the project service
    """
    return ProjectService()


# Type alias for dependency injection
ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)] 