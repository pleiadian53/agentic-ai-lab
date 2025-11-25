"""
Progress tracking for research report generation.

Provides a callback-based system for tracking progress through the research pipeline,
enabling real-time updates via Server-Sent Events (SSE) or other mechanisms.
"""

import time
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum


class ProgressStage(str, Enum):
    """Stages of research report generation."""
    INITIALIZING = "initializing"
    FORMAT_DECISION = "format_decision"
    PLANNING = "planning"
    EXECUTING = "executing"
    GENERATING_SLUG = "generating_slug"
    SAVING = "saving"
    COMPLETE = "complete"
    ERROR = "error"


class AgentType(str, Enum):
    """Types of agents in the pipeline."""
    PLANNER = "planner"
    RESEARCH = "research"
    WRITER = "writer"
    EDITOR = "editor"


@dataclass
class ProgressUpdate:
    """Progress update message."""
    stage: ProgressStage
    message: str
    progress_percent: int  # 0-100
    agent: Optional[AgentType] = None
    step_number: Optional[int] = None
    total_steps: Optional[int] = None
    estimated_time_remaining: Optional[int] = None  # seconds
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {k: v.value if isinstance(v, Enum) else v 
                for k, v in asdict(self).items() if v is not None}


class ProgressTracker:
    """
    Tracks progress through the research pipeline.
    
    Usage:
        tracker = ProgressTracker()
        tracker.set_callback(lambda update: print(update.message))
        
        tracker.update(ProgressStage.PLANNING, "Creating research plan...")
        tracker.update_step(1, 10, AgentType.RESEARCH, "Gathering papers...")
    """
    
    def __init__(self, callback: Optional[Callable[[ProgressUpdate], None]] = None):
        """
        Initialize progress tracker.
        
        Args:
            callback: Optional function to call with progress updates
        """
        self.callback = callback
        self.start_time = time.time()
        self.current_stage = ProgressStage.INITIALIZING
        self.total_steps = 0
        self.completed_steps = 0
        
        # Time estimates (in seconds) for each stage
        self.stage_estimates = {
            ProgressStage.INITIALIZING: 2,
            ProgressStage.FORMAT_DECISION: 5,
            ProgressStage.PLANNING: 15,
            ProgressStage.EXECUTING: 300,  # 5 minutes (most variable)
            ProgressStage.GENERATING_SLUG: 5,
            ProgressStage.SAVING: 2,
        }
        
        # Step time tracking for better estimates
        self.step_times = []
    
    def set_callback(self, callback: Callable[[ProgressUpdate], None]):
        """Set or update the progress callback function."""
        self.callback = callback
    
    def update(
        self,
        stage: ProgressStage,
        message: str,
        progress_percent: Optional[int] = None
    ):
        """
        Send a general progress update.
        
        Args:
            stage: Current stage of processing
            message: Human-readable progress message
            progress_percent: Optional override for progress percentage
        """
        self.current_stage = stage
        
        if progress_percent is None:
            progress_percent = self._calculate_progress()
        
        estimated_time = self._estimate_remaining_time()
        
        update = ProgressUpdate(
            stage=stage,
            message=message,
            progress_percent=progress_percent,
            estimated_time_remaining=estimated_time
        )
        
        if self.callback:
            self.callback(update)
    
    def update_step(
        self,
        step_number: int,
        total_steps: int,
        agent: AgentType,
        message: str
    ):
        """
        Send a step-level progress update during execution.
        
        Args:
            step_number: Current step number (1-indexed)
            total_steps: Total number of steps
            agent: Agent currently executing
            message: Description of current task
        """
        self.total_steps = total_steps
        self.completed_steps = step_number - 1
        
        # Track step timing
        step_start = time.time()
        if self.step_times:
            step_duration = step_start - self.step_times[-1]
            self.step_times.append(step_start)
        else:
            self.step_times.append(step_start)
        
        # Calculate progress within execution stage
        execution_progress = int((step_number / total_steps) * 100)
        # Overall progress: 30% for setup, 60% for execution, 10% for finalization
        overall_progress = 30 + int(execution_progress * 0.6)
        
        estimated_time = self._estimate_remaining_time_from_steps(step_number, total_steps)
        
        update = ProgressUpdate(
            stage=ProgressStage.EXECUTING,
            message=message,
            progress_percent=overall_progress,
            agent=agent,
            step_number=step_number,
            total_steps=total_steps,
            estimated_time_remaining=estimated_time
        )
        
        if self.callback:
            self.callback(update)
    
    def complete(self, message: str = "Report generation complete!"):
        """Mark progress as complete."""
        update = ProgressUpdate(
            stage=ProgressStage.COMPLETE,
            message=message,
            progress_percent=100,
            estimated_time_remaining=0
        )
        
        if self.callback:
            self.callback(update)
    
    def error(self, message: str):
        """Report an error."""
        update = ProgressUpdate(
            stage=ProgressStage.ERROR,
            message=f"Error: {message}",
            progress_percent=0
        )
        
        if self.callback:
            self.callback(update)
    
    def _calculate_progress(self) -> int:
        """Calculate overall progress percentage based on current stage."""
        stage_weights = {
            ProgressStage.INITIALIZING: 5,
            ProgressStage.FORMAT_DECISION: 10,
            ProgressStage.PLANNING: 20,
            ProgressStage.EXECUTING: 60,
            ProgressStage.GENERATING_SLUG: 5,
            ProgressStage.SAVING: 5,
            ProgressStage.COMPLETE: 100,
        }
        
        # Sum up completed stages
        completed = 0
        for stage, weight in stage_weights.items():
            if stage.value < self.current_stage.value:
                completed += weight
            elif stage == self.current_stage:
                # Add partial progress for current stage
                completed += weight // 2
                break
        
        return min(completed, 99)  # Never show 100% until complete
    
    def _estimate_remaining_time(self) -> int:
        """Estimate remaining time in seconds."""
        elapsed = time.time() - self.start_time
        
        # Get estimate for remaining stages
        remaining_time = 0
        current_stage_passed = False
        
        for stage, estimate in self.stage_estimates.items():
            if stage == self.current_stage:
                current_stage_passed = True
                # Add half the current stage time
                remaining_time += estimate // 2
            elif current_stage_passed:
                remaining_time += estimate
        
        return max(remaining_time, 10)  # At least 10 seconds
    
    def _estimate_remaining_time_from_steps(self, current_step: int, total_steps: int) -> int:
        """Estimate remaining time based on step execution times."""
        if len(self.step_times) < 2:
            # Not enough data, use default estimate
            remaining_steps = total_steps - current_step
            return remaining_steps * 30  # Assume 30 seconds per step
        
        # Calculate average step time
        step_durations = []
        for i in range(1, len(self.step_times)):
            step_durations.append(self.step_times[i] - self.step_times[i-1])
        
        avg_step_time = sum(step_durations) / len(step_durations)
        remaining_steps = total_steps - current_step
        
        # Add time for finalization stages
        finalization_time = self.stage_estimates[ProgressStage.GENERATING_SLUG] + \
                           self.stage_estimates[ProgressStage.SAVING]
        
        return int(remaining_steps * avg_step_time + finalization_time)
