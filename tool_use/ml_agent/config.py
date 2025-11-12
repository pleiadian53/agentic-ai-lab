"""
Configuration module for ML Agent.

Centralizes all configuration settings for the TCGA tumor classification system.
"""

from dotenv import load_dotenv
import os
from pathlib import Path

# Path setup
ML_AGENT_DIR = Path(__file__).parent
PROJECT_ROOT = ML_AGENT_DIR.parent.parent

# Load environment variables (project root first, then local override)
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(ML_AGENT_DIR / ".env", override=True)

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEFAULT_MODEL = os.getenv("DEFAULT_LLM_MODEL", "openai:gpt-4o")

# Server Configuration
ML_SERVER_HOST = os.getenv("ML_SERVER_HOST", "0.0.0.0")
ML_SERVER_PORT = int(os.getenv("ML_SERVER_PORT", "8002"))
LLM_SERVER_PORT = int(os.getenv("ML_LLM_SERVER_PORT", "8003"))
ML_SERVER_URL = os.getenv("ML_SERVER_API_URL", f"http://localhost:{ML_SERVER_PORT}")

# Data Configuration
DATA_DIR = ML_AGENT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = ML_AGENT_DIR / "models"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
RAW_DATA_DIR.mkdir(exist_ok=True)
PROCESSED_DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# TCGA Configuration
TCGA_CANCER_TYPES = [
    "BRCA",  # Breast Cancer
    "LUAD",  # Lung Adenocarcinoma
    "LUSC",  # Lung Squamous Cell Carcinoma
    "PRAD",  # Prostate Adenocarcinoma
    "COAD",  # Colon Adenocarcinoma
]

# Model Configuration
MODEL_TYPE = os.getenv("MODEL_TYPE", "xgboost")  # xgboost, random_forest, neural_network
N_TOP_GENES = int(os.getenv("N_TOP_GENES", "1000"))  # Top variable genes to use
TEST_SIZE = float(os.getenv("TEST_SIZE", "0.2"))
RANDOM_STATE = int(os.getenv("RANDOM_STATE", "42"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"


def validate_config():
    """Validate required configuration"""
    errors = []
    
    if not OPENAI_API_KEY and not ANTHROPIC_API_KEY:
        errors.append("No LLM API key configured (OPENAI_API_KEY or ANTHROPIC_API_KEY)")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")


def get_config_summary():
    """Get configuration summary"""
    return {
        "ml_server_url": ML_SERVER_URL,
        "ml_server_port": ML_SERVER_PORT,
        "llm_server_port": LLM_SERVER_PORT,
        "default_model": DEFAULT_MODEL,
        "data_dir": str(DATA_DIR),
        "models_dir": str(MODELS_DIR),
        "cancer_types": TCGA_CANCER_TYPES,
        "n_top_genes": N_TOP_GENES,
        "openai_configured": bool(OPENAI_API_KEY),
        "anthropic_configured": bool(ANTHROPIC_API_KEY),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(get_config_summary(), indent=2))
