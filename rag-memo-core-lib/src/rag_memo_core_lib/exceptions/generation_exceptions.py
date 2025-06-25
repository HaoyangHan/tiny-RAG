"""Generation Exception Classes"""

from .base import TinyRAGError

class GenerationError(TinyRAGError):
    """Exception raised for generation errors."""
    pass

class TemplateError(GenerationError):
    """Exception raised for template errors."""
    pass

class ContextError(GenerationError):
    """Exception raised for context errors."""
    pass

class WorkflowError(GenerationError):
    """Exception raised for workflow errors."""
    pass 