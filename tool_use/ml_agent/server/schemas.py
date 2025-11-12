"""
Pydantic schemas for ML Agent API.

Defines request and response models for tumor classification endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum


class PredictionRequest(BaseModel):
    """Single gene expression sample for prediction"""
    gene_expression: Dict[str, float] = Field(
        ...,
        description="Gene expression values as {gene_name: expression_value}"
    )
    sample_id: Optional[str] = Field(
        None,
        description="Optional sample identifier"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "gene_expression": {
                    "GENE_00001": 5.23,
                    "GENE_00002": 3.45,
                    "GENE_00003": 7.89,
                    # ... more genes
                },
                "sample_id": "SAMPLE_001"
            }
        }


class PredictionResponse(BaseModel):
    """Prediction result for a single sample"""
    predicted_cancer_type: str = Field(..., description="Predicted cancer type")
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence (0-1)")
    probabilities: Dict[str, float] = Field(..., description="Probability for each cancer type")
    sample_id: Optional[str] = Field(None, description="Sample identifier if provided")
    top_biomarkers: List[Dict[str, float]] = Field(
        ...,
        description="Top genes contributing to prediction"
    )


class BatchPredictionRequest(BaseModel):
    """Multiple samples for batch prediction"""
    samples: List[PredictionRequest] = Field(..., description="List of samples to predict")


class BatchPredictionResponse(BaseModel):
    """Batch prediction results"""
    predictions: List[PredictionResponse]
    total_processed: int
    success_count: int
    error_count: int


class ModelInfo(BaseModel):
    """Model metadata and information"""
    model_type: str
    version: str
    n_features: int
    n_classes: int
    class_names: List[str]
    accuracy: float
    cv_accuracy: float


class HealthStatus(BaseModel):
    """API health status"""
    status: str
    model_loaded: bool
    model_version: Optional[str]
    available_endpoints: List[str]
