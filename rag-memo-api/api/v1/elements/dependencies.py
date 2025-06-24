"""
Dependencies for element API endpoints.

This module contains dependency injection functions for element-related
operations following FastAPI dependency injection patterns.
"""

from typing import Annotated
from fastapi import Depends

from .service import ElementService


def get_element_service() -> ElementService:
    """
    Dependency to get ElementService instance.
    
    Returns:
        ElementService: Instance of the element service
    """
    return ElementService()


# Type alias for dependency injection
ElementServiceDep = Annotated[ElementService, Depends(get_element_service)] 