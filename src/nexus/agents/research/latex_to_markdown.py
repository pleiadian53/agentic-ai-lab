"""
Convert LaTeX reports to GitHub-friendly Markdown.

This module converts LaTeX source to Markdown while preserving:
- Section structure
- Equations (using GitHub's LaTeX support: $...$)
- Emphasis and formatting
- Lists and itemize/enumerate
"""

import re
from typing import Optional


def latex_to_markdown(latex_content: str, preserve_equations: bool = True) -> str:
    """
    Convert LaTeX document to GitHub-friendly Markdown.
    
    Args:
        latex_content: Full LaTeX document source
        preserve_equations: If True, keep LaTeX equations (GitHub supports them)
        
    Returns:
        Markdown version of the document
    """
    
    # Extract title, author, date from preamble
    title = _extract_latex_command(latex_content, r'\\title\{([^}]+)\}')
    author = _extract_latex_command(latex_content, r'\\author\{([^}]+)\}')
    
    # Extract document body (between \begin{document} and \end{document})
    body_match = re.search(r'\\begin\{document\}(.*?)\\end\{document\}', latex_content, re.DOTALL)
    if not body_match:
        # If no document environment, use the whole content
        content = latex_content
    else:
        content = body_match.group(1)
    
    # Remove \maketitle and \tableofcontents
    content = re.sub(r'\\maketitle', '', content)
    content = re.sub(r'\\tableofcontents', '', content)
    
    # Build markdown document
    md_lines = []
    
    # Add title and metadata
    if title:
        # Clean up title (remove line breaks)
        title = title.replace('\\\\', ' ').strip()
        md_lines.append(f"# {title}\n")
        if author:
            md_lines.append(f"**{author}**\n")
        md_lines.append("---\n")
    
    # Convert sections
    content = _convert_sections(content)
    
    # Convert emphasis
    content = _convert_emphasis(content)
    
    # Convert lists
    content = _convert_lists(content)
    
    # Convert equations
    if preserve_equations:
        content = _convert_equations(content)
    else:
        content = _remove_equations(content)
    
    # Convert citations and references
    content = _convert_citations(content)
    
    # Clean up LaTeX commands
    content = _cleanup_latex_commands(content)
    
    # Clean up whitespace
    content = _cleanup_whitespace(content)
    
    md_lines.append(content)
    
    return '\n'.join(md_lines)


def _extract_latex_command(text: str, pattern: str) -> Optional[str]:
    """Extract content from a LaTeX command."""
    match = re.search(pattern, text)
    return match.group(1) if match else None


def _convert_sections(content: str) -> str:
    """Convert LaTeX sections to Markdown headers."""
    # \section{Title} → ## Title
    content = re.sub(r'\\section\{([^}]+)\}', r'## \1', content)
    # \subsection{Title} → ### Title
    content = re.sub(r'\\subsection\{([^}]+)\}', r'### \1', content)
    # \subsubsection{Title} → #### Title
    content = re.sub(r'\\subsubsection\{([^}]+)\}', r'#### \1', content)
    # \paragraph{Title} → **Title**
    content = re.sub(r'\\paragraph\{([^}]+)\}', r'**\1**', content)
    
    return content


def _convert_emphasis(content: str) -> str:
    """Convert LaTeX emphasis to Markdown."""
    # \textbf{text} → **text**
    content = re.sub(r'\\textbf\{([^}]+)\}', r'**\1**', content)
    # \textit{text} → *text*
    content = re.sub(r'\\textit\{([^}]+)\}', r'*\1*', content)
    # \emph{text} → *text*
    content = re.sub(r'\\emph\{([^}]+)\}', r'*\1*', content)
    # \texttt{text} → `text`
    content = re.sub(r'\\texttt\{([^}]+)\}', r'`\1`', content)
    
    return content


def _convert_lists(content: str) -> str:
    """Convert LaTeX lists to Markdown."""
    # Convert itemize (bullet lists)
    # \begin{itemize} ... \end{itemize}
    def replace_itemize(match):
        items = match.group(1)
        # Convert \item to -
        items = re.sub(r'\\item\s+', '- ', items)
        return items
    
    content = re.sub(r'\\begin\{itemize\}(.*?)\\end\{itemize\}', replace_itemize, content, flags=re.DOTALL)
    
    # Convert enumerate (numbered lists)
    def replace_enumerate(match):
        items = match.group(1)
        # Convert \item to numbered list
        item_count = 1
        def number_item(m):
            nonlocal item_count
            result = f"{item_count}. "
            item_count += 1
            return result
        items = re.sub(r'\\item\s+', number_item, items)
        return items
    
    content = re.sub(r'\\begin\{enumerate\}(.*?)\\end\{enumerate\}', replace_enumerate, content, flags=re.DOTALL)
    
    return content


def _convert_equations(content: str) -> str:
    """Convert LaTeX equations to GitHub-compatible format."""
    # Display equations: \[ ... \] → $$...$$
    content = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', content, flags=re.DOTALL)
    
    # Display equations: \begin{equation} ... \end{equation} → $$...$$
    content = re.sub(r'\\begin\{equation\}(.*?)\\end\{equation\}', r'$$\1$$', content, flags=re.DOTALL)
    
    # Display equations: \begin{align} ... \end{align} → $$...$$
    content = re.sub(r'\\begin\{align\}(.*?)\\end\{align\}', r'$$\1$$', content, flags=re.DOTALL)
    
    # Display equations: $$ ... $$ (already correct)
    # Inline equations: $ ... $ (already correct)
    
    return content


def _remove_equations(content: str) -> str:
    """Remove equations and replace with placeholder."""
    # Remove display equations
    content = re.sub(r'\\\[.*?\\\]', '[equation]', content, flags=re.DOTALL)
    content = re.sub(r'\\begin\{equation\}.*?\\end\{equation\}', '[equation]', content, flags=re.DOTALL)
    content = re.sub(r'\\begin\{align\}.*?\\end\{align\}', '[equation]', content, flags=re.DOTALL)
    content = re.sub(r'\$\$.*?\$\$', '[equation]', content, flags=re.DOTALL)
    
    # Remove inline equations
    content = re.sub(r'\$[^$]+\$', '[eq]', content)
    
    return content


def _convert_citations(content: str) -> str:
    """Convert LaTeX citations to plain text."""
    # \cite{ref} → [ref]
    content = re.sub(r'\\cite\{([^}]+)\}', r'[\1]', content)
    # \citep{ref} → [ref]
    content = re.sub(r'\\citep\{([^}]+)\}', r'[\1]', content)
    # \citet{ref} → [ref]
    content = re.sub(r'\\citet\{([^}]+)\}', r'[\1]', content)
    
    return content


def _cleanup_latex_commands(content: str) -> str:
    """Remove or convert remaining LaTeX commands."""
    # Remove \label{...}
    content = re.sub(r'\\label\{[^}]+\}', '', content)
    
    # Remove \ref{...} and \eqref{...}
    content = re.sub(r'\\ref\{([^}]+)\}', r'\1', content)
    content = re.sub(r'\\eqref\{([^}]+)\}', r'(\1)', content)
    
    # Convert ~ (non-breaking space) to regular space
    content = content.replace('~', ' ')
    
    # Convert LaTeX dashes
    content = content.replace('---', '—')  # em dash
    content = content.replace('--', '–')   # en dash
    
    # Convert LaTeX quotes
    content = content.replace('``', '"')
    content = content.replace("''", '"')
    content = content.replace('`', "'")
    
    # Remove remaining backslash commands (simple ones)
    content = re.sub(r'\\[a-zA-Z]+\s*', '', content)
    
    return content


def _cleanup_whitespace(content: str) -> str:
    """Clean up excessive whitespace."""
    # Remove multiple blank lines
    content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
    
    # Remove trailing whitespace
    lines = [line.rstrip() for line in content.split('\n')]
    content = '\n'.join(lines)
    
    return content.strip()


def generate_markdown_preview(latex_content: str, output_path: str) -> bool:
    """
    Generate a Markdown preview from LaTeX content.
    
    Args:
        latex_content: Full LaTeX document source
        output_path: Path to save Markdown file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        markdown = latex_to_markdown(latex_content, preserve_equations=True)
        
        # Add header note
        header = """> **Note**: This is a GitHub-friendly Markdown preview. 
> For the full report with properly rendered equations, see the [PDF version](report_*.pdf).

---

"""
        markdown = header + markdown
        
        with open(output_path, 'w') as f:
            f.write(markdown)
        
        return True
    except Exception as e:
        print(f"Error generating Markdown preview: {e}")
        return False
