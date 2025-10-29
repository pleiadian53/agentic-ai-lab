"""Configuration for the research agent workflow."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ResearchAgentConfig:
    """Configuration for the reflective essay writing workflow."""
    
    # Model configuration
    draft_model: str = "openai:gpt-4o-mini"
    reflection_model: str = "openai:gpt-4o"
    revision_model: str = "openai:gpt-4o"
    
    # Workflow configuration
    max_iterations: int = 2  # Total iterations (draft + refinements)
    stop_on_convergence: bool = True  # Stop if no significant changes
    
    # Output configuration
    output_dir: Path = Path("./essays")
    essay_basename: str = "essay"
    save_artifacts: bool = True  # Save drafts, feedback, and final essay
    
    # Temperature settings
    draft_temperature: float = 1.0
    reflection_temperature: float = 1.0
    revision_temperature: float = 0.7  # Lower for more controlled edits
    
    def __post_init__(self):
        """Ensure output_dir is a Path object."""
        if not isinstance(self.output_dir, Path):
            self.output_dir = Path(self.output_dir)
