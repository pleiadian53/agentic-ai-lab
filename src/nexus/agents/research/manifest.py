"""
Manifest system for tracking research report generation metadata.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional


class ReportManifest:
    """Manages metadata for research reports."""
    
    MANIFEST_FILENAME = "manifest.json"
    
    def __init__(self, topic_dir: Path):
        """
        Initialize manifest for a topic directory.
        
        Args:
            topic_dir: Path to the topic directory
        """
        self.topic_dir = Path(topic_dir)
        self.manifest_path = self.topic_dir / self.MANIFEST_FILENAME
        self.data = self._load()
    
    def _load(self) -> dict:
        """Load existing manifest or create new one."""
        if self.manifest_path.exists():
            with open(self.manifest_path, 'r') as f:
                return json.load(f)
        else:
            return {
                "topic_directory": self.topic_dir.name,
                "created_at": datetime.now().isoformat(),
                "reports": []
            }
    
    def _save(self):
        """Save manifest to disk."""
        self.topic_dir.mkdir(parents=True, exist_ok=True)
        with open(self.manifest_path, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def add_report(
        self,
        filename: str,
        topic: str,
        model: str,
        report_length: str,
        context: Optional[str] = None,
        source: str = "cli",
        word_count: Optional[int] = None,
        generation_time_seconds: Optional[float] = None,
        plan_steps: Optional[int] = None,
        pdf_filename: Optional[str] = None,
        format_decision: Optional[dict] = None
    ):
        """
        Add a report entry to the manifest.
        
        Args:
            filename: Report filename (e.g., "report_2025-11-21_16-53.md")
            topic: Research topic
            model: Model used (e.g., "openai:gpt-4o")
            report_length: Length tier (brief, standard, comprehensive, technical-paper)
            context: User-provided context/template
            source: Source of generation (cli, web)
            word_count: Number of words in report
            generation_time_seconds: Time taken to generate
            plan_steps: Number of steps in research plan
            pdf_filename: Optional PDF filename if generated
            format_decision: Format decision info (format, reasoning, needs_equations, llm_can_pdf)
        """
        report_entry = {
            "filename": filename,
            "generated_at": datetime.now().isoformat(),
            "topic": topic,
            "model": model,
            "report_length": report_length,
            "context": context,
            "source": source,
            "metadata": {
                "word_count": word_count,
                "generation_time_seconds": generation_time_seconds,
                "plan_steps": plan_steps,
                "pdf_filename": pdf_filename,
                "format_decision": format_decision  # Track format decision
            }
        }
        
        self.data["reports"].append(report_entry)
        self.data["last_updated"] = datetime.now().isoformat()
        self._save()
    
    def get_reports(self) -> list[dict]:
        """Get all report entries."""
        return self.data.get("reports", [])
    
    def get_latest_report(self) -> Optional[dict]:
        """Get the most recent report entry."""
        reports = self.get_reports()
        return reports[-1] if reports else None
    
    def get_report_by_filename(self, filename: str) -> Optional[dict]:
        """Get a specific report entry by filename."""
        for report in self.get_reports():
            if report["filename"] == filename:
                return report
        return None
    
    def get_stats(self) -> dict:
        """Get statistics about reports in this topic."""
        reports = self.get_reports()
        if not reports:
            return {
                "total_reports": 0,
                "sources": {},
                "models": {},
                "lengths": {}
            }
        
        sources = {}
        models = {}
        lengths = {}
        
        for report in reports:
            # Count by source
            source = report.get("source", "unknown")
            sources[source] = sources.get(source, 0) + 1
            
            # Count by model
            model = report.get("model", "unknown")
            models[model] = models.get(model, 0) + 1
            
            # Count by length
            length = report.get("report_length", "unknown")
            lengths[length] = lengths.get(length, 0) + 1
        
        return {
            "total_reports": len(reports),
            "sources": sources,
            "models": models,
            "lengths": lengths,
            "first_report": reports[0]["generated_at"],
            "latest_report": reports[-1]["generated_at"]
        }


def create_manifest_entry(
    topic_dir: Path,
    filename: str,
    topic: str,
    model: str,
    report_length: str,
    context: Optional[str],
    source: str,
    report_content: Optional[str] = None,
    generation_time_seconds: Optional[float] = None,
    plan_steps: Optional[int] = None,
    pdf_filename: Optional[str] = None,
    format_decision: Optional[dict] = None
) -> "ReportManifest":
    """
    Convenience function to create a manifest entry.
    
    Args:
        topic_dir: Path to topic directory
        filename: Report filename
        topic: Research topic
        model: Model used
        report_length: Length tier
        context: User context
        source: Generation source
        report_content: Report content (for word count)
        generation_time_seconds: Generation time
        plan_steps: Number of plan steps
        pdf_filename: Optional PDF filename
        format_decision: Format decision info
        
    Returns:
        ReportManifest instance
    """
    manifest = ReportManifest(topic_dir)
    
    # Calculate word count if content provided
    word_count = None
    if report_content:
        word_count = len(report_content.split())
    
    manifest.add_report(
        filename=filename,
        topic=topic,
        model=model,
        report_length=report_length,
        context=context,
        source=source,
        word_count=word_count,
        generation_time_seconds=generation_time_seconds,
        plan_steps=plan_steps,
        pdf_filename=pdf_filename,
        format_decision=format_decision
    )
    
    return manifest


# Example usage and testing
# NOTE: This code only runs when executing this file directly (python manifest.py)
# In production, manifests are created automatically by run.py (CLI) and research_service.py (web)
if __name__ == "__main__":
    from pathlib import Path
    
    print("Running manifest.py example/test code...")
    print("=" * 60)
    
    # Create a test manifest
    test_dir = Path("output/research_reports/test_topic")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    manifest = ReportManifest(test_dir)
    
    # Add a sample report entry (hardcoded values for demonstration)
    # In production, these values come from actual generation results
    manifest.add_report(
        filename="report_2025-11-21_16-53.md",
        topic="Diffusion models in computational biology",
        model="openai:gpt-4o",
        report_length="standard",
        context="Follow Nature Methods style",
        source="cli",
        word_count=8500,
        generation_time_seconds=320.5,
        plan_steps=15
    )
    
    # Get stats
    stats = manifest.get_stats()
    print("Manifest Stats:")
    print(json.dumps(stats, indent=2))
    
    # Get latest report
    latest = manifest.get_latest_report()
    print("\nLatest Report:")
    print(json.dumps(latest, indent=2))
