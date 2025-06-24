"""
Evaluation model for TinyRAG v1.4.

This module contains the Evaluation model which implements an LLM-as-a-judge
evaluation framework for quality assessment of generated content.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from beanie import Indexed
from pydantic import Field, validator
from models.base import BaseDocument
from models.enums import EvaluationStatus, TenantType, TaskType


class EvaluationCriteria(BaseDocument):
    """
    Evaluation criteria and scoring definitions.
    
    Defines the criteria, metrics, and scoring methodology
    for content evaluation.
    """
    
    # Criteria definitions
    relevance_weight: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
        description="Weight for relevance scoring"
    )
    accuracy_weight: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
        description="Weight for accuracy scoring"
    )
    completeness_weight: float = Field(
        default=0.20,
        ge=0.0,
        le=1.0,
        description="Weight for completeness scoring"
    )
    clarity_weight: float = Field(
        default=0.20,
        ge=0.0,
        le=1.0,
        description="Weight for clarity scoring"
    )
    coherence_weight: float = Field(
        default=0.10,
        ge=0.0,
        le=1.0,
        description="Weight for coherence scoring"
    )
    
    # Custom criteria
    custom_criteria: Dict[str, float] = Field(
        default_factory=dict,
        description="Custom evaluation criteria with weights"
    )
    
    # Evaluation prompts
    evaluation_prompts: Dict[str, str] = Field(
        default_factory=dict,
        description="Custom prompts for different evaluation aspects"
    )
    
    @validator('relevance_weight', 'accuracy_weight', 'completeness_weight', 'clarity_weight', 'coherence_weight')
    def validate_weights(cls, v: float) -> float:
        """Validate weight values are between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError('Weight must be between 0.0 and 1.0')
        return v


class EvaluationScore(BaseDocument):
    """
    Individual evaluation score for a specific criterion.
    
    Contains detailed scoring information for each
    evaluation dimension.
    """
    
    # Score details
    criterion: str = Field(
        description="Name of the evaluation criterion"
    )
    score: float = Field(
        ge=0.0,
        le=1.0,
        description="Score value between 0 and 1"
    )
    weight: float = Field(
        ge=0.0,
        le=1.0,
        description="Weight of this criterion in overall score"
    )
    weighted_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Score multiplied by weight"
    )
    
    # Explanations
    reasoning: Optional[str] = Field(
        None,
        description="Reasoning behind the score"
    )
    examples: List[str] = Field(
        default_factory=list,
        description="Examples supporting the score"
    )
    
    # Suggestions
    strengths: List[str] = Field(
        default_factory=list,
        description="Identified strengths"
    )
    weaknesses: List[str] = Field(
        default_factory=list,
        description="Identified weaknesses"
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Improvement suggestions"
    )


class EvaluationResult(BaseDocument):
    """
    Complete evaluation result with all scores and analysis.
    
    Contains the comprehensive evaluation output including
    individual scores, overall assessment, and recommendations.
    """
    
    # Overall scoring
    overall_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall weighted score"
    )
    
    # Individual scores
    relevance_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Relevance to query/context score"
    )
    accuracy_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Factual accuracy score"
    )
    completeness_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Completeness of response score"
    )
    clarity_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Clarity and readability score"
    )
    coherence_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Logical coherence score"
    )
    
    # Quality assessment
    hallucination_detected: bool = Field(
        default=False,
        description="Whether hallucinations were detected"
    )
    hallucination_severity: Optional[str] = Field(
        None,
        description="Severity of detected hallucinations"
    )
    
    # Detailed analysis
    detailed_scores: List[EvaluationScore] = Field(
        default_factory=list,
        description="Detailed scores for each criterion"
    )
    
    # Summary
    summary: Optional[str] = Field(
        None,
        description="Overall evaluation summary"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Recommendations for improvement"
    )


class Evaluation(BaseDocument):
    """
    Evaluation model for LLM-as-a-judge quality assessment.
    
    Implements comprehensive evaluation framework for generated content
    using LLM-based evaluation with structured scoring and analysis.
    
    Attributes:
        generation_id: ID of the generation being evaluated
        project_id: ID of the associated project
        user_id: ID of the user who requested evaluation
        tenant_type: Type of tenant for context-aware evaluation
        task_type: Type of task being evaluated
        status: Evaluation processing status
        criteria: Evaluation criteria and weights
        result: Evaluation results and scores
        evaluator_model: LLM model used for evaluation
        evaluation_config: Configuration for evaluation process
        context_data: Additional context for evaluation
    """
    
    # Association IDs
    generation_id: Indexed(str) = Field(
        description="ID of the generation being evaluated"
    )
    project_id: Indexed(str) = Field(
        description="ID of the associated project"
    )
    user_id: Indexed(str) = Field(
        description="ID of the user who requested evaluation"
    )
    
    # Context
    tenant_type: TenantType = Field(
        description="Type of tenant for context-aware evaluation"
    )
    task_type: TaskType = Field(
        description="Type of task being evaluated"
    )
    
    # Evaluation Status
    status: EvaluationStatus = Field(
        default=EvaluationStatus.PENDING,
        description="Current status of the evaluation"
    )
    
    # Evaluation Configuration
    criteria: EvaluationCriteria = Field(
        default_factory=EvaluationCriteria,
        description="Evaluation criteria and weights"
    )
    
    # Results
    result: Optional[EvaluationResult] = Field(
        None,
        description="Evaluation results and scores"
    )
    
    # Evaluation Process
    evaluator_model: Optional[str] = Field(
        None,
        description="LLM model used for evaluation"
    )
    evaluation_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Configuration for evaluation process"
    )
    
    # Context and Input
    original_query: Optional[str] = Field(
        None,
        description="Original query that generated the content"
    )
    generated_content: Optional[str] = Field(
        None,
        description="Content being evaluated"
    )
    context_documents: List[str] = Field(
        default_factory=list,
        description="Documents used for context"
    )
    context_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for evaluation"
    )
    
    # Performance Metrics
    evaluation_time_ms: Optional[int] = Field(
        None,
        description="Time taken for evaluation in milliseconds"
    )
    evaluator_tokens_used: Optional[int] = Field(
        None,
        description="Tokens used by evaluator LLM"
    )
    
    # Error Handling
    error_details: Optional[Dict[str, Any]] = Field(
        None,
        description="Error information if evaluation failed"
    )
    
    @validator('status')
    def validate_status_transition(cls, v: EvaluationStatus, values: Dict[str, Any]) -> EvaluationStatus:
        """Validate status transitions are logical."""
        # Add status transition validation logic here if needed
        return v
    
    def set_completed(self, result: EvaluationResult) -> None:
        """Mark evaluation as completed with results."""
        self.status = EvaluationStatus.COMPLETED
        self.result = result
        self.update_timestamp()
    
    def set_failed(self, error_message: str, error_details: Dict[str, Any] = None) -> None:
        """Mark evaluation as failed with error details."""
        self.status = EvaluationStatus.FAILED
        self.error_details = {
            "error_message": error_message,
            "timestamp": datetime.utcnow().isoformat(),
            **(error_details or {})
        }
        self.update_timestamp()
    
    def update_criteria(self, **criteria_updates) -> None:
        """Update evaluation criteria."""
        for key, value in criteria_updates.items():
            if hasattr(self.criteria, key):
                setattr(self.criteria, key, value)
        self.update_timestamp()
    
    def add_custom_criterion(self, name: str, weight: float, prompt: str = None) -> None:
        """Add a custom evaluation criterion."""
        self.criteria.custom_criteria[name] = weight
        if prompt:
            self.criteria.evaluation_prompts[name] = prompt
        self.update_timestamp()
    
    def get_overall_score(self) -> Optional[float]:
        """Get the overall evaluation score."""
        return self.result.overall_score if self.result else None
    
    def get_score_by_criterion(self, criterion: str) -> Optional[float]:
        """Get score for a specific criterion."""
        if not self.result:
            return None
        
        # Check standard criteria first
        standard_criteria = {
            'relevance': self.result.relevance_score,
            'accuracy': self.result.accuracy_score,
            'completeness': self.result.completeness_score,
            'clarity': self.result.clarity_score,
            'coherence': self.result.coherence_score
        }
        
        if criterion in standard_criteria:
            return standard_criteria[criterion]
        
        # Check detailed scores
        for score in self.result.detailed_scores:
            if score.criterion == criterion:
                return score.score
        
        return None
    
    def has_hallucinations(self) -> bool:
        """Check if hallucinations were detected."""
        return self.result.hallucination_detected if self.result else False
    
    def get_recommendations(self) -> List[str]:
        """Get improvement recommendations."""
        return self.result.recommendations if self.result else []
    
    def is_successful(self) -> bool:
        """Check if evaluation was successful."""
        return self.status == EvaluationStatus.COMPLETED and self.result is not None
    
    def get_evaluation_summary(self) -> Dict[str, Any]:
        """Get a summary of the evaluation results."""
        if not self.result:
            return {"status": "not_completed"}
        
        return {
            "overall_score": self.result.overall_score,
            "individual_scores": {
                "relevance": self.result.relevance_score,
                "accuracy": self.result.accuracy_score,
                "completeness": self.result.completeness_score,
                "clarity": self.result.clarity_score,
                "coherence": self.result.coherence_score
            },
            "hallucination_detected": self.result.hallucination_detected,
            "summary": self.result.summary,
            "recommendations_count": len(self.result.recommendations)
        }
    
    class Settings:
        name = "evaluations"
        indexes = [
            "generation_id",
            "project_id",
            "user_id",
            "tenant_type",
            "task_type",
            "status",
            "evaluator_model",
            "created_at",
            "updated_at",
            "is_deleted"
        ] 