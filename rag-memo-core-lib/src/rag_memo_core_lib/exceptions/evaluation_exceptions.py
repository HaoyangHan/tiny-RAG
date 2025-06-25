"""Evaluation Exception Classes"""

from .base import TinyRAGError

class EvaluationError(TinyRAGError):
    """Exception raised for evaluation errors."""
    pass

class MetricError(EvaluationError):
    """Exception raised for metric calculation errors."""
    pass

class ScoreError(EvaluationError):
    """Exception raised for scoring errors."""
    pass

class ComparisonError(EvaluationError):
    """Exception raised for comparison errors."""
    pass 