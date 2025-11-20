from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class ModelType(str, Enum):
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O = "gpt-4o"
    GPT_5 = "gpt-5"
    GPT_5_MINI = "gpt-5-mini"
    GPT_5_CODEX_MINI = "gpt-5.1-codex-mini"

class AnalysisRequest(BaseModel):
    """Request to analyze data and generate a chart plan."""
    dataset_path: str = Field(
        ..., 
        description="Path to the dataset file (csv, tsv, etc.)",
        examples=["data/splice_sites_enhanced.tsv"]
    )
    question: str = Field(
        ..., 
        description="The analysis question or goal (e.g. 'Show distribution of splice sites')",
        examples=["Show the top 20 genes with the most splice sites"]
    )
    context: Optional[str] = Field(
        None, 
        description="Additional domain context or constraints",
        examples=["Focus on standard chromosomes only. Use publication-ready styling."]
    )
    model: ModelType = Field(
        ModelType.GPT_4O_MINI, 
        description="LLM to use for generation"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "dataset_path": "data/splice_sites_enhanced.tsv",
                    "question": "Show the top 20 genes with the most splice sites",
                    "context": "Focus on standard chromosomes only. Use publication-ready styling.",
                    "model": "gpt-4o-mini"
                }
            ]
        }
    }

class PlanResponse(BaseModel):
    """The generated analysis plan (code)."""
    code: str = Field(
        ..., 
        description="Generated Python code for the chart",
        examples=["import matplotlib.pyplot as plt\nimport pandas as pd\n\n# Chart code here..."]
    )
    explanation: str = Field(
        ..., 
        description="Explanation of the approach",
        examples=["Generated bar chart using matplotlib"]
    )
    libraries_used: List[str] = Field(
        default_factory=list, 
        description="List of libraries imported",
        examples=[["matplotlib", "pandas", "seaborn"]]
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "code": "import matplotlib.pyplot as plt\nimport pandas as pd\n\nplt.figure(figsize=(10, 6))\nplt.bar(df['x'], df['y'])\nplt.title('Example Chart')\nplt.show()",
                    "explanation": "Generated bar chart showing data distribution",
                    "libraries_used": ["matplotlib", "pandas"]
                }
            ]
        }
    }

class CritiqueRequest(BaseModel):
    """Request to critique/reflect on generated code."""
    code: str = Field(..., description="The code to critique")
    domain_context: str = Field(..., description="Domain context for the critique")
    model: ModelType = Field(ModelType.GPT_4O_MINI, description="LLM to use for critique")

class CritiqueResponse(BaseModel):
    """Structured critique of the code."""
    quality: str = Field(..., description="Assessment of quality (excellent, good, fair, poor)")
    strengths: List[str] = Field(default_factory=list)
    issues: List[Dict[str, str]] = Field(default_factory=list, description="List of issues with severity")
    needs_refinement: bool = Field(..., description="Whether the code needs improvement")

class ExecutionRequest(BaseModel):
    """Request to execute the chart code."""
    code: str = Field(..., description="Python code to execute")
    dataset_path: str = Field(..., description="Path to the dataset to load")
    output_format: str = Field("pdf", description="Output format (pdf, png)")

class ExecutionResponse(BaseModel):
    """Result of code execution."""
    success: bool
    image_path: Optional[str] = Field(None, description="Path to the generated image file")
    logs: str = Field(..., description="Execution logs (stdout/stderr)")
    error: Optional[str] = Field(None, description="Error message if failed")

class InsightRequest(BaseModel):
    """Request to generate insights/captions for a plot."""
    analysis_title: str
    image_path: str = Field(..., description="Path to the plot image")
    dataset_context: str = Field(..., description="Context about the dataset")
    model: ModelType = Field(ModelType.GPT_5_CODEX_MINI, description="LLM to use for captioning")

class InsightResponse(BaseModel):
    """Generated insight/caption."""
    caption: str
    key_insights: List[str]
