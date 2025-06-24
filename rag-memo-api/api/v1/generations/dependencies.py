"""
Dependencies for generation API endpoints.

This module contains dependency injection functions for generation-related
operations following FastAPI dependency injection patterns.
"""

from typing import Annotated
from fastapi import Depends

from .service import ElementGenerationService


def get_generation_service() -> ElementGenerationService:
    """
    Dependency to get ElementGenerationService instance.
    
    Returns:
        ElementGenerationService: Instance of the generation service
    """
    return ElementGenerationService()


# Type alias for dependency injection
GenerationServiceDep = Annotated[ElementGenerationService, Depends(get_generation_service)] 