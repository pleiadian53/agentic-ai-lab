"""
ML tools for LLM integration.

These functions wrap the ML API endpoints and can be called by the LLM
to perform tumor classification tasks.
"""

import requests
import json
from typing import Dict, List, Optional
import os
from config import ML_SERVER_URL

# Get base URL from environment or config
BASE_URL = os.getenv("ML_SERVER_API_URL", ML_SERVER_URL)


def predict_tumor_type(gene_expression: Dict[str, float], sample_id: Optional[str] = None) -> dict:
    """
    Predict cancer type from gene expression data.
    
    Args:
        gene_expression: Dictionary of gene names to expression values.
                        Example: {"GENE_00001": 5.23, "GENE_00002": 3.45, ...}
        sample_id: Optional identifier for the sample
    
    Returns:
        dict: Prediction results including:
            - predicted_cancer_type: The predicted cancer type
            - confidence: Confidence score (0-1)
            - probabilities: Probability for each cancer type
            - top_biomarkers: Top genes contributing to prediction
    
    Example:
        >>> expression = {"GENE_00001": 5.23, "GENE_00002": 3.45}
        >>> result = predict_tumor_type(expression, sample_id="SAMPLE_001")
        >>> print(result['predicted_cancer_type'])
        'BRCA'
    """
    payload = {
        "gene_expression": gene_expression,
        "sample_id": sample_id
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": f"Prediction failed with status {response.status_code}",
            "detail": response.text
        }


def predict_batch(samples: List[Dict]) -> dict:
    """
    Predict cancer types for multiple samples.
    
    Args:
        samples: List of sample dictionaries, each containing:
                - gene_expression: Dict of gene expression values
                - sample_id: Optional sample identifier
    
    Returns:
        dict: Batch prediction results including:
            - predictions: List of prediction results
            - total_processed: Number of samples processed
            - success_count: Number of successful predictions
            - error_count: Number of failed predictions
    
    Example:
        >>> samples = [
        ...     {"gene_expression": {...}, "sample_id": "S1"},
        ...     {"gene_expression": {...}, "sample_id": "S2"}
        ... ]
        >>> results = predict_batch(samples)
        >>> print(f"Processed {results['total_processed']} samples")
    """
    payload = {"samples": samples}
    
    response = requests.post(f"{BASE_URL}/predict/batch", json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": f"Batch prediction failed with status {response.status_code}",
            "detail": response.text
        }


def get_model_info() -> dict:
    """
    Get information about the tumor classification model.
    
    Returns:
        dict: Model metadata including:
            - model_type: Type of model (e.g., "XGBoost")
            - version: Model version
            - n_features: Number of genes used
            - n_classes: Number of cancer types
            - class_names: List of cancer types
            - accuracy: Model accuracy on test set
            - cv_accuracy: Cross-validation accuracy
    
    Example:
        >>> info = get_model_info()
        >>> print(f"Model can predict: {info['class_names']}")
        ['BRCA', 'LUAD', 'LUSC', 'PRAD', 'COAD']
    """
    response = requests.get(f"{BASE_URL}/model/info")
    
    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": f"Failed to get model info with status {response.status_code}",
            "detail": response.text
        }


def get_cancer_types() -> dict:
    """
    Get list of cancer types the model can predict.
    
    Returns:
        dict: Contains:
            - cancer_types: List of cancer type codes
            - n_classes: Number of cancer types
    
    Example:
        >>> types = get_cancer_types()
        >>> print(types['cancer_types'])
        ['BRCA', 'LUAD', 'LUSC', 'PRAD', 'COAD']
    """
    response = requests.get(f"{BASE_URL}/model/classes")
    
    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": f"Failed to get cancer types with status {response.status_code}",
            "detail": response.text
        }


def get_required_genes() -> dict:
    """
    Get list of genes required for prediction.
    
    Returns:
        dict: Contains:
            - genes: List of gene names
            - n_genes: Number of genes
    
    Example:
        >>> genes = get_required_genes()
        >>> print(f"Model uses {genes['n_genes']} genes")
        Model uses 1000 genes
    """
    response = requests.get(f"{BASE_URL}/model/features")
    
    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": f"Failed to get genes with status {response.status_code}",
            "detail": response.text
        }


def check_ml_service_health() -> dict:
    """
    Check if the ML service is running and healthy.
    
    Returns:
        dict: Health status including:
            - status: "healthy" or "degraded"
            - model_loaded: Whether model is loaded
            - n_features: Number of features
            - n_classes: Number of classes
    
    Example:
        >>> health = check_ml_service_health()
        >>> if health['model_loaded']:
        ...     print("ML service is ready!")
    """
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "detail": f"HTTP {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"status": "unreachable", "error": str(e)}


# Cancer type descriptions for LLM context
CANCER_TYPE_INFO = {
    "BRCA": {
        "name": "Breast Invasive Carcinoma",
        "description": "The most common type of breast cancer",
        "common_biomarkers": ["ESR1", "PGR", "ERBB2"]
    },
    "LUAD": {
        "name": "Lung Adenocarcinoma",
        "description": "The most common type of lung cancer",
        "common_biomarkers": ["EGFR", "KRAS", "ALK"]
    },
    "LUSC": {
        "name": "Lung Squamous Cell Carcinoma",
        "description": "A type of non-small cell lung cancer",
        "common_biomarkers": ["TP63", "SOX2", "PIK3CA"]
    },
    "PRAD": {
        "name": "Prostate Adenocarcinoma",
        "description": "The most common type of prostate cancer",
        "common_biomarkers": ["AR", "PSA", "TMPRSS2"]
    },
    "COAD": {
        "name": "Colon Adenocarcinoma",
        "description": "The most common type of colon cancer",
        "common_biomarkers": ["APC", "KRAS", "TP53"]
    }
}


def get_cancer_type_description(cancer_type: str) -> dict:
    """
    Get detailed information about a specific cancer type.
    
    Args:
        cancer_type: Cancer type code (e.g., "BRCA", "LUAD")
    
    Returns:
        dict: Cancer type information including name, description, and biomarkers
    
    Example:
        >>> info = get_cancer_type_description("BRCA")
        >>> print(info['name'])
        'Breast Invasive Carcinoma'
    """
    return CANCER_TYPE_INFO.get(
        cancer_type,
        {"name": "Unknown", "description": "No information available", "common_biomarkers": []}
    )
