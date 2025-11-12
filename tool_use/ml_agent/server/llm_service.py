"""
LLM service for ML Agent.

Orchestrates ML predictions through natural language using AISuite and tool calling.
The LLM can understand user requests and call appropriate ML tools.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aisuite as ai
import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DEFAULT_MODEL, CORS_ORIGINS, CORS_ALLOW_CREDENTIALS
import ml_tools

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="ML Agent LLM Service",
    description="Natural language interface for tumor classification",
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

# Initialize AISuite client
client = ai.Client()


class PromptRequest(BaseModel):
    """Request model for LLM prompts"""
    prompt: str
    model: str = DEFAULT_MODEL


class PromptResponse(BaseModel):
    """Response model for LLM prompts"""
    response: str
    tool_calls: list = []


def build_system_prompt() -> str:
    """Build system prompt with ML context"""
    return """You are an AI assistant specialized in tumor classification using gene expression data.

You have access to a machine learning model that can predict cancer types from gene expression profiles.

Available Tools:
- predict_tumor_type: Predict cancer type from gene expression data
- predict_batch: Predict cancer types for multiple samples
- get_model_info: Get information about the ML model
- get_cancer_types: Get list of cancer types the model can predict
- get_required_genes: Get list of genes required for prediction
- check_ml_service_health: Check if ML service is running
- get_cancer_type_description: Get detailed info about a cancer type

Cancer Types:
- BRCA: Breast Invasive Carcinoma
- LUAD: Lung Adenocarcinoma
- LUSC: Lung Squamous Cell Carcinoma
- PRAD: Prostate Adenocarcinoma
- COAD: Colon Adenocarcinoma

When users ask about tumor classification:
1. Check if the ML service is healthy first
2. Use the appropriate tools to get predictions
3. Explain the results in clear, medical terms
4. Provide confidence scores and top biomarkers
5. Offer context about the predicted cancer type

Be helpful, accurate, and explain technical results in accessible language."""


@app.get("/")
def root():
    """API health check"""
    return {
        "status": "healthy",
        "service": "ML Agent LLM Service",
        "model": DEFAULT_MODEL,
        "endpoints": {
            "prompt": "/prompt",
            "health": "/health"
        }
    }


@app.get("/health")
def health_check():
    """Check health of LLM service and ML backend"""
    ml_health = ml_tools.check_ml_service_health()
    
    return {
        "llm_service": "healthy",
        "ml_service": ml_health.get("status", "unknown"),
        "ml_model_loaded": ml_health.get("model_loaded", False),
        "default_model": DEFAULT_MODEL
    }


@app.post("/prompt", response_model=PromptResponse)
def process_prompt(request: PromptRequest):
    """
    Process natural language prompt and orchestrate ML tools.
    
    The LLM will understand the request and call appropriate ML tools
    to perform tumor classification tasks.
    """
    try:
        logger.info(f"Processing prompt: {request.prompt[:100]}...")
        
        # Build messages
        system_prompt = build_system_prompt()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.prompt}
        ]
        
        # Call LLM with tools
        response = client.chat.completions.create(
            model=request.model,
            messages=messages,
            tools=[
                ml_tools.predict_tumor_type,
                ml_tools.predict_batch,
                ml_tools.get_model_info,
                ml_tools.get_cancer_types,
                ml_tools.get_required_genes,
                ml_tools.check_ml_service_health,
                ml_tools.get_cancer_type_description
            ],
            tool_choice="auto"
        )
        
        # Extract response
        message = response.choices[0].message
        
        # Check if tools were called
        tool_calls_info = []
        if hasattr(message, 'tool_calls') and message.tool_calls:
            for tool_call in message.tool_calls:
                tool_calls_info.append({
                    "tool": tool_call.function.name,
                    "arguments": tool_call.function.arguments
                })
        
        response_text = message.content or "No response generated"
        
        logger.info(f"Response generated (tools called: {len(tool_calls_info)})")
        
        return PromptResponse(
            response=response_text,
            tool_calls=tool_calls_info
        )
    
    except Exception as e:
        logger.error(f"Error processing prompt: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process prompt: {str(e)}"
        )


@app.post("/predict_with_explanation")
def predict_with_explanation(gene_expression: dict, sample_id: str = None):
    """
    Make a prediction and get LLM explanation.
    
    Combines ML prediction with natural language explanation.
    """
    try:
        # Get prediction
        prediction = ml_tools.predict_tumor_type(gene_expression, sample_id)
        
        if "error" in prediction:
            raise HTTPException(status_code=500, detail=prediction["error"])
        
        # Generate explanation using LLM
        prompt = f"""I have a tumor sample prediction result:

Predicted Cancer Type: {prediction['predicted_cancer_type']}
Confidence: {prediction['confidence']:.2%}

Probabilities for each type:
{chr(10).join(f"- {k}: {v:.2%}" for k, v in prediction['probabilities'].items())}

Top Biomarkers:
{chr(10).join(f"- {b['gene']}: {b['score']:.4f}" for b in prediction['top_biomarkers'][:5])}

Please explain this prediction in clear medical terms, including:
1. What this cancer type is
2. The confidence level and what it means
3. Key biomarkers and their significance
4. Any important clinical considerations"""
        
        explanation_response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": prompt}
            ]
        )
        
        explanation = explanation_response.choices[0].message.content
        
        return {
            "prediction": prediction,
            "explanation": explanation
        }
    
    except Exception as e:
        logger.error(f"Error in predict_with_explanation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
