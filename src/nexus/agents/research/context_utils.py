"""
Utilities for generating smart context strings with dynamic date ranges.
"""
from datetime import datetime


def get_smart_date_range(years_back: int = 2) -> str:
    """
    Generate a smart date range for research papers based on current date.
    
    Args:
        years_back: How many years back to include (default: 2)
        
    Returns:
        Date range string like "2024-2025" or "2023-2025"
        
    Examples:
        >>> # If today is Nov 2025
        >>> get_smart_date_range(2)
        '2024-2025'
        >>> get_smart_date_range(3)
        '2023-2025'
    """
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # If we're in Q4 (Oct-Dec), include next year in range
    # since papers are often published with next year's date
    if current_month >= 10:
        end_year = current_year + 1
    else:
        end_year = current_year
    
    start_year = end_year - years_back
    
    if start_year == end_year:
        return str(end_year)
    else:
        return f"{start_year}-{end_year}"


def enhance_context_with_dates(context: str = None, years_back: int = 2) -> str:
    """
    Enhance user-provided context with smart date ranges if not already specified.
    
    Args:
        context: User-provided context string (can be None)
        years_back: How many years back to include (default: 2)
        
    Returns:
        Enhanced context string with date range
        
    Examples:
        >>> enhance_context_with_dates("Focus on clinical applications")
        'Focus on clinical applications. Focus on papers from 2024-2025.'
        
        >>> enhance_context_with_dates("Papers from 2020-2022")
        'Papers from 2020-2022'  # Don't add dates if already specified
    """
    if context is None:
        context = ""
    
    # Check if context already contains year specifications
    # Look for patterns like "2020", "2020-2021", "from 2020", etc.
    has_years = any(str(year) in context for year in range(2015, 2030))
    
    if has_years:
        # User already specified years, don't override
        return context
    
    # Add smart date range
    date_range = get_smart_date_range(years_back)
    date_suffix = f"Focus on papers from {date_range}."
    
    if context.strip():
        # Append to existing context
        return f"{context.strip()} {date_suffix}"
    else:
        # Use as default context
        return date_suffix


def get_current_year() -> int:
    """Get current year for use in prompts and examples."""
    return datetime.now().year


def get_recent_years_list(count: int = 3) -> list[int]:
    """
    Get list of recent years for research.
    
    Args:
        count: Number of recent years to return
        
    Returns:
        List of years, e.g., [2025, 2024, 2023]
    """
    current_year = datetime.now().year
    return [current_year - i for i in range(count)]


def format_date_context(
    start_year: int = None,
    end_year: int = None,
    include_preprints: bool = True,
    include_published: bool = True
) -> str:
    """
    Format a detailed date context string for research queries.
    
    Args:
        start_year: Starting year (if None, uses 2 years back)
        end_year: Ending year (if None, uses current/next year)
        include_preprints: Whether to include preprints
        include_published: Whether to include published papers
        
    Returns:
        Formatted context string
    """
    if end_year is None:
        current_month = datetime.now().month
        current_year = datetime.now().year
        end_year = current_year + 1 if current_month >= 10 else current_year
    
    if start_year is None:
        start_year = end_year - 2
    
    date_range = f"{start_year}-{end_year}" if start_year != end_year else str(end_year)
    
    context_parts = [f"Focus on papers from {date_range}"]
    
    if include_preprints and include_published:
        context_parts.append("Include both preprints and peer-reviewed publications")
    elif include_preprints:
        context_parts.append("Include preprints (arXiv, bioRxiv, medRxiv)")
    elif include_published:
        context_parts.append("Focus on peer-reviewed publications only")
    
    return ". ".join(context_parts) + "."


# Example usage and testing
if __name__ == "__main__":
    print("Smart Date Range Examples:")
    print(f"Default (2 years): {get_smart_date_range()}")
    print(f"3 years back: {get_smart_date_range(3)}")
    print(f"5 years back: {get_smart_date_range(5)}")
    print()
    
    print("Context Enhancement Examples:")
    print(f"No context: '{enhance_context_with_dates()}'")
    print(f"With context: '{enhance_context_with_dates('Focus on clinical applications')}'")
    print(f"Already has years: '{enhance_context_with_dates('Papers from 2020-2022')}'")
    print()
    
    print("Detailed Date Context:")
    print(format_date_context())
    print(format_date_context(start_year=2020, end_year=2023))
    print(format_date_context(include_preprints=False))
