"""
Utilities for generating smart, concise topic slugs using LLM.
"""
import re
from pathlib import Path
from typing import Optional
from aisuite import Client


def generate_topic_slug(
    topic: str, 
    max_length: int = 50, 
    use_llm: bool = True,
    output_dir: Optional[Path] = None,
    ensure_unique: bool = False
) -> str:
    """
    Generate a concise, meaningful directory slug from a research topic.
    
    Args:
        topic: Full research topic string
        max_length: Maximum length for the slug
        use_llm: Whether to use LLM for smart slug generation (default: True)
        output_dir: Base output directory to check for collisions (optional)
        ensure_unique: If True and output_dir provided, append number if slug exists
        
    Returns:
        Clean slug suitable for directory name
        
    Examples:
        >>> generate_topic_slug("Recent advancements on active inference and its relation to energy models")
        'active_inference_energy_models'
        
        >>> generate_topic_slug("Diffusion models for protein structure prediction and molecular generation")
        'diffusion_protein_structure'
        
    Note:
        Multiple reports with the same slug will share a directory but have different
        timestamps, so they won't conflict. The manifest tracks all reports in a directory.
    """
    if use_llm:
        try:
            slug = _llm_generate_slug(topic, max_length)
        except Exception as e:
            print(f"⚠️  LLM slug generation failed ({e}), falling back to simple method")
            slug = _simple_slug(topic, max_length)
    else:
        slug = _simple_slug(topic, max_length)
    
    # Check for collisions if requested
    if ensure_unique and output_dir:
        slug = _ensure_unique_slug(slug, output_dir)
    
    return slug


def _ensure_unique_slug(slug: str, output_dir: Path) -> str:
    """
    Ensure slug is unique by appending a number if directory exists.
    
    Args:
        slug: Base slug
        output_dir: Directory to check for existing slugs
        
    Returns:
        Unique slug (may have _2, _3, etc. appended)
    """
    from pathlib import Path
    
    output_dir = Path(output_dir)
    original_slug = slug
    counter = 2
    
    while (output_dir / slug).exists():
        slug = f"{original_slug}_{counter}"
        counter += 1
    
    return slug


def _llm_generate_slug(topic: str, max_length: int) -> str:
    """
    Use LLM to generate a concise, meaningful slug.
    
    The LLM extracts key concepts and creates a readable slug.
    """
    client = Client()
    
    prompt = f"""Generate a concise directory name (slug) for this research topic:
"{topic}"

Requirements:
- Maximum {max_length} characters
- Use underscores to separate words (snake_case)
- Include only the most important 2-4 keywords
- Use lowercase
- No special characters except underscores
- Be descriptive but concise

Examples:
- "Recent advances in CRISPR gene editing" → "crispr_gene_editing"
- "Diffusion models for protein structure prediction" → "diffusion_protein_structure"
- "Active inference and its relation to energy models" → "active_inference_energy_models"

Output ONLY the slug, no explanation or quotes."""

    response = client.chat.completions.create(
        model="openai:gpt-4o-mini",  # Fast and cheap for this task
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3  # Lower temperature for more consistent output
    )
    
    slug = response.choices[0].message.content.strip()
    
    # Clean up the response (remove quotes, extra whitespace, etc.)
    slug = slug.strip('"\'` \n')
    
    # Validate and sanitize
    slug = _sanitize_slug(slug, max_length)
    
    return slug


def _simple_slug(topic: str, max_length: int) -> str:
    """
    Fallback: Simple slug generation without LLM.
    
    Just lowercase, replace spaces with underscores, and truncate.
    """
    slug = topic.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special chars
    slug = re.sub(r'[-\s]+', '_', slug)   # Replace spaces/hyphens with underscores
    slug = slug[:max_length]
    slug = slug.strip('_')
    return slug


def _sanitize_slug(slug: str, max_length: int) -> str:
    """
    Sanitize a slug to ensure it's valid for directory names.
    
    Args:
        slug: Input slug
        max_length: Maximum allowed length
        
    Returns:
        Sanitized slug
    """
    # Lowercase
    slug = slug.lower()
    
    # Remove any characters that aren't alphanumeric or underscore
    slug = re.sub(r'[^a-z0-9_]', '', slug)
    
    # Replace multiple underscores with single
    slug = re.sub(r'_+', '_', slug)
    
    # Truncate to max length
    slug = slug[:max_length]
    
    # Remove leading/trailing underscores
    slug = slug.strip('_')
    
    # Ensure it's not empty
    if not slug:
        slug = "research_topic"
    
    return slug


def extract_key_terms(topic: str, max_terms: int = 4) -> list[str]:
    """
    Extract key terms from a topic using LLM.
    
    Useful for tagging and categorization.
    
    Args:
        topic: Research topic
        max_terms: Maximum number of key terms to extract
        
    Returns:
        List of key terms
    """
    client = Client()
    
    prompt = f"""Extract the {max_terms} most important keywords from this research topic:
"{topic}"

Return ONLY the keywords separated by commas, no explanation.
Example: "machine learning, neural networks, optimization, deep learning"
"""

    response = client.chat.completions.create(
        model="openai:gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    
    terms_str = response.choices[0].message.content.strip()
    terms = [t.strip().lower() for t in terms_str.split(',')]
    
    return terms[:max_terms]


# Testing and examples
if __name__ == "__main__":
    test_topics = [
        "Recent advancements on active inference and its relation to energy models",
        "Diffusion models for protein structure prediction and molecular generation in computational biology",
        "CRISPR-Cas9 gene editing applications in cancer therapy",
        "Quantum computing approaches to drug discovery and molecular simulation",
        "Large language models for scientific literature review and synthesis"
    ]
    
    print("LLM-Generated Slugs:")
    print("=" * 70)
    for topic in test_topics:
        slug = generate_topic_slug(topic, use_llm=True)
        print(f"Topic: {topic}")
        print(f"Slug:  {slug}")
        print(f"Length: {len(slug)} chars")
        print()
    
    print("\nSimple Slugs (fallback):")
    print("=" * 70)
    for topic in test_topics:
        slug = generate_topic_slug(topic, use_llm=False)
        print(f"Topic: {topic}")
        print(f"Slug:  {slug}")
        print(f"Length: {len(slug)} chars")
        print()
