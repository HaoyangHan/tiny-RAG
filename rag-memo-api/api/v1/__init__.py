"""
TinyRAG API v1.4 package.

This module contains the v1.4 API structure with domain-based organization
following the project-based RAG architecture.
"""

from fastapi import APIRouter
from .router import api_router

__all__ = ["api_router"]