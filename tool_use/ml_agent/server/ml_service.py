"""
FastAPI service for tumor classification predictions.

Serves the trained XGBoost model for TCGA tumor type prediction.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
import logging
import sys
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import MODELS_DIR, CORS_ORIGINS, CORS_ALLOW_CREDENTIALS
from server.schemas import (
    PredictionRequest,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    ModelInfo,
    HealthStatus
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="TCGA Tumor Classification API",
    description="XGBoost-based cancer type prediction from gene expression data",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model storage
MODEL = None
LABEL_ENCODER = None
FEATURE_NAMES = None
CLASS_NAMES = None
MODEL_METADATA = None


class ModelPredictor:
    """Handles model predictions"""
    
    def __init__(self, model, label_encoder, feature_names, class_names):
        self.model = model
        self.label_encoder = label_encoder
        self.feature_names = feature_names
        self.class_names = class_names
    
    def prepare_features(self, gene_expression: Dict[str, float]) -> np.ndarray:
        """
        Convert gene expression dictionary to model input format.
        
        Args:
            gene_expression: Dict of {gene_name: expression_value}
        
        Returns:
            Feature array in correct order
        """
        # Create feature vector in correct order
        features = []
        missing_genes = []
        
        for gene in self.feature_names:
            if gene in gene_expression:
                features.append(gene_expression[gene])
            else:
                # Use 0 for missing genes (or could use mean)
                features.append(0.0)
                missing_genes.append(gene)
        
        if missing_genes:
            logger.warning(f"Missing {len(missing_genes)} genes, using 0 for missing values")
        
        return np.array(features).reshape(1, -1)
    
    def predict(self, request: PredictionRequest) -> PredictionResponse:
        """Make prediction for a single sample"""
        # Prepare features
        X = self.prepare_features(request.gene_expression)
        
        # Get prediction
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        
        # Decode prediction
        predicted_cancer_type = self.label_encoder.inverse_transform([prediction])[0]
        confidence = float(probabilities[prediction])
        
        # Get probabilities for all classes
        prob_dict = {
            class_name: float(prob)
            for class_name, prob in zip(self.class_names, probabilities)
        }
        
        # Get top biomarkers (feature importance for this prediction)
        top_biomarkers = self._get_top_biomarkers(X, n_top=10)
        
        return PredictionResponse(
            predicted_cancer_type=predicted_cancer_type,
            confidence=confidence,
            probabilities=prob_dict,
            sample_id=request.sample_id,
            top_biomarkers=top_biomarkers
        )
    
    def _get_top_biomarkers(self, X: np.ndarray, n_top: int = 10) -> List[Dict[str, float]]:
        """Get top contributing genes for this prediction"""
        if hasattr(self.model, 'feature_importances_'):
            # Get feature importance
            importance = self.model.feature_importances_
            
            # Get expression values
            expression = X[0]
            
            # Combine importance with expression
            gene_scores = []
            for gene, imp, expr in zip(self.feature_names, importance, expression):
                if expr > 0:  # Only include expressed genes
                    score = imp * expr  # Weighted by expression
                    gene_scores.append({'gene': gene, 'score': float(score)})
            
            # Sort by score and return top N
            gene_scores.sort(key=lambda x: x['score'], reverse=True)
            return gene_scores[:n_top]
        else:
            return []


# Event handlers
@app.on_event("startup")
def load_model():
    """Load model on startup"""
    global MODEL, LABEL_ENCODER, FEATURE_NAMES, CLASS_NAMES, MODEL_METADATA
    
    model_path = MODELS_DIR / "tumor_classifier.pkl"
    
    if not model_path.exists():
        logger.warning(f"Model not found at {model_path}")
        logger.warning("Please run train_model.py first!")
        return
    
    try:
        logger.info(f"Loading model from {model_path}")
        model_data = joblib.load(model_path)
        
        MODEL = model_data['model']
        LABEL_ENCODER = model_data['label_encoder']
        FEATURE_NAMES = model_data['feature_names']
        CLASS_NAMES = model_data['class_names']
        MODEL_METADATA = model_data.get('metrics', {})
        
        logger.info(f"Model loaded successfully!")
        logger.info(f"  Version: {model_data.get('version', 'unknown')}")
        logger.info(f"  Classes: {CLASS_NAMES}")
        logger.info(f"  Features: {len(FEATURE_NAMES)}")
        
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise


# API Endpoints
@app.get("/", response_model=HealthStatus)
def root():
    """API health check and info"""
    return HealthStatus(
        status="healthy" if MODEL is not None else "model_not_loaded",
        model_loaded=MODEL is not None,
        model_version="1.0.0" if MODEL is not None else None,
        available_endpoints=[
            "/predict",
            "/predict/batch",
            "/model/info",
            "/model/classes"
        ]
    )


@app.get("/health")
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy" if MODEL is not None else "degraded",
        "model_loaded": MODEL is not None,
        "n_features": len(FEATURE_NAMES) if FEATURE_NAMES else 0,
        "n_classes": len(CLASS_NAMES) if CLASS_NAMES else 0
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """
    Predict cancer type from gene expression data.
    
    Accepts gene expression values and returns predicted cancer type
    with confidence scores and top biomarkers.
    """
    if MODEL is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please ensure model is trained and available."
        )
    
    try:
        predictor = ModelPredictor(MODEL, LABEL_ENCODER, FEATURE_NAMES, CLASS_NAMES)
        prediction = predictor.predict(request)
        
        logger.info(
            f"Prediction: {prediction.predicted_cancer_type} "
            f"(confidence: {prediction.confidence:.3f})"
        )
        
        return prediction
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/batch", response_model=BatchPredictionResponse)
def predict_batch(request: BatchPredictionRequest):
    """
    Predict cancer types for multiple samples.
    
    Useful for processing multiple gene expression profiles at once.
    """
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        predictor = ModelPredictor(MODEL, LABEL_ENCODER, FEATURE_NAMES, CLASS_NAMES)
        
        predictions = []
        errors = 0
        
        for sample in request.samples:
            try:
                pred = predictor.predict(sample)
                predictions.append(pred)
            except Exception as e:
                logger.error(f"Error predicting sample {sample.sample_id}: {e}")
                errors += 1
        
        return BatchPredictionResponse(
            predictions=predictions,
            total_processed=len(request.samples),
            success_count=len(predictions),
            error_count=errors
        )
    
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


@app.get("/model/info", response_model=ModelInfo)
def get_model_info():
    """Get model metadata and performance metrics"""
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    metadata_file = MODELS_DIR / "model_metadata.json"
    
    if metadata_file.exists():
        import json
        with open(metadata_file) as f:
            metadata = json.load(f)
        return ModelInfo(**metadata)
    else:
        # Return basic info
        return ModelInfo(
            model_type="XGBoost",
            version="1.0.0",
            n_features=len(FEATURE_NAMES),
            n_classes=len(CLASS_NAMES),
            class_names=CLASS_NAMES,
            accuracy=0.0,
            cv_accuracy=0.0
        )


@app.get("/model/classes")
def get_classes():
    """Get list of cancer types the model can predict"""
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "cancer_types": CLASS_NAMES,
        "n_classes": len(CLASS_NAMES)
    }


@app.get("/model/features")
def get_features():
    """Get list of genes used by the model"""
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "genes": FEATURE_NAMES,
        "n_genes": len(FEATURE_NAMES)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
